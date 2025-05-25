#!/usr/bin/env python3
"""
Backend application for the full-stack voice assistant with Siri-like UI.
This module provides the core backend functionality including:
- FastAPI server with REST and WebSocket endpoints
- Speech recognition and processing
- AI integration with Mistral
- Command processing and execution
- External service integration
- Auto-clear conversation history on startup
"""

import os
import re
import time
import json
import asyncio
import logging
import datetime
import subprocess
import webbrowser
from typing import Dict, List, Optional, Union, Any
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Speech recognition
import speech_recognition as sr

# AI integration
from mistralai import Mistral
from dotenv import load_dotenv

# Database
import sqlite3
from contextlib import contextmanager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("voice_assistant.log")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=".env")

# Initialize Mistral client
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "W7ubHcUDajunz3zrREm7zXya31Nlj9n2")
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

# Constants
MISTRAL_MODEL = "mistral-large-latest"
SYSTEM_PROMPT = "You are Ballsy, a helpful voice assistant. Always provide a single sentence answer, keeping responses brief, concise, and to the point."
DB_PATH = "voice_assistant.db"
VOICE = "Daniel"  # Default voice
VOICE_SPEED = 180  # Default speech rate

# Function to clear conversation history on startup
def clear_conversation_history():
    """Clear all conversation history for a fresh start."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Clear all messages and command history
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM command_history")
            cursor.execute("DELETE FROM conversations")
            conn.commit()
            logger.info("✨ Conversation history cleared - Fresh start for Ballsy!")
    except Exception as e:
        logger.error(f"Error clearing history: {e}")

# Define lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and clear history
    init_db()
    logger.info("Database initialized")
    
    # Clear conversation history for fresh start
    clear_conversation_history()
    
    yield
    # Shutdown: Clean up resources if needed
    logger.info("Shutting down Ballsy...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Ballsy Voice Assistant API",
    description="Backend API for Ballsy - the full-stack voice assistant with Siri-like UI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Database setup
def init_db():
    """Initialize the SQLite database with required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            is_user BOOLEAN NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
        ''')
        
        # Settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            voice TEXT DEFAULT 'Daniel',
            voice_speed INTEGER DEFAULT 180,
            theme TEXT DEFAULT 'light',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Command history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            command TEXT NOT NULL,
            result TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()

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
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# Pydantic models
class CommandRequest(BaseModel):
    command: str
    user_id: Optional[int] = 1

class CommandResponse(BaseModel):
    response: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

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
    
    def recognize_from_file(self, audio_file):
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

# Command processor
class CommandProcessor:
    def __init__(self):
        self.session_memory = {
            "conversation_history": [],
            "current_topic": None,
            "last_question": None,
            "calculations": [],
            "last_result": None
        }
    
    async def process_command(self, cmd: str, user_id: int = 1) -> CommandResponse:
        """Process a voice command and return appropriate response."""
        if not cmd:
            return CommandResponse(response="I didn't catch that. Could you please repeat?")
        
        try:
            # Store command in history
            self._store_command(user_id, cmd)
            
            # Basic greetings
            if cmd.lower() in ["hello", "hi", "hey"]:
                return CommandResponse(response="Hi there! I'm Ballsy, your voice assistant. How can I help?")
            
            # Name questions
            if any(phrase in cmd.lower() for phrase in ["what's your name", "who are you", "what are you called"]):
                return CommandResponse(response="I'm Ballsy, your personal voice assistant!")
            
            # How are you
            if any(phrase in cmd.lower() for phrase in ["how are you", "how's it going", "what's up"]):
                return CommandResponse(response="I'm doing great! Ready to help you with anything you need!")
            
            # Exit commands
            if any(word in cmd.lower() for word in ["bye", "goodbye", "exit", "stop", "quit"]):
                return CommandResponse(
                    response="Goodbye! Take care!",
                    action="exit"
                )
            
            # Who is/What is questions - AI response
            if any(phrase in cmd.lower() for phrase in ["who is", "who's", "what is", "what's", "tell me about"]):
                # Check if it's a person query
                is_person = any(phrase in cmd.lower() for phrase in ["who is", "who's"])
                
                # Remove question words to get the subject
                subject = cmd.lower()
                for phrase in ["who is", "who's", "what is", "what's", "tell me about"]:
                    subject = subject.replace(phrase, "").strip()
                
                if subject:
                    # Try AI first, falls back to search if needed
                    result = await self._get_info_or_search(subject, is_person)
                    return result
            
            # Math expressions
            if re.match(r"(?:what'?s\s*)?([\d\s\+\-\*\/]+)$", cmd) or re.match(r"^\s*[\+\-\*\/]\s*\d+", cmd):
                result = self._handle_math_expression(cmd)
                if result:
                    return result
            
            # YouTube specific searches
            if "on youtube" in cmd.lower():
                match = re.search(r"(?:open|search|play|watch)?\s*(.+?)\s+on\s+youtube", cmd.lower())
                if match:
                    query = match.group(1).strip()
                    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                    return CommandResponse(
                        response=f"Opening {query} on YouTube",
                        action="open_url",
                        data={"url": url, "description": f"{query} on YouTube"}
                    )
            
            # Popular Sites URL Handlers
            # Spotify
            if "on spotify" in cmd.lower():
                match = re.search(r"(?:open|search|play|listen to)?\s*(.+?)\s+on\s+spotify", cmd.lower())
                if match:
                    query = match.group(1).strip()
                    url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
                    return CommandResponse(
                        response=f"Opening {query} on Spotify",
                        action="open_url",
                        data={"url": url, "description": f"{query} on Spotify"}
                    )
            
            # Netflix
            if "on netflix" in cmd.lower():
                match = re.search(r"(?:open|search|play|watch)?\s*(.+?)\s+on\s+netflix", cmd.lower())
                if match:
                    query = match.group(1).strip()
                    url = f"https://www.netflix.com/search?q={query.replace(' ', '%20')}"
                    return CommandResponse(
                        response=f"Opening {query} on Netflix",
                        action="open_url",
                        data={"url": url, "description": f"{query} on Netflix"}
                    )
            
            # Amazon
            if "on amazon" in cmd.lower():
                match = re.search(r"(?:open|search|find|buy)?\s*(.+?)\s+on\s+amazon", cmd.lower())
                if match:
                    query = match.group(1).strip()
                    url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
                    return CommandResponse(
                        response=f"Opening {query} on Amazon",
                        action="open_url",
                        data={"url": url, "description": f"{query} on Amazon"}
                    )
            
            # Twitter/X
            if any(s in cmd.lower() for s in ["on twitter", "on x"]):
                pattern = r"(?:open|search|find)?\s*(.+?)\s+on\s+(?:twitter|x)"
                match = re.search(pattern, cmd.lower())
                if match:
                    query = match.group(1).strip()
                    url = f"https://twitter.com/search?q={query.replace(' ', '%20')}"
                    return CommandResponse(
                        response=f"Opening {query} on Twitter",
                        action="open_url",
                        data={"url": url, "description": f"{query} on Twitter"}
                    )
            
            # Facebook
            if "on facebook" in cmd.lower():
                match = re.search(r"(?:open|search|find)?\s*(.+?)\s+on\s+facebook", cmd.lower())
                if match:
                    query = match.group(1).strip()
                    url = f"https://www.facebook.com/search/top/?q={query.replace(' ', '%20')}"
                    return CommandResponse(
                        response=f"Opening {query} on Facebook",
                        action="open_url",
                        data={"url": url, "description": f"{query} on Facebook"}
                    )
            
            # Instagram
            if "on instagram" in cmd.lower():
                match = re.search(r"(?:open|search|find)?\s*(.+?)\s+on\s+instagram", cmd.lower())
                if match:
                    query = match.group(1).strip()
                    # Check if it's a username (without spaces)
                    if " " not in query:
                        url = f"https://www.instagram.com/{query}"
                        return CommandResponse(
                            response=f"Opening {query}'s Instagram",
                            action="open_url",
                            data={"url": url, "description": f"{query}'s Instagram"}
                        )
                    else:
                        # Assume it's a search or hashtag
                        url = f"https://www.instagram.com/explore/tags/{query.replace(' ', '')}"
                        return CommandResponse(
                            response=f"Opening #{query} on Instagram",
                            action="open_url",
                            data={"url": url, "description": f"#{query} on Instagram"}
                        )
            
            # Google Maps
            if any(s in cmd.lower() for s in ["on maps", "on google maps", "directions to"]):
                if "directions to" in cmd.lower():
                    match = re.search(r"directions to\s+(.+?)(?:\s+from\s+(.+))?$", cmd.lower())
                    if match:
                        destination = match.group(1).strip()
                        origin = match.group(2).strip() if match.group(2) else ""
                        if origin:
                            url = f"https://www.google.com/maps/dir/{origin.replace(' ', '+')}/{destination.replace(' ', '+')}"
                            return CommandResponse(
                                response=f"Getting directions from {origin} to {destination}",
                                action="open_url",
                                data={"url": url, "description": f"Directions from {origin} to {destination}"}
                            )
                        else:
                            url = f"https://www.google.com/maps/dir//{destination.replace(' ', '+')}"
                            return CommandResponse(
                                response=f"Getting directions to {destination}",
                                action="open_url",
                                data={"url": url, "description": f"Directions to {destination}"}
                            )
                else:
                    match = re.search(r"(?:find|search|locate|show)?\s*(.+?)\s+on\s+(?:maps|google maps)", cmd.lower())
                    if match:
                        location = match.group(1).strip()
                        url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
                        return CommandResponse(
                            response=f"Showing {location} on Maps",
                            action="open_url",
                            data={"url": url, "description": f"{location} on Maps"}
                        )
            
            # News searches
            if any(s in cmd.lower() for s in ["news about", "latest news on"]):
                match = re.search(r"(?:news about|latest news on)\s+(.+)", cmd.lower())
                if match:
                    topic = match.group(1).strip()
                    url = f"https://news.google.com/search?q={topic.replace(' ', '+')}"
                    return CommandResponse(
                        response=f"Here's the latest news about {topic}",
                        action="open_url",
                        data={"url": url, "description": f"News about {topic}"}
                    )
            
            # Email
            if "open email" in cmd.lower() or "check email" in cmd.lower():
                if "gmail" in cmd.lower():
                    url = "https://mail.google.com"
                elif "outlook" in cmd.lower():
                    url = "https://outlook.live.com"
                elif "yahoo" in cmd.lower():
                    url = "https://mail.yahoo.com"
                else:
                    # Default to Gmail
                    url = "https://mail.google.com"
                return CommandResponse(
                    response="Opening your email",
                    action="open_url",
                    data={"url": url, "description": "Email"}
                )
            
            # Streaming services
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
            
            # Check if command contains any streaming service
            for service, url in streaming_services.items():
                if f"open {service}" in cmd.lower():
                    return CommandResponse(
                        response=f"Opening {service.title()}",
                        action="open_url",
                        data={"url": url, "description": service.title()}
                    )
            
            # Open commands for websites
            if "open" in cmd.lower():
                match = re.search(r"open\s+(.+?)(?:\s+on\s+google)?$", cmd.lower())
                if match:
                    target = match.group(1).strip()
                    
                    # Check if it should be opened on Google
                    if " on google" in cmd.lower():
                        url = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                        return CommandResponse(
                            response=f"Searching for {target} on Google",
                            action="open_url",
                            data={"url": url, "description": f"{target} on Google"}
                        )
                    
                    # Web applications and websites
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
                    
                    # Check for websites
                    for site, url in website_mapping.items():
                        if site in target.lower():
                            return CommandResponse(
                                response=f"Opening {site.title()}",
                                action="open_url",
                                data={"url": url, "description": site.title()}
                            )
                    
                    # If not a known website, try to open as an app
                    return CommandResponse(
                        response=f"Opening {target}",
                        action="open_app",
                        data={"app_name": target.title()}
                    )
            
            # Time
            if "time" in cmd.lower() and any(word in cmd.lower() for word in ["what", "current", "right now"]):
                current_time = datetime.datetime.now().strftime('%I:%M %p')
                return CommandResponse(response=f"It's {current_time}")
            
            # Date
            if "date" in cmd.lower() and any(word in cmd.lower() for word in ["what", "today", "current"]):
                current_date = datetime.datetime.today().strftime('%B %d, %Y')
                return CommandResponse(response=f"Today is {current_date}")
            
            # Default to AI for everything else
            ai_response = await self._ai_fallback(cmd)
            return ai_response
            
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            return CommandResponse(response="Sorry, I had an error processing that request.")
    
    def _store_command(self, user_id: int, command: str, result: str = None):
        """Store command in database for history."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO command_history (user_id, command, result) VALUES (?, ?, ?)",
                    (user_id, command, result)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing command: {e}")
    
    def _handle_math_expression(self, cmd: str) -> Optional[CommandResponse]:
        """Handle math calculations."""
        try:
            # Handle continuation like "+ 6"
            if re.match(r"^\s*[\+\-\*\/]\s*\d+", cmd):
                if self.session_memory["last_result"] is not None:
                    expression = f"{self.session_memory['last_result']} {cmd}"
                    result = eval(expression)
                    
                    self.session_memory["last_result"] = result
                    self.session_memory["calculations"].append({
                        "expression": expression,
                        "result": result
                    })
                    
                    return CommandResponse(response=f"{result}")
            
            # Handle full math expressions like "5 + 10"
            match = re.match(r"(?:what'?s\s*)?([\d\s\+\-\*\/]+)$", cmd)
            if match:
                expression = match.group(1).strip()
                result = eval(expression)
                
                self.session_memory["last_result"] = result
                self.session_memory["calculations"].append({
                    "expression": expression,
                    "result": result
                })
                
                return CommandResponse(response=f"{result}")
        
        except Exception as e:
            logger.error(f"Math error: {e}")
            return None
        
        return None
    
    async def _get_info_or_search(self, query: str, is_person: bool = False) -> CommandResponse:
        """Try to answer with AI first, then fall back to search."""
        try:
            # Customize prompt based on whether it's a person query
            if is_person:
                prompt = f"Who is {query}? Provide a brief, factual sentence about this person."
            else:
                prompt = f"Answer this briefly in one sentence: {query}"
            
            # First try to get info from Mistral AI
            chat_response = mistral_client.chat.complete(
                model=MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            reply = chat_response.choices[0].message.content.strip()
            
            # Check if the AI gave a non-answer
            uncertain_phrases = [
                "don't know", "not familiar", "can't find",
                "don't have information", "not sure",
                "unable to provide", "no information",
                "beyond my knowledge", "not available",
                "hello", "hi there", "what about", "it seems",
                "I don't have specific", "I don't have enough"
            ]
            
            # For person queries, check for generic or uncertain responses
            if is_person and (
                    any(phrase in reply.lower() for phrase in uncertain_phrases) or
                    len(reply.split()) < 4 or  # Too short to be informative
                    reply.endswith("?") or  # AI is asking a question back
                    "would you like" in reply.lower()
            ):
                # AI doesn't know or gave generic response, search for the person
                search_term = f"who is {query} person biography"
                return CommandResponse(
                    response=f"Let me find information about {query}",
                    action="search",
                    data={"query": search_term}
                )
            elif not is_person and any(phrase in reply.lower() for phrase in uncertain_phrases):
                # AI doesn't know, search on Google
                return CommandResponse(
                    response=f"Let me search for information about {query}",
                    action="search",
                    data={"query": query}
                )
            else:
                # AI provided an answer
                return CommandResponse(response=reply)
        
        except Exception as e:
            logger.error(f"Error getting info: {e}")
            # Fall back to search on failure
            if is_person:
                return CommandResponse(
                    response=f"Let me search for that",
                    action="search",
                    data={"query": f"who is {query} person"}
                )
            else:
                return CommandResponse(
                    response=f"Let me search for that",
                    action="search",
                    data={"query": query}
                )
    
    async def _ai_fallback(self, prompt: str) -> CommandResponse:
        """Use Mistral AI for general responses - limited to one sentence."""
        try:
            # Explicitly request single sentence responses
            augmented_prompt = f"Answer this in a single concise sentence: {prompt}"
            
            chat_response = mistral_client.chat.complete(
                model=MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": augmented_prompt}
                ],
                temperature=0.5,
                max_tokens=75  # Reduced to encourage shorter responses
            )
            
            reply = chat_response.choices[0].message.content.strip()
            
            # If response still has multiple sentences, just keep the first one
            sentences = re.split(r'(?<=[.!?])\s+', reply)
            if len(sentences) > 1:
                reply = sentences[0]
            
            return CommandResponse(response=reply)
        
        except Exception as e:
            logger.error(f"Mistral AI error: {e}")
            # Fall back to search on AI failure
            return CommandResponse(
                response="Let me search for that",
                action="search",
                data={"query": prompt}
            )

command_processor = CommandProcessor()

# API Routes
@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Ballsy Voice Assistant API",
        "version": "1.0.0",
        "status": "running",
        "message": "Ballsy is ready to help!"
    }

@app.post("/api/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """Process a text command and return the response."""
    response = await command_processor.process_command(request.command, request.user_id)
    return response

@app.post("/api/voice", response_model=CommandResponse)
async def process_voice(file: UploadFile = File(...), user_id: int = 1):
    """Process a voice file and return the response."""
    # Save the uploaded file temporarily
    temp_file_path = f"temp_audio_{int(time.time())}.wav"
    try:
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Recognize speech from the file
        text = speech_recognizer.recognize_from_file(temp_file_path)
        
        if not text:
            return CommandResponse(response="I didn't catch that. Could you please repeat?")
        
        # Process the recognized command
        response = await command_processor.process_command(text, user_id)
        return response
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/api/history/{user_id}")
async def get_command_history(user_id: int, limit: int = 10):
    """Get command history for a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM command_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            history = [dict(row) for row in cursor.fetchall()]
            return {"history": history}
    except Exception as e:
        logger.error(f"Error retrieving command history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve command history")

@app.put("/api/settings/{user_id}")
async def update_settings(user_id: int, settings: SettingsUpdate):
    """Update user settings."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                # Create user if not exists
                cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
            
            # Update settings
            updates = []
            params = []
            
            if settings.voice is not None:
                updates.append("voice = ?")
                params.append(settings.voice)
            
            if settings.voice_speed is not None:
                updates.append("voice_speed = ?")
                params.append(settings.voice_speed)
            
            if settings.theme is not None:
                updates.append("theme = ?")
                params.append(settings.theme)
            
            if updates:
                # Check if settings exist for user
                cursor.execute("SELECT id FROM settings WHERE user_id = ?", (user_id,))
                user_settings = cursor.fetchone()
                
                if user_settings:
                    # Update existing settings
                    query = f"UPDATE settings SET {', '.join(updates)} WHERE user_id = ?"
                    params.append(user_id)
                    cursor.execute(query, params)
                else:
                    # Create new settings
                    columns = ["user_id"]
                    values = ["?"]
                    params_with_user_id = [user_id]
                    
                    if settings.voice is not None:
                        columns.append("voice")
                        values.append("?")
                        params_with_user_id.append(settings.voice)
                    
                    if settings.voice_speed is not None:
                        columns.append("voice_speed")
                        values.append("?")
                        params_with_user_id.append(settings.voice_speed)
                    
                    if settings.theme is not None:
                        columns.append("theme")
                        values.append("?")
                        params_with_user_id.append(settings.theme)
                    
                    query = f"INSERT INTO settings ({', '.join(columns)}) VALUES ({', '.join(values)})"
                    cursor.execute(query, params_with_user_id)
            
            conn.commit()
            
            # Return updated settings
            cursor.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,))
            updated_settings = dict(cursor.fetchone())
            return {"settings": updated_settings}
    
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

@app.get("/api/settings/{user_id}")
async def get_settings(user_id: int):
    """Get user settings."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,))
            settings = cursor.fetchone()
            
            if not settings:
                # Return default settings if not found
                return {
                    "settings": {
                        "user_id": user_id,
                        "voice": VOICE,
                        "voice_speed": VOICE_SPEED,
                        "theme": "light"
                    }
                }
            
            return {"settings": dict(settings)}
    
    except Exception as e:
        logger.error(f"Error retrieving settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve settings")

# WebSocket endpoint for real-time voice communication
@app.websocket("/ws/voice/{client_id}")
async def websocket_voice_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Receive JSON data
            data = await websocket.receive_json()
            
            if "command" in data:
                # Process text command
                response = await command_processor.process_command(data["command"], client_id)
                await manager.send_message(client_id, {
                    "type": "command_response",
                    "data": response.dict()
                })
            
            elif "status" in data and data["status"] == "listening":
                # Client is listening for voice input
                await manager.send_message(client_id, {
                    "type": "status_update",
                    "status": "ready"
                })
            
            else:
                # Unknown message type
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

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Serve static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI server
    logger.info("🚀 Starting Ballsy Voice Assistant...")
    uvicorn.run(app, host="0.0.0.0", port=8000)