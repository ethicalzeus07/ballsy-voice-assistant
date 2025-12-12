#!/usr/bin/env python3
"""
Backend application for the full-stack voice assistant with Siri-like UI.
This module provides the core backend functionality including:
- FastAPI server with REST and WebSocket endpoints
- Speech recognition and processing
- AI integration with Gemini
- Command processing and execution
- External service integration
- Auto-clear conversation history on startup
- Serving the frontend (HTML/CSS/JS) via FastAPI
"""


import os
import re
import time
import logging
import datetime
import asyncio
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager


from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel


import speech_recognition as sr
from src.backend.config import config
from src.backend.database import init_database, get_db_session, clear_conversation_history, CommandHistory, Setting, User
from src.backend.ai import generate_reply
from src.backend.tts import synthesize_speech_base64


# ──────────────────────────────────────────────────────────────────────────────
# Setup logging - Cloud Logging friendly format
logging.basicConfig(
   level=getattr(logging, config.LOG_LEVEL),
   format='{"timestamp": "%(asctime)s", "severity": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
   handlers=[
       logging.StreamHandler()
   ]
)
logger = logging.getLogger(__name__)








# Database is initialized via init_database() from database.py module



# FastAPI app with lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
   """Application lifespan manager."""
   # Try to initialize database, but don't fail if it's not ready
   db_ready = init_database(retry=True, max_retries=3, delay=2.0)
   if db_ready:
       logger.info("Database initialized")
       try:
           clear_conversation_history()
       except Exception as e:
           logger.warning(f"Could not clear conversation history: {e}")
   else:
       logger.warning("Database not ready at startup. Will retry on first use.")
   yield
   logger.info("Shutting down Ballsy...")


app = FastAPI(
   title="Ballsy Voice Assistant API",
   description="Backend API for Ballsy - the full-stack voice assistant with Siri-like UI",
   version="1.0.0",
   lifespan=lifespan
)


# Security: Configure CORS
app.add_middleware(
   CORSMiddleware,
   allow_origins=config.CORS_ORIGINS if "*" not in config.CORS_ORIGINS else ["*"],
   allow_credentials=True,
   allow_methods=["GET", "POST", "PUT"],
   allow_headers=["*"],
)

# Security: Add trusted host middleware
app.add_middleware(
   TrustedHostMiddleware,
   allowed_hosts=["*"] if not config.is_production() else config.CORS_ORIGINS
)



# WebSocket connection manager


class ConnectionManager:
   def __init__(self):
       self.active_connections: Dict[int, WebSocket] = {}


   async def connect(self, websocket: WebSocket, client_id: int):
       await websocket.accept()
       self.active_connections[client_id] = websocket


   def disconnect(self, client_id: int):
       if client_id in self.active_connections:
           del self.active_connections[client_id]


   async def send_message(self, client_id: int, message: Dict[str, Any]):
       if client_id in self.active_connections:
           await self.active_connections[client_id].send_json(message)


   async def broadcast(self, message: Dict[str, Any]):
       for ws in list(self.active_connections.values()):
           await ws.send_json(message)


manager = ConnectionManager()



# Pydantic models


class CommandRequest(BaseModel):
   command: str
   user_id: Optional[int] = 1


class CommandResponse(BaseModel):
    response: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    audio_base64: Optional[str] = None  # Base64-encoded audio from Gemini TTS


class SettingsUpdate(BaseModel):
   voice: Optional[str] = None
   voice_speed: Optional[int] = None
   theme: Optional[str] = None



# Speech recognition


class SpeechRecognizer:
   def __init__(self):
       self.recognizer = sr.Recognizer()
       self.recognizer.pause_threshold = 1.5
       self.recognizer.dynamic_energy_threshold = True
       self.recognizer.energy_threshold = 200
       self.recognizer.operation_timeout = None


   def calibrate(self, duration=3):
       """Calibrate microphone for ambient noise."""
       with sr.Microphone() as source:
           logger.info("Calibrating microphone...")
           self.recognizer.adjust_for_ambient_noise(source, duration=duration)
           logger.info(f"Energy threshold set to: {self.recognizer.energy_threshold}")
           if self.recognizer.energy_threshold > 500:
               self.recognizer.energy_threshold = 300
               logger.info(f"Adjusted threshold to: {self.recognizer.energy_threshold}")


   def recognize_from_file(self, audio_file: str) -> str:
       """Recognize speech from an audio file."""
       try:
           with sr.AudioFile(audio_file) as source:
               audio = self.recognizer.record(source)
               text = self.recognizer.recognize_google(audio, language="en-US", show_all=False)
               return text.lower().strip()
       except sr.UnknownValueError:
           logger.warning("Could not understand audio")
           return ""
       except sr.RequestError as e:
           logger.error(f"Speech service error: {e}")
           return ""
       except Exception as e:
           logger.error(f"Recognition error: {e}")
           return ""


