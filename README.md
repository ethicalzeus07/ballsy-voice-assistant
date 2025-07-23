# 🎤 Ballsy Voice Assistant

A full-stack AI voice assistant with a Siri-like UI, powered by Mistral AI. Ballsy combines natural language processing, speech recognition, and intelligent command execution to provide a seamless voice interaction experience.

![Ballsy Voice Assistant](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Mistral AI](https://img.shields.io/badge/Mistral%20AI-0.4+-purple)

## ✨ Features

### 🎯 Core Capabilities
- **Voice Recognition**: Real-time speech-to-text with noise cancellation
- **AI-Powered Responses**: Intelligent conversations using Mistral AI
- **Command Processing**: Execute various commands and actions
- **Math Calculations**: Handle mathematical expressions and calculations
- **Web Integration**: Open websites, search engines, and streaming services
- **App Control**: Launch applications and services

### 🎨 Siri-like UI
- **Animated Voice Orb**: Dynamic visual feedback for voice interactions
- **Real-time Status**: Visual indicators for listening, processing, and responding states
- **Dark/Light Mode**: Toggle between themes for comfortable usage
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Fluid Animations**: Smooth transitions and micro-interactions

### 🔧 Smart Commands
- **Media Services**: "Play [song] on Spotify", "Watch [movie] on Netflix"
- **Web Search**: "Search for [topic] on Google", "Find [location] on Maps"
- **Information Queries**: "Who is [person]", "What is [concept]"
- **Time & Date**: "What time is it", "What's today's date"
- **Math Operations**: "What's 15 + 27", "Calculate 50 * 3"
- **App Launching**: "Open Gmail", "Open YouTube"

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Microphone access
- Internet connection
- Mistral AI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ethicalzeus07/ballsy-voice-assistant
   cd Ballsy_1
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "MISTRAL_API_KEY=your_mistral_api_key_here" > .env
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## 🏗️ Architecture

### Backend (FastAPI)
- **Voice Processing**: Speech recognition with Google Speech-to-Text
- **AI Integration**: Mistral AI for natural language understanding
- **Command Engine**: Intelligent command parsing and execution
- **WebSocket Support**: Real-time communication with frontend
- **Database**: SQLite for conversation history and user settings

### Frontend (HTML/CSS/JavaScript)
- **Siri-like Interface**: Modern, responsive UI with animations
- **Voice Visualization**: Dynamic orb with status indicators
- **Real-time Updates**: WebSocket communication for live feedback
- **Theme Support**: Dark and light mode toggle
- **Mobile Responsive**: Optimized for all device sizes

### Key Components
```
src/
├── backend/
│   └── app.py              # FastAPI application with all endpoints
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css  # Main stylesheet with animations
│   │   └── js/
│   │       ├── app.js      # Main application logic
│   │       ├── ui.js       # UI interactions and animations
│   │       └── voice.js    # Voice processing and WebSocket handling
│   └── templates/
│       └── index.html      # Main HTML template
```

## 🎮 Usage

### Voice Commands

#### Basic Interaction
- **"Hello"** - Greet Ballsy
- **"What's your name?"** - Learn about Ballsy
- **"How are you?"** - Check Ballsy's status

#### Information Queries
- **"Who is [person]?"** - Get information about people
- **"What is [concept]?"** - Learn about topics
- **"Tell me about [subject]"** - Detailed information

#### Math Operations
- **"What's 25 + 15?"** - Basic arithmetic
- **"Calculate 100 * 3"** - Mathematical expressions
- **"+ 10"** - Continue calculations from previous result

#### Media & Entertainment
- **"Play [song] on Spotify"** - Search and open Spotify
- **"Watch [movie] on Netflix"** - Search Netflix
- **"Open YouTube"** - Launch YouTube
- **"Search for [topic] on Google"** - Web search

#### Productivity
- **"Open Gmail"** - Launch email
- **"What time is it?"** - Get current time
- **"What's today's date?"** - Get current date
- **"Open Maps"** - Launch Google Maps

#### Navigation & Search
- **"Find [location] on Maps"** - Search locations
- **"Directions to [place]"** - Get directions
- **"Search for [topic] on [platform]"** - Platform-specific searches

### UI Controls

#### Voice Activation
- **Click the animated orb** to start voice recording
- **Speak your command** clearly into the microphone
- **Wait for processing** and visual feedback
- **Listen to the response** or read the text

#### Manual Input
- **Type commands** in the text input field
- **Press Enter** to submit
- **View responses** in the conversation history

#### Settings
- **Toggle dark/light mode** using the moon/sun button
- **Adjust voice settings** through the API
- **View conversation history** in the chat area

## 🔧 Configuration

### Environment Variables
```bash
# Required
MISTRAL_API_KEY=your_mistral_api_key_here

# Optional
HOST=0.0.0.0
PORT=8000
```

### API Endpoints

#### Voice Processing
- `POST /api/voice` - Process voice commands
- `POST /api/command` - Process text commands
- `WebSocket /ws/voice/{client_id}` - Real-time voice communication

#### User Management
- `GET /api/settings/{user_id}` - Get user settings
- `PUT /api/settings/{user_id}` - Update user settings
- `GET /api/history/{user_id}` - Get command history

### Database Schema
- **Users**: User profiles and authentication
- **Conversations**: Conversation history
- **Messages**: Individual message records
- **Settings**: User preferences
- **Command History**: Executed commands and results

## 🛠️ Development

### Project Structure
```
Ballsy_1/
├── main.py                 # Replit deployment launcher
├── run.py                  # Production deployment entry point
├── pyproject.toml         # Project dependencies and metadata
├── src/
│   ├── backend/
│   │   └── app.py         # FastAPI application
│   └── frontend/
│       ├── static/        # CSS, JS, and assets
│       └── templates/     # HTML templates
├── architecture_design.md # Detailed architecture documentation
├── todo.md               # Development progress tracking
└── user_guide.md         # User documentation
```

### Key Dependencies
- **FastAPI**: High-performance web framework
- **Mistral AI**: Advanced language model integration
- **SpeechRecognition**: Speech-to-text processing
- **WebSockets**: Real-time communication
- **SQLite**: Lightweight database
- **Jinja2**: Template engine

### Development Setup
1. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run in development mode**
   ```bash
   python run.py --reload
   ```

3. **Access API documentation**
   Navigate to `http://localhost:8000/docs` for interactive API docs

## 🚀 Deployment

### Local Development
```bash
python run.py
```

### Production (Render)
```bash
# Deploy to Render with automatic environment variable injection
# The app will use the PORT environment variable set by Render
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["python", "run.py"]
```

## 🧪 Testing

### Manual Testing
1. **Voice Recognition**: Test microphone input and speech recognition
2. **Command Processing**: Verify all command types work correctly
3. **UI Responsiveness**: Test on different screen sizes
4. **Performance**: Monitor response times and resource usage

### Automated Testing
```bash
# Run tests (when implemented)
pytest tests/

# Run linting
flake8 src/

# Run type checking
mypy src/
```

## 🔒 Security

### API Security
- **CORS Configuration**: Configured for cross-origin requests
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Graceful error responses without sensitive data

### Data Protection
- **Environment Variables**: Sensitive data stored in environment variables
- **Database Security**: SQLite with proper connection handling
- **Session Management**: WebSocket connection management

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests if applicable**
5. **Submit a pull request**

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ features and consistent formatting
- **CSS**: Use BEM methodology for class naming
- **Documentation**: Update README and docstrings as needed


## 🙏 Acknowledgments

- **Mistral AI** for providing the language model capabilities
- **Google Speech-to-Text** for speech recognition
- **FastAPI** for the excellent web framework
- **Open source community** for various libraries and tools

## 📞 Support

### Getting Help
- **Documentation**: Check the `user_guide.md` for detailed usage instructions
- **Issues**: Report bugs and feature requests through GitHub Issues
- **Discussions**: Join community discussions for questions and ideas

### Common Issues
1. **Microphone not working**: Check browser permissions and microphone access
2. **API key errors**: Verify your Mistral API key is correctly set in `.env`
3. **Slow responses**: Check internet connection and API service status
4. **UI not loading**: Ensure all static files are properly served

---

**Made with ❤️ by Pravar Chauhan(The real Ballsy!!)**

*Ballsy - Your AI companion that talks like Ryan Reynolds and thinks like Robert Greene*
