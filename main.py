#!/usr/bin/env python3
import os
import re
import time
import subprocess
import webbrowser
import datetime
import speech_recognition as sr
from mistralai import Mistral
from dotenv import load_dotenv


# ——— Load API key ———
load_dotenv(dotenv_path=".env")
mistral_client = Mistral(api_key="W7ubHcUDajunz3zrREm7zXya31Nlj9n2")


# Instruct the AI to respond in a single sentence
SYSTEM = "You are Ballsy, a helpful voice assistant. Always provide a single sentence answer, keeping responses brief, concise, and to the point."
MEMORY_FILE = "memory.json"


# Mistral AI model to use
MISTRAL_MODEL = "mistral-large-latest"


# ——— Voice and Sound Settings ———
VOICE = "Daniel"  # Using Daniel voice as in your current code
VOICE_SPEED = 180  # Speech rate
STARTUP_SOUND = "Hero.aiff"  # Path to startup sound file (we'll create this)


# ——— Session Memory ———
session_memory = {
   "conversation_history": [],
   "current_topic": None,
   "last_question": None,
   "calculations": [],
   "last_result": None
}


# ——— Initialize Recognizer ———
r = sr.Recognizer()
r.pause_threshold = 1.5
r.dynamic_energy_threshold = True
r.energy_threshold = 200
r.operation_timeout = None




def say(text: str, speed: int = VOICE_SPEED):
   """Speak text using the selected voice and speed"""
   print("Ballsy:", text)
   try:
       subprocess.call(["say", "-v", VOICE, "-r", str(speed), text])
   except Exception as e:
       print(f"Speech error: {e}")




def create_startup_sound():
   """Create a startup sound file if it doesn't exist"""
   if os.path.exists(STARTUP_SOUND):
       return True


   try:
       # Use a gentle tone/chime instead of robot voice
       subprocess.run([
           "say",
           "-v", "Daniel",  # Using the same voice as the assistant
           "Hello",
           "-o", STARTUP_SOUND
       ], check=True)
       return True
   except Exception as e:
       print(f"Error creating startup sound: {e}")
       return False




def play_startup_sound():
   """Play a cool startup sound"""
   subprocess.call(["afplay", "/System/Library/Sounds/Glass.aiff"])
def play_startup_sound1():
   """Play a cool startup sound"""
   subprocess.call(["afplay", "/System/Library/Sounds/Hero.aiff"])


def calibrate_microphone():
   with sr.Microphone() as source:
       print("Calibrating microphone...")
       r.adjust_for_ambient_noise(source, duration=3)
       print(f"Energy threshold set to: {r.energy_threshold}")


       if r.energy_threshold > 500:
           r.energy_threshold = 300
           print(f"Adjusted threshold to: {r.energy_threshold}")




def take_command() -> str:
   with sr.Microphone() as source:
       print("\n🎤 Listening...")


       try:
           r.adjust_for_ambient_noise(source, duration=0.3)


           audio = r.listen(
               source,
               timeout=15,
               phrase_time_limit=25
           )


           print("🔄 Processing speech...")


           try:
               text = r.recognize_google(audio, language="en-US", show_all=False)
               print(f"✅ You said: '{text}'")


               return text.lower().strip()
           except sr.UnknownValueError:
               print("❌ Could not understand audio")
               return ""
           except sr.RequestError as e:
               print(f"❌ Speech service error: {e}")
               return ""


       except sr.WaitTimeoutError:
           print("⏰ No speech detected")
           return ""
       except Exception as e:
           print(f"❌ Recognition error: {e}")
           return ""




def handle_math_expression(cmd: str) -> bool:
   """Handle math calculations"""
   try:
       # Handle continuation like "+ 6"
       if re.match(r"^\s*[\+\-\*\/]\s*\d+", cmd):
           if session_memory["last_result"] is not None:
               expression = f"{session_memory['last_result']} {cmd}"
               result = eval(expression)


               session_memory["last_result"] = result
               session_memory["calculations"].append({
                   "expression": expression,
                   "result": result
               })


               say(f"{result}", speed=190)
               return True


       # Handle full math expressions like "5 + 10"
       match = re.match(r"(?:what'?s\s*)?([\d\s\+\-\*\/]+)$", cmd)
       if match:
           expression = match.group(1).strip()
           result = eval(expression)


           session_memory["last_result"] = result
           session_memory["calculations"].append({
               "expression": expression,
               "result": result
           })


           say(f"{result}", speed=190)
           return True


   except Exception as e:
       print(f"Math error: {e}")
       return False


   return False




