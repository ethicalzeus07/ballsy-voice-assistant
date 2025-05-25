# 🎤 Ballsy - AI Voice Assistant

**Ballsy** is a full-stack Python-based voice assistant with a beautiful Siri-like UI. Built with FastAPI backend and modern web frontend, Ballsy provides intelligent voice interactions powered by Mistral AI.

![Ballsy Voice Assistant](https://img.shields.io/badge/Voice%20Assistant-Ballsy-blue?style=for-the-badge&logo=microphone)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow?style=flat-square&logo=javascript)

## ✨ Features

### 🎯 Core Capabilities
- **🎙️ Voice Recognition** - Real-time speech-to-text using browser APIs
- **🔊 Voice Synthesis** - Natural text-to-speech responses
- **🤖 AI Integration** - Powered by Mistral AI for intelligent conversations
- **🧮 Math Calculator** - Built-in mathematical expression evaluation
- **⏰ Time & Date** - Current time and date information
- **🌐 Web Integration** - Open websites and search the internet

### 🚀 Advanced Features
- **📱 App Control** - Open and manage applications (macOS support)
- **🎵 Streaming Services** - Quick access to Netflix, Spotify, YouTube, etc.
- **🗺️ Maps & Directions** - Google Maps integration for navigation
- **📰 News Search** - Latest news on any topic
- **📧 Email Access** - Quick access to Gmail, Outlook, Yahoo Mail
- **🎯 Smart Search** - Intelligent web searches with contextual results

### 💫 User Experience
- **🎨 Siri-like UI** - Beautiful, animated voice orb interface
- **🌓 Dark/Light Themes** - Customizable appearance
- **📱 Responsive Design** - Works on desktop and mobile
- **💬 Conversation History** - Persistent chat memory
- **⚙️ Customizable Settings** - Voice, speed, and theme preferences

## 🏗️ Architecture

### Backend (FastAPI)
- **🐍 Python 3.8+** with FastAPI framework
- **🤖 Mistral AI** integration for natural language processing
- **🎙️ Speech Recognition** using Google Speech API
- **💾 SQLite Database** for conversation history and settings
- **🔌 WebSocket Support** for real-time communication
- **📡 RESTful API** endpoints for all functionality

### Frontend (Modern Web)
- **🌐 HTML5/CSS3/JavaScript** with modern ES6+ features
- **🎨 CSS Animations** for smooth, Siri-like transitions
- **🎙️ Web Speech API** for browser-based voice recognition
- **🔊 Speech Synthesis API** for text-to-speech
- **📱 Responsive Design** using CSS Grid and Flexbox

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Microphone access
- Internet connection

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ethicalzeus07/ballsy-voice-assistant.git
cd ballsy-voice-assistant
```

2. **Run Ballsy** (One command setup)
```bash
python3 run.py --frontend-port 5001
```

That's it! Ballsy will:
- ✅ Install all dependencies automatically
- ✅ Start backend server on port 8000
- ✅ Start frontend server on port 5001 (avoiding macOS AirPlay conflicts)
- ✅ Open your browser to the voice assistant
- ✅ Be ready for voice commands!

### Alternative Manual Setup

If you prefer manual setup:

1. **Install dependencies**
```bash
pip install fastapi uvicorn flask python-dotenv mistralai SpeechRecognition pydantic python-multipart websockets jinja2
```

2. **Start backend server**
```bash
cd src/backend
python app.py
```

3. **Start frontend server** (in new terminal)
```bash
cd src/frontend
python -m http.server 5000
```

4. **Open browser** to `http://localhost:5001`

## 🎯 Usage

### Voice Commands

Ballsy responds to natural language. Try these commands:

#### 🗣️ Basic Interaction
- *"Hello"* → Greeting and introduction
- *"What's your name?"* → Ballsy introduces itself
- *"How are you?"* → Status response
- *"Goodbye"* → Farewell message

#### 🧮 Mathematics
- *"What's 25 plus 17?"* → Mathematical calculations
- *"Calculate 144 divided by 12"* → Advanced math
- *"What's 15 percent of 200?"* → Percentage calculations

#### ⏰ Time & Information
- *"What time is it?"* → Current time
- *"What's today's date?"* → Current date

#### 🌐 Web & Search
- *"Search for electric cars"* → Google search
- *"Who is Elon Musk?"* → AI-powered information
- *"What is machine learning?"* → Intelligent explanations

#### 🎵 Entertainment & Apps
- *"Open YouTube"* → Launch YouTube
- *"Find Stranger Things on Netflix"* → Search Netflix
- *"Play Taylor Swift on Spotify"* → Open Spotify search
- *"Open Chrome"* → Launch Google Chrome

#### 🗺️ Navigation & Location
- *"Directions to Central Park"* → Google Maps directions
- *"Find coffee shops near me"* → Location-based search
- *"Show me Paris on maps"* → Maps location search

#### 📰 News & Information
- *"Latest news on climate change"* → Current news search
- *"What's happening in technology?"* → Tech news

### 💻 Text Input Alternative

Don't want to use voice? Click the keyboard icon for text input!

## ⚙️ Configuration

### Settings Panel
Access via the gear icon:
- **🎙️ Voice Selection** - Choose from available system voices
- **⚡ Speech Rate** - Adjust speaking speed (120-250 WPM)
- **🎨 Theme** - Light, Dark, or System default
- **🎨 Accent Colors** - Blue, Purple, Green, Orange
- **🎙️ Microphone Sensitivity** - Adjust voice detection
- **🔄 Auto-listen** - Automatically listen after responses

### Environment Variables
Create `.env` file for configuration:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

## 📁 Project Structure

```
ballsy-voice-assistant/
├── 📄 README.md                    # This file
├── 🚀 run.py                      # Main launcher script
├── 🧪 test.py                     # Test suite
├── 📝 .env                        # Environment variables
├── 📚 docs/                       # Documentation
│   ├── architecture_design.md     # Architecture overview
│   ├── user_guide.md             # Detailed user guide
│   └── todo.md                   # Development roadmap
├── 🔧 src/                        # Source code
│   ├── backend/                  # FastAPI backend
│   │   └── app.py               # Main backend application
│   └── frontend/                # Web frontend
│       ├── templates/           # HTML templates
│       │   └── index.html      # Main UI template
│       └── static/             # Static assets
│           ├── css/
│           │   └── styles.css  # Siri-like UI styling
│           └── js/
│               ├── app.js      # Main application logic
│               ├── ui.js       # UI interactions
│               └── voice.js    # Voice processing
└── 📊 static/                    # Additional static files
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test.py
```

Tests include:
- ✅ Backend API functionality
- ✅ Command processing accuracy
- ✅ AI response quality
- ✅ Mathematical calculations
- ✅ Settings management
- ✅ WebSocket communication

## 🛠️ Development

### Adding New Commands

1. **Backend**: Add command patterns in `src/backend/app.py` → `CommandProcessor.process_command()`
2. **Frontend**: Voice commands are automatically processed through speech recognition

### Extending AI Capabilities

Modify the `SYSTEM_PROMPT` in `app.py` to change Ballsy's personality or capabilities.

### Custom Integrations

Add new service integrations in the command processor's URL handlers section.

## 🔧 Troubleshooting

### Common Issues

**🎙️ Microphone not working**
- Ensure browser has microphone permissions
- Check no other app is using the microphone
- Try refreshing the page

**🤖 Voice recognition not accurate**
- Speak clearly at moderate pace
- Reduce background noise
- Adjust microphone sensitivity in settings

**🔧 Backend server won't start**
- Check all dependencies are installed: `pip install -r requirements.txt`
- Ensure port 8000 is available
- Check console for error messages

**🌐 Frontend not connecting**
- Verify both servers are running
- Check browser console (F12) for errors
- Try using port 5001: `python3 run.py --frontend-port 5001`
- On macOS, port 5000 might conflict with AirPlay Receiver

**🚪 Port 5000 already in use (macOS)**
- Use the recommended command: `python3 run.py --frontend-port 5001`
- Or disable AirPlay Receiver: System Preferences → General → AirDrop & Handoff
- Alternative ports: `--frontend-port 8080` or `--frontend-port 3000`

### 📋 System Requirements

- **Python**: 3.8 or higher
- **Browser**: Chrome 60+, Firefox 55+, Safari 14+, Edge 79+
- **RAM**: Minimum 2GB available
- **Storage**: 100MB free space
- **Network**: Internet connection for AI features

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/ethicalzeus07/ballsy-voice-assistant.git

# Create virtual environment
python -m venv ballsy-env
source ballsy-env/bin/activate  # On Windows: ballsy-env\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python test.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **🤖 Mistral AI** - For providing the AI language model
- **🎙️ Google Speech API** - For speech recognition capabilities
- **🎨 Font Awesome** - For beautiful icons
- **🌐 FastAPI** - For the excellent web framework
- **💻 Web Speech API** - For browser-based voice capabilities

## 📞 Support

- **📧 Issues**: [GitHub Issues](https://github.com/ethicalzeus07/ballsy-voice-assistant/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/ethicalzeus07/ballsy-voice-assistant/discussions)
- **📖 Wiki**: [Project Wiki](https://github.com/ethicalzeus07/ballsy-voice-assistant/wiki)

## 🚀 What's Next?

Check out our [development roadmap](docs/todo.md) for upcoming features:
- 🌍 Multi-language support
- 📱 Mobile app versions
- 🏠 Smart home integration
- 🔌 Plugin system
- ☁️ Cloud deployment options

---

**⭐ If you like Ballsy, please give us a star on GitHub! ⭐**

*Built with ❤️ and lots of ☕*