speech_recognizer = SpeechRecognizer()



# Command processing with per-session memory


class CommandProcessor:
   def __init__(self):
       # Per-user session memory to support multiple concurrent users
       # Each user gets their own conversation history and state
       self.user_sessions: Dict[str, Dict[str, Any]] = {}
       
       # Security: Rate limiting and session management
       self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))  # Last 10 requests per user
       self.session_timestamps: Dict[str, float] = {}  # Track when sessions were last accessed
       self.max_sessions = config.MAX_SESSIONS
       self.session_timeout = config.SESSION_TIMEOUT
       self.rate_limit_window = config.RATE_LIMIT_WINDOW
       self.max_requests_per_minute = config.MAX_REQUESTS_PER_MINUTE
   
   def _cleanup_expired_sessions(self):
       """Remove expired sessions to prevent memory leaks."""
       current_time = time.time()
       expired_users = []
       
       for user_key, timestamp in self.session_timestamps.items():
           if current_time - timestamp > self.session_timeout:
               expired_users.append(user_key)
       
       for user_key in expired_users:
           del self.user_sessions[user_key]
           del self.session_timestamps[user_key]
           if user_key in self.rate_limits:
               del self.rate_limits[user_key]
       
       if expired_users:
           logger.info(f"Cleaned up {len(expired_users)} expired sessions")
   
   def _check_rate_limit(self, user_id: str) -> bool:
       """Check if user is within rate limits."""
       current_time = time.time()
       user_key = str(user_id)
       
       # Clean old rate limit entries
       while (self.rate_limits[user_key] and 
              current_time - self.rate_limits[user_key][0] > self.rate_limit_window):
           self.rate_limits[user_key].popleft()
       
       # Check if user has exceeded rate limit
       if len(self.rate_limits[user_key]) >= self.max_requests_per_minute:
           logger.warning(f"Rate limit exceeded for user {user_key}")
           return False
       
       # Add current request timestamp
       self.rate_limits[user_key].append(current_time)
       return True
   
   def _get_user_session(self, user_id) -> Dict[str, Any]:
       """Get or create session memory for a specific user with security checks."""
       # Clean up expired sessions first
       self._cleanup_expired_sessions()
       
       # Convert user_id to string to handle both int and string IDs
       user_key = str(user_id)
       
       # Check if we've reached maximum sessions
       if len(self.user_sessions) >= self.max_sessions and user_key not in self.user_sessions:
           logger.warning(f"Maximum sessions reached ({self.max_sessions})")
           # Remove oldest session to make room
           oldest_user = min(self.session_timestamps.keys(), key=lambda k: self.session_timestamps[k])
           del self.user_sessions[oldest_user]
           del self.session_timestamps[oldest_user]
           if oldest_user in self.rate_limits:
               del self.rate_limits[oldest_user]
       
       if user_key not in self.user_sessions:
           self.user_sessions[user_key] = {
               "conversation_history": [],  # List of {"role": "user"/"assistant", "content": "..."}
               "last_result": None,
               "calculations": []
           }
       
       # Update session timestamp
       self.session_timestamps[user_key] = time.time()
       return self.user_sessions[user_key]


   async def process_command(self, cmd: str, user_id = 1) -> CommandResponse:
       """
       Process a voice/text command and return the response.
       At the start, we append the user message into user-specific session_memory.
       At the end, we append Ballsy's response as well.
       """
       # Security: Input validation and sanitization
       if not cmd or not isinstance(cmd, str):
           return CommandResponse(response="Invalid input. Please provide a valid command.")
       
       # Limit command length to prevent abuse
       if len(cmd) > 1000:
           return CommandResponse(response="Command too long. Please keep it under 1000 characters.")
       
       # Basic sanitization - remove potentially dangerous characters
       cmd = cmd.strip()
       if not cmd:
           return CommandResponse(response="I didn't catch that. Could you please repeat?")

       # Security: Check rate limits
       if not self._check_rate_limit(user_id):
           return CommandResponse(response="Too many requests. Please wait a moment before trying again.")

       # Get user-specific session memory
       session_memory = self._get_user_session(user_id)

       # 1) Append the user message to session memory
       session_memory["conversation_history"].append({
           "role": "user",
           "content": cmd
       })


       # 2) Initialize a placeholder for our final response
       response_data: CommandResponse


       try:
           lower_cmd = cmd.lower().strip()


           # Basic greetings
           if lower_cmd in ["hello", "hi", "hey"]:
               response_data = CommandResponse(response="Hi there! I'm Ballsy, your voice assistant. How can I help?")
           # Name questions
           elif any(phrase in lower_cmd for phrase in ["what's your name", "who are you", "what are you called"]):
               response_data = CommandResponse(response="I'm Ballsy, your personal voice assistant!")
           # How are you
           elif any(phrase in lower_cmd for phrase in ["how are you", "how's it going", "what's up"]):
               response_data = CommandResponse(response="I'm doing great! Ready to help you with anything you need!")
           # Exit commands
           elif any(word in lower_cmd for word in ["bye", "goodbye", "exit", "stop", "quit"]):
               response_data = CommandResponse(response="Goodbye! Take care!", action="exit")
           # Who is/What is questions - AI response
           elif any(phrase in lower_cmd for phrase in ["who is", "who's", "what is", "what's", "tell me about"]):
               is_person = any(phrase in lower_cmd for phrase in ["who is", "who's"])
               subject = lower_cmd
               for phrase in ["who is", "who's", "what is", "what's", "tell me about"]:
                   subject = subject.replace(phrase, "").strip()
               if subject:
                   return await self._get_info_or_search(subject, is_person, user_id)
               else:
                   response_data = CommandResponse(response="What would you like to know?")
           # Math expressions
           elif re.match(r"(?:what'?s\s*)?([\d\s\+\-\*\/]+)$", lower_cmd) or re.match(r"^\s*[\+\-\*\/]\s*\d+", lower_cmd):
               math_result = self._handle_math_expression(lower_cmd, user_id)
               if math_result:
                   response_data = math_result
               else:
                   response_data = CommandResponse(response="Sorry, I couldn't compute that.")
           # YouTube search
           elif "on youtube" in lower_cmd:
               match = re.search(r"(?:open|search|play|watch)?\s*(.+?)\s+on\s+youtube", lower_cmd)
               if match:
                   query = match.group(1).strip()
                   url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                   response_data = CommandResponse(
                       response=f"Opening {query} on YouTube",
                       action="open_url",
                       data={"url": url, "description": f"{query} on YouTube"}
                   )
               else:
                   response_data = CommandResponse(response="What would you like to search on YouTube?")
           # Spotify search
           elif "on spotify" in lower_cmd:
               match = re.search(r"(?:open|search|play|listen to)?\s*(.+?)\s+on\s+spotify", lower_cmd)
               if match:
                   query = match.group(1).strip()
                   url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
                   response_data = CommandResponse(
                       response=f"Opening {query} on Spotify",
                       action="open_url",
                       data={"url": url, "description": f"{query} on Spotify"}
                   )
               else:
                   response_data = CommandResponse(response="What would you like to search on Spotify?")
           # Netflix search
           elif "on netflix" in lower_cmd:
               match = re.search(r"(?:open|search|play|watch)?\s*(.+?)\s+on\s+netflix", lower_cmd)
               if match:
                   query = match.group(1).strip()
                   url = f"https://www.netflix.com/search?q={query.replace(' ', '%20')}"
                   response_data = CommandResponse(
                       response=f"Opening {query} on Netflix",
                       action="open_url",
                       data={"url": url, "description": f"{query} on Netflix"}
                   )
               else:
                   response_data = CommandResponse(response="What would you like to watch on Netflix?")
           # Amazon search
           elif "on amazon" in lower_cmd:
               match = re.search(r"(?:open|search|find|buy)?\s*(.+?)\s+on\s+amazon", lower_cmd)
               if match:
                   query = match.group(1).strip()
                   url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
                   response_data = CommandResponse(
                       response=f"Opening {query} on Amazon",
                       action="open_url",
                       data={"url": url, "description": f"{query} on Amazon"}
                   )
               else:
                   response_data = CommandResponse(response="What would you like to search on Amazon?")
           # Twitter / X search
           elif any(s in lower_cmd for s in ["on twitter", "on x"]):
               pattern = r"(?:open|search|find)?\s*(.+?)\s+on\s+(?:twitter|x)"
               match = re.search(pattern, lower_cmd)
               if match:
                   query = match.group(1).strip()
                   url = f"https://twitter.com/search?q={query.replace(' ', '%20')}"
                   response_data = CommandResponse(
                       response=f"Opening {query} on Twitter",
                       action="open_url",
                       data={"url": url, "description": f"{query} on Twitter"}
                   )
               else:
                   response_data = CommandResponse(response="What would you like to search on Twitter?")
           # Facebook search
           elif "on facebook" in lower_cmd:
               match = re.search(r"(?:open|search|find)?\s*(.+?)\s+on\s+facebook", lower_cmd)
               if match:
                   query = match.group(1).strip()
                   url = f"https://www.facebook.com/search/top/?q={query.replace(' ', '%20')}"
                   response_data = CommandResponse(
                       response=f"Opening {query} on Facebook",
                       action="open_url",
                       data={"url": url, "description": f"{query} on Facebook"}
                   )
               else:
                   response_data = CommandResponse(response="What would you like to search on Facebook?")
           # Instagram search/profile
           elif "on instagram" in lower_cmd:
               match = re.search(r"(?:open|search|find)?\s*(.+?)\s+on\s+instagram", lower_cmd)
               if match:
                   query = match.group(1).strip()
                   if " " not in query:
                       url = f"https://www.instagram.com/{query}"
                       response_data = CommandResponse(
                           response=f"Opening {query}'s Instagram",
                           action="open_url",
                           data={"url": url, "description": f"{query}'s Instagram"}
                       )
                   else:
                       url = f"https://www.instagram.com/explore/tags/{query.replace(' ', '')}"
                       response_data = CommandResponse(
                           response=f"Opening #{query} on Instagram",
                           action="open_url",
                           data={"url": url, "description": f"#{query} on Instagram"}
                       )
               else:
                   response_data = CommandResponse(response="What would you like to search on Instagram?")
           # Google Maps / Directions
           elif any(s in lower_cmd for s in ["on maps", "on google maps", "directions to"]):
               if "directions to" in lower_cmd:
                   match = re.search(r"directions to\s+(.+?)(?:\s+from\s+(.+))?$", lower_cmd)
                   if match:
                       destination = match.group(1).strip()
                       origin = match.group(2).strip() if match.group(2) else ""
                       if origin:
                           url = f"https://www.google.com/maps/dir/{origin.replace(' ', '+')}/{destination.replace(' ', '+')}"
                           response_data = CommandResponse(
                               response=f"Getting directions from {origin} to {destination}",
                               action="open_url",
                               data={"url": url, "description": f"Directions from {origin} to {destination}"}
                           )
                       else:
                           url = f"https://www.google.com/maps/dir//{destination.replace(' ', '+')}"
                           response_data = CommandResponse(
                               response=f"Getting directions to {destination}",
                               action="open_url",
                               data={"url": url, "description": f"Directions to {destination}"}
                           )
                   else:
                       response_data = CommandResponse(response="Where would you like directions to?")
               else:
                   match = re.search(r"(?:find|search|locate|show)?\s*(.+?)\s+on\s+(?:maps|google maps)", lower_cmd)
                   if match:
                       location = match.group(1).strip()
                       url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
                       response_data = CommandResponse(
                           response=f"Showing {location} on Maps",
                           action="open_url",
                           data={"url": url, "description": f"{location} on Maps"}
                       )
                   else:
                       response_data = CommandResponse(response="What location would you like to find on Maps?")
           # News searches
           elif any(s in lower_cmd for s in ["news about", "latest news on"]):
               match = re.search(r"(?:news about|latest news on)\s+(.+)", lower_cmd)
               if match:
                   topic = match.group(1).strip()
                   url = f"https://news.google.com/search?q={topic.replace(' ', '+')}"
                   response_data = CommandResponse(
                       response=f"Here's the latest news about {topic}",
                       action="open_url",
                       data={"url": url, "description": f"News about {topic}"}
                   )
               else:
                   response_data = CommandResponse(response="What topic would you like news on?")
           # Email
           elif "open email" in lower_cmd or "check email" in lower_cmd:
               if "gmail" in lower_cmd:
                   url = "https://mail.google.com"
               elif "outlook" in lower_cmd:
                   url = "https://outlook.live.com"
               elif "yahoo" in lower_cmd:
                   url = "https://mail.yahoo.com"
               else:
                   url = "https://mail.google.com"
               response_data = CommandResponse(
                   response="Opening your email",
                   action="open_url",
                   data={"url": url, "description": "Email"}
               )
           # Streaming services
           else:
               streaming_services = {
                   "netflix": "https://www.netflix.com",
                   "hulu": "https://www.hulu.com",
                   "disney plus": "https://www.disneyplus.com",
                   "disney+": "https://www.disneyplus.com",
                   "prime video": "https://www.amazon.com/Prime-Video",
                   "amazon prime": "https://www.amazon.com/Prime-Video",
                   "hbo": "https://www.hbomax.com",
                   "hbo max": "https://www.hbomax.com",
                   "peacock": "https://www.peacocktv.com",
                   "paramount": "https://www.paramountplus.com",
                   "paramount+": "https://www.paramountplus.com",
                   "apple tv": "https://tv.apple.com",
                   "apple tv+": "https://tv.apple.com"
               }
               matched_service = next((s for s in streaming_services if f"open {s}" in lower_cmd), None)
               if matched_service:
                   url = streaming_services[matched_service]
                   response_data = CommandResponse(
                       response=f"Opening {matched_service.title()}",
                       action="open_url",
                       data={"url": url, "description": matched_service.title()}
                   )
               # Open generic websites or apps
               elif "open" in lower_cmd:
                   match = re.search(r"open\s+(.+?)(?:\s+on\s+google)?$", lower_cmd)
                   if match:
                       target = match.group(1).strip()
                       if " on google" in lower_cmd:
                           url = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                           response_data = CommandResponse(
                               response=f"Searching for {target} on Google",
                               action="open_url",
                               data={"url": url, "description": f"{target} on Google"}
                           )
                       else:
                           website_mapping = {
                               "youtube": "https://youtube.com",
                               "google": "https://google.com",
                               "gmail": "https://mail.google.com",
                               "spotify": "https://open.spotify.com",
                               "netflix": "https://netflix.com",
                               "amazon": "https://amazon.com",
                               "facebook": "https://facebook.com",
                               "instagram": "https://instagram.com",
                               "twitter": "https://twitter.com",
                               "x": "https://twitter.com",
                               "linkedin": "https://linkedin.com",
                               "reddit": "https://reddit.com",
                               "twitch": "https://twitch.tv",
                               "disney plus": "https://disneyplus.com",
                               "disney+": "https://disneyplus.com",
                               "hulu": "https://hulu.com",
                               "github": "https://github.com",
                               "stackoverflow": "https://stackoverflow.com",
                               "pinterest": "https://pinterest.com",
                               "maps": "https://maps.google.com",
                               "google maps": "https://maps.google.com"
                           }
                           mapped_site = next((site for site in website_mapping if site in target.lower()), None)
                           if mapped_site:
                               response_data = CommandResponse(
                                   response=f"Opening {mapped_site.title()}",
                                   action="open_url",
                                   data={"url": website_mapping[mapped_site], "description": mapped_site.title()}
                               )
                           else:
                               response_data = CommandResponse(
                                   response=f"Opening {target}",
                                   action="open_app",
                                   data={"app_name": target.title()}
                               )
                   else:
                       response_data = CommandResponse(response="What would you like me to open?")
               # Time queries
               elif "time" in lower_cmd and any(word in lower_cmd for word in ["what", "current", "right now"]):
                   current_time = datetime.datetime.now().strftime('%I:%M %p')
                   response_data = CommandResponse(response=f"It's {current_time}")
               # Date queries
               elif "date" in lower_cmd and any(word in lower_cmd for word in ["what", "today", "current"]):
                   current_date = datetime.datetime.today().strftime('%B %d, %Y')
                   response_data = CommandResponse(response=f"Today is {current_date}")
               # Default to AI fallback
               else:
                   response_data = await self._ai_fallback(lower_cmd, user_id)


       except Exception as e:
           logger.error(f"Command processing error: {e}")
           response_data = CommandResponse(response="Sorry, I had an error processing that request.")


       # 3) Append Ballsy’s response into session_memory
       session_memory["conversation_history"].append({
           "role": "assistant",
           "content": response_data.response
       })

       # 4) Generate TTS audio synchronously but with timeout to keep response fast
       # For ~1s response time, we generate TTS inline but it should be fast
       if config.ENABLE_GEMINI_TTS and not response_data.audio_base64 and response_data.response:
           try:
               logger.debug(f"Generating TTS for: '{response_data.response[:50]}...'")
               audio_base64 = synthesize_speech_base64(text=response_data.response)
               if audio_base64:
                   response_data.audio_base64 = audio_base64
                   logger.info(f"✅ Generated TTS audio (length: {len(audio_base64)} chars)")
               else:
                   logger.warning(f"TTS returned None for: '{response_data.response[:50]}...'")
           except Exception as tts_error:
               logger.warning(f"TTS generation failed: {tts_error}")
               # Continue without audio - response is still valid

       return response_data


   def _store_command(self, user_id: int, command: str, result: Optional[str] = None):
       """Store command in database for history."""
       try:
           with get_db_session() as session:
               history_entry = CommandHistory(
                   user_id=user_id,
                   command=command,
                   result=result
               )
               session.add(history_entry)
               session.commit()
       except Exception as e:
           logger.error(f"Error storing command: {e}")


   def _handle_math_expression(self, cmd: str, user_id = 1) -> Optional[CommandResponse]:
       """Handle math calculations."""
       try:
           session_memory = self._get_user_session(user_id)
           # Continuation math (e.g., "+ 6")
           if re.match(r"^\s*[\+\-\*\/]\s*\d+", cmd):
               if session_memory["last_result"] is not None:
                   expression = f"{session_memory['last_result']} {cmd}"
                   result = eval(expression)
                   session_memory["last_result"] = result
                   session_memory["calculations"].append({
                       "expression": expression,
                       "result": result
                   })
                   return CommandResponse(response=f"{result}")
           # Full math expression (e.g., "5 + 10")
           match = re.match(r"(?:what'?s\s*)?([\d\s\+\-\*\/]+)$", cmd)
           if match:
               expression = match.group(1).strip()
               result = eval(expression)
               session_memory["last_result"] = result
               session_memory["calculations"].append({
                   "expression": expression,
                   "result": result
               })
               return CommandResponse(response=f"{result}")
       except Exception as e:
           logger.error(f"Math error: {e}")
           return None
       return None


   async def _get_info_or_search(self, query: str, is_person: bool = False, user_id = 1) -> CommandResponse:
       """
       Try to answer a 'who is/what is' query via AI first. If uncertain, fall back to a search action.
       This method ALSO appends both the user and assistant turns to session_memory.
       """
       # Get user-specific session memory
       session_memory = self._get_user_session(user_id)
       
       # Build conversation history for Gemini
       conversation_history = session_memory["conversation_history"][-6:]
       
       if is_person:
           user_prompt = f"Who is {query}? Provide a brief, factual sentence about this person."
       else:
           user_prompt = f"Answer this briefly in one sentence: {query}"

       try:
           reply = await generate_reply(
               prompt=user_prompt,
               conversation_history=conversation_history,
               temperature=0.3,
               max_tokens=100,
               system_prompt=config.SYSTEM_PROMPT
           )


           uncertain_phrases = [
               "don't know", "not familiar", "can't find",
               "don't have information", "not sure",
               "unable to provide", "no information",
               "beyond my knowledge", "not available",
               "hello", "hi there", "what about", "it seems",
               "I don't have specific", "I don't have enough"
           ]


           # If AI's reply seems uncertain or too short, fall back to search
           if is_person and (
               any(phrase in reply.lower() for phrase in uncertain_phrases)
               or len(reply.split()) < 4
               or reply.endswith("?")
               or "would you like" in reply.lower()
           ):
               return CommandResponse(
                   response=f"Let me find information about {query}",
                   action="search",
                   data={"query": f"who is {query} person biography"}
               )
           elif not is_person and any(phrase in reply.lower() for phrase in uncertain_phrases):
               return CommandResponse(
                   response=f"Let me search for information about {query}",
                   action="search",
                   data={"query": query}
               )
           else:
               return CommandResponse(response=reply)


       except Exception as e:
           logger.error(f"Error getting info: {e}")
           if is_person:
               return CommandResponse(
                   response="Let me search for that",
                   action="search",
                   data={"query": f"who is {query} person"}
               )
           else:
               return CommandResponse(
                   response="Let me search for that",
                   action="search",
                   data={"query": query}
               )


   async def _ai_fallback(self, prompt: str, user_id = 1) -> CommandResponse:
       """
       Use Gemini AI for general responses. We inject recent conversation history so that the model
       is aware of previous turns in this session. We limit the response to one concise sentence.
       Also generates TTS audio if enabled.
       """
       # Get user-specific session memory
       session_memory = self._get_user_session(user_id)
       
       # Build conversation history for Gemini
       conversation_history = session_memory["conversation_history"][-6:]
       user_message = f"Answer this in a single concise sentence: {prompt}"

       try:
           raw_reply = await generate_reply(
               prompt=user_message,
               conversation_history=conversation_history,
               temperature=0.5,
               max_tokens=75,
               system_prompt=config.SYSTEM_PROMPT
           )
           # Ensure single-sentence
           sentences = re.split(r'(?<=[.!?])\s+', raw_reply)
           final_reply = sentences[0] if len(sentences) > 1 else raw_reply
           
           # Generate TTS audio if enabled
           audio_base64 = None
           if config.ENABLE_GEMINI_TTS:
               try:
                   audio_base64 = synthesize_speech_base64(text=final_reply)
                   if audio_base64:
                       logger.info(f"✅ Generated TTS audio for response (length: {len(audio_base64)} chars)")
                   else:
                       logger.warning("TTS returned None, falling back to browser TTS")
               except Exception as tts_error:
                   logger.warning(f"TTS generation failed, falling back to browser TTS: {tts_error}", exc_info=True)
           
           return CommandResponse(
               response=final_reply,
               audio_base64=audio_base64
           )
       except Exception as e:
           logger.error(f"Gemini AI error: {e}")
           return CommandResponse(
               response="Let me search for that",
               action="search",
               data={"query": prompt}
           )


