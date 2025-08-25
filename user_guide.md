# Voice Assistant with Siri-like UI - User Guide

## Overview

This document provides comprehensive instructions for setting up, running, and using the full-stack Python-based voice assistant with a Siri-like UI. The system combines powerful backend voice processing with an elegant, responsive frontend interface.

## Features

The voice assistant includes the following key features:

- **Voice Recognition**: Real-time speech recognition with automatic silence detection
- **Natural Language Processing**: AI-powered responses using Mistral AI
- **Math Calculations**: Built-in calculator for mathematical expressions
- **Web Integration**: Search and open websites directly from voice commands
- **App Control**: Open and manage applications through voice commands
- **Streaming Services**: Quick access to popular streaming platforms
- **Maps and Directions**: Get directions and location information
- **News and Information**: Access to news and general knowledge
- **Siri-like UI**: Elegant, animated interface with real-time feedback
- **Customization**: Adjustable voice, speed, theme, and sensitivity settings
- **WebSocket Communication**: Real-time bidirectional communication
- **Persistent Memory**: Conversation history and user preferences storage

## System Requirements

- **Python**: Version 3.8 or higher
- **Web Browser**: Chrome, Firefox, Edge, or Safari (latest versions recommended)
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for AI responses and web services
- **Microphone**: Required for voice recognition

## Installation

1. **Clone or extract** the project files to your desired location
2. **Navigate** to the project directory
3. **Install dependencies** by running the setup script:

```bash
python run.py
```

This script will automatically:
- Create the necessary environment file
- Install all required Python packages
- Start both backend and frontend servers
- Open the application in your default web browser

## Manual Setup (Alternative)

If you prefer to set up the components manually:

1. **Install dependencies**:
```bash
pip install fastapi uvicorn flask python-dotenv mistralai SpeechRecognition pydantic python-multipart websockets jinja2
```

2. **Create a `.env` file** in the project root with your Mistral API key:
```
MISTRAL_API_KEY=your_api_key_here
```

3. **Start the backend server**:
```bash
cd src/backend
python app.py
```

4. **Start the frontend server** (in a separate terminal):
```bash
cd src/frontend
flask run
```

5. **Open your browser** and navigate to `http://localhost:5000`

## Usage

### Voice Commands

The voice assistant responds to a wide range of commands, including:

- **General Questions**: "What is the capital of France?", "Who is Albert Einstein?"
- **Math Calculations**: "What's 5 plus 10?", "Calculate 25 divided by 5"
- **Time and Date**: "What time is it?", "What's today's date?"
- **Web Searches**: "Search for electric vehicles", "Look up recipe for chocolate cake"
- **Opening Websites**: "Open YouTube", "Go to Twitter"
- **Streaming Services**: "Find Stranger Things on Netflix", "Play Taylor Swift on Spotify"
- **Maps and Directions**: "Show me directions to Central Park", "Find coffee shops near me"
- **News**: "Get the latest news on climate change", "What's happening in technology"
- **App Control**: "Open Chrome", "Launch Spotify"
- **System Control**: "Close Firefox", "Exit Zoom"

### Using the Interface

1. **Activate Voice Recognition**:
   - Click the central orb or the microphone button
   - The orb will pulse to indicate it's listening
   - Speak your command clearly

2. **Text Input** (alternative to voice):
   - Click the keyboard icon to show the text input field
   - Type your command and press Enter or click the send button

3. **Settings**:
   - Click the gear icon in the top right corner
   - Adjust voice, speed, theme, and other preferences
   - Click "Save Settings" to apply changes

4. **Visual Feedback**:
   - Pulsing orb: Idle state
   - Expanding waves: Listening state
   - Contracting orb: Processing state
   - Fluctuating orb: Speaking state

## Architecture

The system follows a modern full-stack architecture:

### Backend

- **FastAPI Server**: High-performance API endpoints
- **WebSocket Support**: Real-time bidirectional communication
- **Speech Recognition**: Processing voice input
- **AI Integration**: Mistral AI for natural language understanding
- **SQLite Database**: Storing conversation history and settings

### Frontend

- **HTML/CSS/JavaScript**: Modern web technologies
- **Responsive Design**: Works on desktop and mobile devices
- **Web Audio API**: Client-side audio processing
- **Web Speech API**: Text-to-speech capabilities
- **WebSocket Client**: Real-time communication with backend

## Customization

### Voice Settings

You can customize the assistant's voice by:
- Selecting different voices from the available system voices
- Adjusting the speech rate (speed)
- Changing the microphone sensitivity

### Appearance

The UI can be customized with:
- Light or dark theme
- System theme matching
- Different accent colors (blue, purple, green, orange)

### Advanced Configuration

For advanced users, the following files can be modified:

- **Backend Configuration**: `/src/backend/app.py`
- **Frontend Styling**: `/src/frontend/static/css/styles.css`
- **Voice Processing**: `/src/frontend/static/js/voice.js`
- **UI Behavior**: `/src/frontend/static/js/ui.js`

## Troubleshooting

### Common Issues

1. **Microphone not working**:
   - Ensure your browser has microphone permissions
   - Check that no other application is using the microphone
   - Try refreshing the page or restarting the browser

2. **Voice recognition not accurate**:
   - Speak clearly and at a moderate pace
   - Reduce background noise
   - Adjust the microphone sensitivity in settings

3. **Backend server not starting**:
   - Check that all dependencies are installed
   - Ensure no other service is using port 8000
   - Check the console for specific error messages

4. **Frontend not connecting to backend**:
   - Verify both servers are running
   - Check browser console for connection errors
   - Ensure the backend URL is correctly configured

### Logs

- Backend logs are available in the terminal running the backend server
- Frontend logs can be viewed in the browser's developer console (F12)

## Development and Extension

### Adding New Features

The modular architecture makes it easy to extend functionality:

1. **New Commands**: Add new command patterns in the `process_command` function in `app.py`
2. **Additional APIs**: Integrate new external services in the backend
3. **UI Enhancements**: Modify the frontend files to add new visual elements

### Testing

A comprehensive test suite is included:

```bash
python test.py
```

This will run tests for:
- Backend API functionality
- Command processing
- AI response quality
- Math calculations
- Settings and history APIs

## License and Credits

- **License**: MIT License
- **AI Integration**: Powered by Mistral AI
- **Speech Recognition**: Google Speech Recognition API
- **Icons**: Font Awesome

## Support

For questions, issues, or feature requests, please contact the developer or submit an issue on the project repository.

---

Thank you for using the Voice Assistant with Siri-like UI! We hope it enhances your productivity and provides a delightful user experience.