def search_in_chrome(query: str):
   """Search directly in Google Chrome"""
   try:
       # First try to use Chrome specifically
       chrome_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"


       # Try to open with Chrome specifically first
       process = subprocess.Popen(["open", "-a", "Google Chrome", chrome_url],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
       stdout, stderr = process.communicate()


       # If Chrome not found, fall back to default browser
       if process.returncode != 0:
           webbrowser.open(chrome_url)


       return True
   except Exception as e:
       print(f"Error searching in Chrome: {e}")
       # Fall back to default browser
       webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
       return False




def open_app(app_name: str):
   """Try to open an app - search on Google if not found"""
   try:
       # First attempt to open the app directly
       process = subprocess.Popen(["open", "-a", app_name],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
       stdout, stderr = process.communicate()


       # Check if the app was successfully opened
       if process.returncode == 0:
           say(f"Opening {app_name}", speed=190)
           return True
       else:
           # App not found - directly search on Google Chrome
           say(f"I couldn't find {app_name}, searching for it", speed=190)
           search_in_chrome(f"{app_name} app mac")
           return False


   except Exception as e:
       print(f"Error opening app: {e}")
       say(f"I couldn't open {app_name}, searching for it", speed=190)
       search_in_chrome(f"{app_name} app mac")
       return False




def open_url(url: str, description: str):
   try:
       webbrowser.open(url)
       say(f"Opening {description}", speed=190)
   except:
       say("Couldn't open that", speed=190)




def close_app(app_name: str):
   """Try to close an app by name"""
   try:
       # AppleScript to close an application
       script = f'''
       tell application "{app_name}"
           quit
       end tell
       '''


       process = subprocess.Popen(['osascript', '-e', script],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
       stdout, stderr = process.communicate()


       if process.returncode == 0:
           say(f"Closed {app_name}", speed=190)
           return True
       else:
           # App might not be running or doesn't exist
           error = stderr.decode().strip()
           if "Application isn't running" in error:
               say(f"{app_name} is not currently running", speed=190)
           else:
               say(f"I couldn't close {app_name}", speed=190)
           return False
   except Exception as e:
       print(f"Error closing app: {e}")
       say(f"I encountered an error trying to close {app_name}", speed=190)
       return False




# Replace the existing get_info_or_search function with this improved version
def get_info_or_search(query: str, is_person=False):
   """Try to answer with AI first, then fall back to search"""
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
               {"role": "system", "content": SYSTEM},
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
           say(f"Let me find information about {query}", speed=190)
           search_term = f"who is {query} person biography"
           search_in_chrome(search_term)
           return False
       elif not is_person and any(phrase in reply.lower() for phrase in uncertain_phrases):
           # AI doesn't know, search on Google with Chrome
           say(f"Let me search for information about {query}", speed=190)
           search_in_chrome(query)
           return False
       else:
           # AI provided an answer
           say(reply, speed=190)
           return True


   except Exception as e:
       print(f"Error getting info: {e}")
       # Fall back to search on failure
       say(f"Let me search for that", speed=190)
       if is_person:
           search_in_chrome(f"who is {query} person")
       else:
           search_in_chrome(query)
       return False




# ——— Mistral AI Integration ———
def ai_get_info(subject: str):
   """Get information about a person/thing using Mistral AI"""
   return get_info_or_search(subject)




def ai_fallback(prompt: str):
   """Use Mistral AI for general responses - limited to one sentence"""
   try:
       # Explicitly request single sentence responses
       augmented_prompt = f"Answer this in a single concise sentence: {prompt}"


       chat_response = mistral_client.chat.complete(
           model=MISTRAL_MODEL,
           messages=[
               {"role": "system", "content": SYSTEM},
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


       say(reply, speed=190)
   except Exception as e:
       print(f"Mistral AI error: {e}")
       # Fall back to search on AI failure
       say("Let me search for that", speed=190)
       search_in_chrome(prompt)




def process_command(cmd: str):
   if not cmd:
       print("💭 Waiting...")
       return


   try:
       # Exit commands
       if cmd.lower() in ["hello", "hi", "hey"]:
           say("Hi there! How can I help?", speed=190)
           return


       if any(phrase in cmd.lower() for phrase in ["how are you", "how's it going", "what's up"]):
           say("I'm doing great! What about you?", speed=190)
           return


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
               get_info_or_search(subject, is_person=is_person)
               return


       if any(word in cmd.lower() for word in ["bye", "goodbye", "exit", "stop", "quit"]):
           say("Goodbye! Take care!", speed=190)
           exit(0)


       # Math expressions
       if re.match(r"(?:what'?s\s*)?([\d\s\+\-\*\/]+)$", cmd) or re.match(r"^\s*[\+\-\*\/]\s*\d+", cmd):
           if handle_math_expression(cmd):
               return


       # YouTube specific searches
       if "on youtube" in cmd.lower():
           # Extract search query before "on youtube"
           match = re.search(r"(?:open|search|play|watch)?\s*(.+?)\s+on\s+youtube", cmd.lower())
           if match:
               query = match.group(1).strip()
               url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
               open_url(url, f"{query} on YouTube")
               return


       # Popular Sites URL Handlers


       # For Spotify searches and playlists
       if "on spotify" in cmd.lower():
           match = re.search(r"(?:open|search|play|listen to)?\s*(.+?)\s+on\s+spotify", cmd.lower())
           if match:
               query = match.group(1).strip()
               url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
               open_url(url, f"{query} on Spotify")
               return


       # For Netflix searches
       if "on netflix" in cmd.lower():
           match = re.search(r"(?:open|search|play|watch)?\s*(.+?)\s+on\s+netflix", cmd.lower())
           if match:
               query = match.group(1).strip()
               url = f"https://www.netflix.com/search?q={query.replace(' ', '%20')}"
               open_url(url, f"{query} on Netflix")
               return


       # For Amazon searches
       if "on amazon" in cmd.lower():
           match = re.search(r"(?:open|search|find|buy)?\s*(.+?)\s+on\s+amazon", cmd.lower())
           if match:
               query = match.group(1).strip()
               url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
               open_url(url, f"{query} on Amazon")
               return


       # For Twitter/X searches
       if any(s in cmd.lower() for s in ["on twitter", "on x"]):
           pattern = r"(?:open|search|find)?\s*(.+?)\s+on\s+(?:twitter|x)"
           match = re.search(pattern, cmd.lower())
           if match:
               query = match.group(1).strip()
               url = f"https://twitter.com/search?q={query.replace(' ', '%20')}"
               open_url(url, f"{query} on Twitter")
               return


       # For Facebook searches or profiles
       if "on facebook" in cmd.lower():
           match = re.search(r"(?:open|search|find)?\s*(.+?)\s+on\s+facebook", cmd.lower())
           if match:
               query = match.group(1).strip()
               url = f"https://www.facebook.com/search/top/?q={query.replace(' ', '%20')}"
               open_url(url, f"{query} on Facebook")
               return


       # For Instagram profiles or hashtags
       if "on instagram" in cmd.lower():
           match = re.search(r"(?:open|search|find)?\s*(.+?)\s+on\s+instagram", cmd.lower())
           if match:
               query = match.group(1).strip()
               # Check if it's a username (without spaces)
               if " " not in query:
                   url = f"https://www.instagram.com/{query}"
                   open_url(url, f"{query}'s Instagram")
               else:
                   # Assume it's a search or hashtag
                   url = f"https://www.instagram.com/explore/tags/{query.replace(' ', '')}"
                   open_url(url, f"#{query} on Instagram")
               return


       # For Google Maps searches
       if any(s in cmd.lower() for s in ["on maps", "on google maps", "directions to"]):
           if "directions to" in cmd.lower():
               match = re.search(r"directions to\s+(.+?)(?:\s+from\s+(.+))?$", cmd.lower())
               if match:
                   destination = match.group(1).strip()
                   origin = match.group(2).strip() if match.group(2) else ""
                   if origin:
                       url = f"https://www.google.com/maps/dir/{origin.replace(' ', '+')}/{destination.replace(' ', '+')}"
                       open_url(url, f"Directions from {origin} to {destination}")
                   else:
                       url = f"https://www.google.com/maps/dir//{destination.replace(' ', '+')}"
                       open_url(url, f"Directions to {destination}")
               return
           else:
               match = re.search(r"(?:find|search|locate|show)?\s*(.+?)\s+on\s+(?:maps|google maps)", cmd.lower())
               if match:
                   location = match.group(1).strip()
                   url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
                   open_url(url, f"{location} on Maps")
                   return


       # For news searches
       if any(s in cmd.lower() for s in ["news about", "latest news on"]):
           match = re.search(r"(?:news about|latest news on)\s+(.+)", cmd.lower())
           if match:
               topic = match.group(1).strip()
               url = f"https://news.google.com/search?q={topic.replace(' ', '+')}"
               open_url(url, f"News about {topic}")
               return


       # For quick access to your email
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
           open_url(url, "Email")
           return


       # For opening streaming services
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
               open_url(url, service.title())
               return


       # Close/end/quit commands
       if "close" in cmd.lower() or "end" in cmd.lower() or "quit" in cmd.lower():
           # Extract what to close
           match = re.search(r"(?:close|end|quit)\s+(.+?)$", cmd.lower())
           if match:
               app_name = match.group(1).strip()


               # Try to close the specified app
               close_app(app_name.title())
               return
           else:
               # If no app specified, ask what to close
               say("What would you like me to close?", speed=190)
               time.sleep(0.5)
               response = take_command()
               if response:
                   close_app(response.title())
               return


       # Open commands
       if "open" in cmd.lower():
           # Extract what to open
           match = re.search(r"open\s+(.+?)(?:\s+on\s+google)?$", cmd.lower())
           if match:
               target = match.group(1).strip()


               # Check if it should be opened on Google
               if " on google" in cmd.lower():
                   url = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                   open_url(url, f"{target} on Google")
                   return


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
                   "google maps": "https://maps.google.com",
                   "apple maps": "maps://"
               }


               # Check for websites first
               for site, url in website_mapping.items():
                   if site in target.lower():
                       open_url(url, site.title())
                       return


               # macOS system apps
               system_apps = {
                   # Productivity & Office
                   "mail": "Mail",
                   "calendar": "Calendar",
                   "contacts": "Contacts",
                   "notes": "Notes",
                   "reminders": "Reminders",
                   "messages": "Messages",
                   "facetime": "FaceTime",
                   "siri": "Siri",
                   "finder": "Finder",
                   "system settings": "System Settings",
                   "system preferences": "System Preferences",
                   "app store": "App Store",
                   "terminal": "Terminal",
                   "safari": "Safari",
                   "photos": "Photos",
                   "preview": "Preview",
                   "calculator": "Calculator",
                   "maps": "Maps",
                   "keychain": "Keychain Access",
                   "activity monitor": "Activity Monitor",
                   "disk utility": "Disk Utility",
                   "screenshot": "Screenshot",
                   "voice memos": "Voice Memos",
                   "books": "Books",
                   "stocks": "Stocks",
                   "news": "News",
                   "podcasts": "Podcasts",
                   "music": "Music",
                   "tv": "TV",
                   "automator": "Automator",
                   "quicktime": "QuickTime Player",
                   "stickies": "Stickies",
                   "font book": "Font Book",
                   "dictionary": "Dictionary",
                   "home": "Home",
                   "time machine": "Time Machine",
                   "text edit": "TextEdit",


                   # Apple Creative Apps
                   "final cut": "Final Cut Pro",
                   "final cut pro": "Final Cut Pro",
                   "logic": "Logic Pro",
                   "logic pro": "Logic Pro",
                   "garageband": "GarageBand",
                   "imovie": "iMovie",
                   "keynote": "Keynote",
                   "pages": "Pages",
                   "numbers": "Numbers"
               }


               # Check for macOS system apps
               for keyword, app_name in system_apps.items():
                   if keyword in target.lower():
                       open_app(app_name)
                       return


               # Common third-party apps by category
               third_party_apps = {
                   # Browsers
                   "chrome": "Google Chrome",
                   "google chrome": "Google Chrome",
                   "firefox": "Firefox",
                   "brave": "Brave Browser",
                   "edge": "Microsoft Edge",
                   "opera": "Opera",
                   "tor": "Tor Browser",
                   "vivaldi": "Vivaldi",


                   # Productivity & Office
                   "word": "Microsoft Word",
                   "excel": "Microsoft Excel",
                   "powerpoint": "Microsoft PowerPoint",
                   "outlook": "Microsoft Outlook",
                   "teams": "Microsoft Teams",
                   "onenote": "Microsoft OneNote",
                   "notion": "Notion",
                   "obsidian": "Obsidian",
                   "evernote": "Evernote",
                   "todoist": "Todoist",
                   "things": "Things",
                   "bear": "Bear",
                   "agenda": "Agenda",
                   "airmail": "Airmail",
                   "spark": "Spark",
                   "fantastical": "Fantastical",
                   "omnifocus": "OmniFocus",
                   "google docs": "Google Docs",
                   "google sheets": "Google Sheets",
                   "google drive": "Google Drive",
                   "dropbox": "Dropbox",
                   "box": "Box",
                   "onedrive": "OneDrive",
                   "trello": "Trello",
                   "asana": "Asana",
                   "jira": "Jira",
                   "wunderlist": "Wunderlist",
                   "anydo": "Any.do",
                   "alfred": "Alfred",
                   "raycast": "Raycast",
                   "bitwarden": "Bitwarden",
                   "1password": "1Password",
                   "lastpass": "LastPass",
                   "dashlane": "Dashlane",
                   "zoom": "Zoom",
                   "skype": "Skype",
                   "slack": "Slack",
                   "discord": "Discord",
                   "telegram": "Telegram",
                   "whatsapp": "WhatsApp",
                   "signal": "Signal",
                   "messenger": "Messenger",


                   # Development
                   "vscode": "Visual Studio Code",
                   "vs code": "Visual Studio Code",
                   "visual studio code": "Visual Studio Code",
                   "xcode": "Xcode",
                   "intellij": "IntelliJ IDEA",
                   "webstorm": "WebStorm",
                   "pycharm": "PyCharm",
                   "android studio": "Android Studio",
                   "eclipse": "Eclipse",
                   "netbeans": "NetBeans",
                   "sublime text": "Sublime Text",
                   "atom": "Atom",
                   "vim": "MacVim",
                   "emacs": "Emacs",
                   "iterm": "iTerm",
                   "terminal": "Terminal",
                   "sourcetree": "Sourcetree",
                   "github desktop": "GitHub Desktop",
                   "postman": "Postman",
                   "docker": "Docker",
                   "insomnia": "Insomnia",


                   # Design & Creative
                   "photoshop": "Adobe Photoshop",
                   "illustrator": "Adobe Illustrator",
                   "indesign": "Adobe InDesign",
                   "lightroom": "Adobe Lightroom",
                   "premiere": "Adobe Premiere Pro",
                   "premiere pro": "Adobe Premiere Pro",
                   "after effects": "Adobe After Effects",
                   "xd": "Adobe XD",
                   "figma": "Figma",
                   "sketch": "Sketch",
                   "affinity photo": "Affinity Photo",
                   "affinity designer": "Affinity Designer",
                   "affinity publisher": "Affinity Publisher",
                   "procreate": "Procreate",
                   "blender": "Blender",
                   "cinema 4d": "Cinema 4D",
                   "maya": "Maya",
                   "zbrush": "ZBrush",
                   "audacity": "Audacity",
                   "ableton": "Ableton Live",
                   "fl studio": "FL Studio",
                   "pro tools": "Pro Tools",
                   "davinci resolve": "DaVinci Resolve",
                   "capture one": "Capture One",


                   # Utilities
                   "cleanmymac": "CleanMyMac X",
                   "bartender": "Bartender",
                   "magnet": "Magnet",
                   "rectangle": "Rectangle",
                   "bettertouchtool": "BetterTouchTool",
                   "hazel": "Hazel",
                   "little snitch": "Little Snitch",
                   "amphetamine": "Amphetamine",
                   "caffeine": "Caffeine",
                   "keka": "Keka",
                   "the unarchiver": "The Unarchiver",
                   "airbuddy": "AirBuddy",
                   "handbrake": "HandBrake",
                   "vlc": "VLC",
                   "iina": "IINA",
                   "spotify": "Spotify",
                   "tunnelblack": "TunnelBear",
                   "nordvpn": "NordVPN",
                   "surfshark": "Surfshark",
                   "expressvpn": "ExpressVPN",
                   "adguard": "AdGuard",


                   # Games
                   "steam": "Steam",
                   "epic games": "Epic Games Launcher",
                   "battle.net": "Battle.net",
                   "origin": "Origin",
                   "uplay": "Ubisoft Connect",
                   "gog galaxy": "GOG Galaxy",
                   "minecraft": "Minecraft"
               }


               # Check for third-party apps
               for keyword, app_name in third_party_apps.items():
                   if keyword in target.lower():
                       open_app(app_name)
                       return


               # If no specific app was matched, try to open with the given name
               open_app(target.title())
               return






       # Time
       if "time" in cmd.lower() and any(word in cmd.lower() for word in ["what", "current", "right now"]):
           current_time = datetime.datetime.now().strftime('%I:%M %p')
           say(f"It's {current_time}", speed=190)
           return


       # Date
       if "date" in cmd.lower() and any(word in cmd.lower() for word in ["what", "today", "current"]):
           current_date = datetime.datetime.today().strftime('%B %d, %Y')
           say(f"Today is {current_date}", speed=190)
           return


       # Set reminders
       if "set" in cmd.lower() and "reminder" in cmd.lower():
           # Extract time if specified
           time_match = re.search(r"(?:at|for)\s+(\d{1,2}:?\d{0,2})", cmd.lower())
           if time_match:
               time_str = time_match.group(1)
               say(f"Reminder set for {time_str}", speed=190)
           else:
               say("What's the reminder?", speed=190)
           return


       # Reminder details (when no specific command)
       if session_memory.get("waiting_for_reminder"):
           # Handle reminder detail
           say(f"Reminder set: {cmd}", speed=190)
           session_memory["waiting_for_reminder"] = False
           return


       # Close/end commands
       if "close" in cmd.lower() or "end" in cmd.lower():
           say("Ended", speed=190)
           return


       # Quick responses
       if cmd.lower() in ["hello", "hi", "hey"]:
           say("Hi there! How can I help?", speed=190)
           return


       if any(phrase in cmd.lower() for phrase in ["how are you", "how's it going", "what's up"]):
           say("I'm doing great! What about you?", speed=190)
           return






       # Default to AI for everything else
       ai_fallback(cmd)


   except Exception as e:
       print(f"Command processing error: {e}")
       say("Sorry, I had an error processing that", speed=190)





# ---------------- FastAPI API layer ----------------
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/ask")
async def ask(q: Query):
    """Endpoint to receive text commands and run process_command."""
    process_command(q.text)
    return {"status": "executed"}


if __name__ == "__main__":
    import sys
    import uvicorn

    # Decide run mode based on first CLI arg
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # ---------------- Terminal assistant mode ----------------
        try:
            # Create and play startup sound
            try:
                play_startup_sound1()
            except Exception:
                pass

            say("Hello, I'm Ballsy. Your Personal Virtual Assistant.", speed=VOICE_SPEED)
            say("Please be silent for sound calibration", speed=VOICE_SPEED)
            calibrate_microphone()
            play_startup_sound()
            say("How can I help you?", speed=VOICE_SPEED)

            print("\n💡 READY: Speak naturally - I'll respond appropriately\n")

            while True:
                c = take_command()
                if c:
                    process_command(c)
                else:
                    print("🔄 Listening...")
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            say("Goodbye!", speed=VOICE_SPEED)
            exit(0)
        except Exception as e:
            print(f"Fatal error: {e}")
            exit(1)
    else:
        # ---------------- FastAPI server mode ----------------
        uvicorn.run(app, host="127.0.0.1", port=5234)