# Instantiate single processor (memory lives until server restart)
command_processor = CommandProcessor()


# ──────────────────────────────────────────────────────────────────────────────
# Serve the frontend (HTML/CSS/JS)


frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(frontend_dir, "templates"))


@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
   """Serve the main UI."""
   return templates.TemplateResponse("index.html", {"request": request})


# ──────────────────────────────────────────────────────────────────────────────
# Health Check Endpoints
@app.get("/health")
async def health_check():
   """Simple health check endpoint."""
   return JSONResponse(content={"status": "ok"})


@app.get("/ready")
async def readiness_check():
   """Readiness check with database connectivity test."""
   from src.backend.database import check_db_connection
   
   db_ok = check_db_connection(max_retries=2, delay=0.5)
   if db_ok:
       return JSONResponse(content={"status": "ready", "db": "ok"})
   else:
       return JSONResponse(
           status_code=503,
           content={"status": "not ready", "db": "unavailable"}
       )


@app.get("/debug/tts")
async def debug_tts():
   """Debug endpoint to test TTS functionality."""
   from src.backend.tts import synthesize_pcm
   
   try:
       _ = synthesize_pcm("This is a human-like Gemini voice test.")
       return JSONResponse(content={"ok": True, "message": "TTS synthesis successful"})
   except Exception as e:
       logger.error(f"TTS debug error: {e}", exc_info=True)
       return JSONResponse(
           status_code=500,
           content={"ok": False, "error": str(e)}
       )


