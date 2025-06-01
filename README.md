````markdown
# 🎤 Ballsy - AI Voice Assistant

**Ballsy** is a full-stack Python-based voice assistant with a beautiful Siri-like UI. Built with a FastAPI backend and a modern web frontend, Ballsy provides intelligent voice interactions powered by Mistral AI.

![Ballsy Voice Assistant]https://img.shields.io/badge/Voice%20Assistant-Ballsy-blue?style=for-the-badge&logo=microphone
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow?style=flat-square&logo=javascript)

---

## 🔗 Live Demo

👉 [Try Ballsy Online!](https://ballsy.onrender.com)  

---

## ✨ Features

### 🎯 Core Capabilities
- **🎙️ Voice Recognition** – Real-time speech-to-text using browser APIs  
- **🔊 Voice Synthesis** – Natural text-to-speech responses  
- **🤖 AI Integration** – Powered by Mistral AI for intelligent conversations  
- **🧮 Math Calculator** – Built-in mathematical expression evaluation  
- **⏰ Time & Date** – Current time and date information  
- **🌐 Web Integration** – Open websites and search the internet  

### 🚀 Advanced Features
- **📱 App Control** – Open and manage applications (macOS support)  
- **🎵 Streaming Services** – Quick access to Netflix, Spotify, YouTube, etc.  
- **🗺️ Maps & Directions** – Google Maps integration for navigation  
- **📰 News Search** – Latest news on any topic  
- **📧 Email Access** – Quick access to Gmail, Outlook, Yahoo Mail  
- **🎯 Smart Search** – Intelligent web searches with contextual results  

### 💫 User Experience
- **🎨 Siri-like UI** – Beautiful, animated voice orb interface  
- **🌓 Dark/Light Themes** – Customizable appearance  
- **📱 Responsive Design** – Works on desktop and mobile  
- **💬 Conversation History** – Persistent chat memory  
- **⚙️ Customizable Settings** – Voice, speed, and theme preferences  

---

## 🏗️ Architecture

### Backend (FastAPI)
- **🐍 Python 3.8+** with FastAPI framework  
- **🤖 Mistral AI** integration for natural language processing  
- **🎙️ Speech Recognition** using Google Speech API (via `speech_recognition`)  
- **💾 SQLite Database** for conversation history and settings  
- **🔌 WebSocket Support** for real-time communication  
- **📡 RESTful API** endpoints for all functionality  

### Frontend (Modern Web)
- **🌐 HTML5/CSS3/JavaScript** with modern ES6+ features  
- **🎨 CSS Animations** for smooth, Siri-like transitions  
- **🎙️ Web Speech API** for browser-based voice recognition  
- **🔊 Speech Synthesis API** for text-to-speech  
- **📱 Responsive Design** using CSS Grid and Flexbox  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher  
- Modern web browser (Chrome, Firefox, Edge, Safari)  
- Microphone access  
- Internet connection  

### Local Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/ethicalzeus07/ballsy-voice-assistant.git
   cd ballsy-voice-assistant
````

2. **Create and activate a Python virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate           # macOS/Linux
   # OR venv\Scripts\activate          # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install .
   ```

4. **Set your Mistral API key**
   Create a file named `.env` in the project root with the following line:

   ```
   MISTRAL_API_KEY=your_actual_mistral_api_key_here
   ```

5. **Run Ballsy locally**

   ```bash
   python run.py
   ```

   * Open your browser at [http://localhost:8000](http://localhost:8000).
   * Speak or type a command (e.g., “Hello”) and watch Ballsy reply!

---

## 🎯 Usage

### Voice Commands

Ballsy responds to natural language. Try these commands:

#### 🗣️ Basic Interaction

* **"Hello"** → Greeting and introduction
* **"What's your name?"** → Ballsy introduces itself
* **"How are you?"** → Status response
* **"Goodbye"** → Farewell message

#### 🧮 Mathematics

* **"What's 25 plus 17?"** → Mathematical calculations
* **"Calculate 144 divided by 12"** → Advanced math
* **"What's 15 percent of 200?"** → Percentage calculations

#### ⏰ Time & Information

* **"What time is it?"** → Current time
* **"What's today's date?"** → Current date

#### 🌐 Web & Search

* **"Search for electric cars"** → Google search
* **"Who is Elon Musk?"** → AI-powered information
* **"What is machine learning?"** → Intelligent explanations

#### 🎵 Entertainment & Apps

* **"Open YouTube"** → Launch YouTube
* **"Find Stranger Things on Netflix"** → Search Netflix
* **"Play Taylor Swift on Spotify"** → Open Spotify search
* **"Open Chrome"** → Launch Google Chrome

#### 🗺️ Navigation & Location

* **"Directions to Central Park"** → Google Maps directions
* **"Find coffee shops near me"** → Location-based search
* **"Show me Paris on maps"** → Maps location search

#### 📰 News & Information

* **"Latest news on climate change"** → Current news search
* **"What's happening in technology?"** → Tech news

### 💻 Text Input Alternative

* Click the keyboard icon in the UI to toggle text input mode. Type your command and press Enter.

---

## ⚙️ Configuration

### Settings Panel

Access via the gear icon in the UI. Available settings:

* **🎙️ Voice Selection** – Choose from system voices (e.g., “Daniel,” “Samantha”).
* **⚡ Speech Rate** – Adjust speaking speed (120–250 WPM).
* **🎨 Theme** – Light, Dark, or System default.
* **🎨 Accent Colors** – Blue, Purple, Green, Orange.
* **🎙️ Microphone Sensitivity** – Adjust voice detection threshold.
* **🔄 Auto-listen** – Automatically listen after responses.

### Environment Variables

* The `.env` file in the project root should contain your Mistral API key:

  ```env
  MISTRAL_API_KEY=your_actual_mistral_api_key_here
  ```

---

## 📁 Project Structure

```
ballsy-voice-assistant/
├── README.md
├── run.py                         # Entrypoint for local and Render deployment
├── pyproject.toml                 # Python project configuration and dependencies
├── LICENSE                        # MIT License
├── .env                           # Environment variables (Mistral API key)
├── docs/                          # Optional: screenshots or additional docs
│   ├── screenshot-ballsy1.png
│   └── screenshot-ballsy2.png
└── src/
    ├── backend/
    │   └── app.py                 # FastAPI backend (serves API + frontend)
    └── frontend/
        ├── templates/
        │   └── index.html         # Main UI template
        └── static/
            ├── css/
            │   └── styles.css      # Siri-like UI styling
            └── js/
                ├── app.js          # Main application logic
                ├── ui.js           # UI interactions
                └── voice.js        # Voice processing
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test.py
```

Tests include:

* ✅ Backend API functionality
* ✅ Command processing accuracy
* ✅ AI response quality
* ✅ Mathematical calculations
* ✅ Settings management
* ✅ WebSocket communication

---

## 🛠️ Development

### Adding New Commands

1. Edit the `CommandProcessor` class in `src/backend/app.py`.
2. Add or modify command patterns within `process_command()` to handle new phrases.

### Extending AI Capabilities

* Edit the `SYSTEM_PROMPT` constant at the top of `src/backend/app.py` to adjust Ballsy’s personality or instructions.

### Custom Integrations

* Add new service integrations (e.g., additional URLs or actions) in the command processor’s handler section.

---

## 🔧 Troubleshooting

### Common Issues

**🎙️ Microphone not working**

* Ensure the browser has microphone permissions.
* Check that no other application is using the microphone.
* Refresh the page if needed.

**🤖 Voice recognition not accurate**

* Speak clearly at a moderate pace.
* Reduce background noise.
* Adjust the microphone sensitivity slider in settings.

**🔧 Backend server won't start**

* Confirm all dependencies are installed: `pip install .`
* Verify that port 8000 is free.
* Inspect console logs for error messages.

**🌐 Frontend not connecting**

* Ensure the backend server is running (`python run.py`).
* Check the browser console (F12) for errors.
* Make sure you’re visiting [http://localhost:8000](http://localhost:8000).

**🚪 Port 5000/5001 conflicts (macOS)**

* If you previously used `--frontend-port 5001`, no longer needed—FastAPI now serves everything on 8000.
* To use a different port locally, set `PORT` environment variable before running:

  ```bash
  export PORT=8080
  python run.py
  ```

### 📋 System Requirements

* **Python:** 3.8 or higher
* **Browser:** Chrome 60+, Firefox 55+, Safari 14+, Edge 79+
* **RAM:** Minimum 2GB available
* **Storage:** 100MB free space
* **Network:** Internet connection for AI features

---

## 🤝 Contributing

We welcome contributions! To get started:

1. **Fork** the repository.
2. **Create** a feature branch:

   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes:

   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push** to your branch:

   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request on GitHub.

### Development Setup

```bash
# Clone your fork
git clone https://github.com/ethicalzeus07/ballsy-voice-assistant.git

# Create virtual environment
python3 -m venv ballsy-env
source ballsy-env/bin/activate  # macOS/Linux
# OR ballsy-env\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python test.py
```



## ⭐️ Acknowledgments

* **🤖 Mistral AI** – For providing the AI language model
* **🎙️ Google Speech API** – For speech recognition capabilities
* **🎨 Font Awesome** – For beautiful icons
* **🌐 FastAPI** – For the excellent web framework
* **💻 Web Speech API** – For browser-based voice capabilities

---

**⭐ If you like Ballsy, please give us a star on GitHub! ⭐**

*Built with ❤️ and lots of ☕*

```
```