# ──────────────────────────────────────────────────────────────────────────────
# API Endpoints


@app.post("/api/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
   """Process a text command and return the response."""
   # Security: Additional validation
   if not request.command or len(request.command) > 1000:
       raise HTTPException(status_code=400, detail="Invalid command")
   
   response = await command_processor.process_command(request.command, request.user_id)
   return response


@app.post("/api/voice", response_model=CommandResponse)
async def process_voice(file: UploadFile = File(...), user_id: int = 1):
   """Process a voice file and return the response."""
   temp_file_path = f"temp_audio_{int(time.time())}.wav"
   try:
       with open(temp_file_path, "wb") as buffer:
           buffer.write(await file.read())
       text = speech_recognizer.recognize_from_file(temp_file_path)
       if not text:
           return CommandResponse(response="I didn't catch that. Could you please repeat?")
       response = await command_processor.process_command(text, user_id)
       return response
   finally:
       if os.path.exists(temp_file_path):
           os.remove(temp_file_path)


@app.get("/api/history/{user_id}")
async def get_command_history(user_id: int, limit: int = 10):
   """Get command history for a user."""
   try:
       with get_db_session() as session:
           history_entries = session.query(CommandHistory)\
               .filter(CommandHistory.user_id == user_id)\
               .order_by(CommandHistory.timestamp.desc())\
               .limit(limit)\
               .all()
           history = [
               {
                   "id": entry.id,
                   "user_id": entry.user_id,
                   "command": entry.command,
                   "result": entry.result,
                   "timestamp": entry.timestamp.isoformat() if entry.timestamp else None
               }
               for entry in history_entries
           ]
           return {"history": history}
   except Exception as e:
       logger.error(f"Error retrieving command history: {e}")
       raise HTTPException(status_code=500, detail="Failed to retrieve command history")


@app.put("/api/settings/{user_id}")
async def update_settings(user_id: int, settings: SettingsUpdate):
   """Update user settings."""
   try:
       with get_db_session() as session:
           # Ensure user exists
           user = session.query(User).filter(User.id == user_id).first()
           if not user:
               user = User(id=user_id, username=f"user{user_id}")
               session.add(user)
               session.flush()
           
           # Get or create settings
           setting = session.query(Setting).filter(Setting.user_id == user_id).first()
           if not setting:
               setting = Setting(user_id=user_id)
               session.add(setting)
           
           # Update fields
           if settings.voice is not None:
               setting.voice = settings.voice
           if settings.voice_speed is not None:
               setting.voice_speed = settings.voice_speed
           if settings.theme is not None:
               setting.theme = settings.theme
           
           session.commit()
           
           return {
               "settings": {
                   "user_id": setting.user_id,
                   "voice": setting.voice,
                   "voice_speed": setting.voice_speed,
                   "theme": setting.theme
               }
           }
   except Exception as e:
       logger.error(f"Error updating settings: {e}")
       raise HTTPException(status_code=500, detail="Failed to update settings")


@app.get("/api/settings/{user_id}")
async def get_settings(user_id: int):
   """Get user settings."""
   try:
       with get_db_session() as session:
           setting = session.query(Setting).filter(Setting.user_id == user_id).first()
           if not setting:
               return {
                   "settings": {
                       "user_id": user_id,
                       "voice": config.VOICE,
                       "voice_speed": config.VOICE_SPEED,
                       "theme": "light"
                   }
               }
           return {
               "settings": {
                   "user_id": setting.user_id,
                   "voice": setting.voice,
                   "voice_speed": setting.voice_speed,
                   "theme": setting.theme
               }
           }
   except Exception as e:
       logger.error(f"Error retrieving settings: {e}")
       raise HTTPException(status_code=500, detail="Failed to retrieve settings")


# ──────────────────────────────────────────────────────────────────────────────
# WebSocket endpoint for real-time voice communication


@app.websocket("/ws/voice/{client_id}")
async def websocket_voice_endpoint(websocket: WebSocket, client_id: int):
   """
   WebSocket endpoint for real-time voice communication.
   Receives JSON messages like {"command": "..."} or {"status": "listening"}.
   """
   await manager.connect(websocket, client_id)
   try:
       while True:
           data = await websocket.receive_json()
           if "command" in data:
               resp = await command_processor.process_command(data["command"], client_id)
               await manager.send_message(client_id, {
                   "type": "command_response",
                   "data": resp.dict()
               })
           elif "status" in data and data["status"] == "listening":
               await manager.send_message(client_id, {
                   "type": "status_update",
                   "status": "ready"
               })
           else:
               await manager.send_message(client_id, {
                   "type": "error",
                   "message": "Unknown message format"
               })
   except WebSocketDisconnect:
       manager.disconnect(client_id)
       logger.info(f"Client #{client_id} disconnected")
   except Exception as e:
       logger.error(f"WebSocket error: {e}")
       manager.disconnect(client_id)


# ──────────────────────────────────────────────────────────────────────────────
# End of file



