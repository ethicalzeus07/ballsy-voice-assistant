### 🎤 Ballsy Voice Assistant

Full‑stack AI voice assistant with a Siri‑like UI, powered by Mistral AI. Speak or type, get smart answers, open sites, and more — with a slick animated interface.

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![Mistral AI](https://img.shields.io/badge/Mistral%20AI-enabled-6f42c1)

![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?logo=git)
![Made with Love](https://img.shields.io/badge/made%20with-❤️-ff69b4)

### ✨ Features

- **Voice recognition**: One‑shot browser speech recognition with real‑time UI states
- **AI answers**: Mistral AI for concise, context‑aware responses
- **Smart commands**: Search the web, open services (YouTube, Netflix, Spotify), maps/directions, news
- **Math**: Inline calculations and chained operations (e.g., + 10)
- **WebSocket + REST**: Real‑time updates and HTTP fallbacks
- **Siri‑like UI**: Animated orb, typing indicator, dark mode

### 🚀 Quick start

Prerequisites:
- Python 3.8+
- Microphone access + Internet
- `MISTRAL_API_KEY`

1) Clone and enter the project
```bash
git clone <your_repo_url>
cd ballsy-voice-assistant-main
```

2) Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3) Install dependencies
```bash
pip install -U fastapi uvicorn[standard] flask python-dotenv mistralai SpeechRecognition pydantic python-multipart websockets jinja2
```

4) Configure your API key
```bash
echo "MISTRAL_API_KEY=your_mistral_api_key_here" > .env
```

5) Run the app
```bash
python run.py
# then open http://localhost:8000
```

Dev reload (alternative):
```bash
uvicorn src.backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### 🏗️ Architecture overview

- **Backend (FastAPI)**: REST + WebSocket, SQLite persistence (`voice_assistant.db`), Mistral AI integration
- **Frontend (HTML/CSS/JS)**: Served by FastAPI; animated orb, chat history, dark mode
- **Key files**:
  - `src/backend/app.py` — API, WebSocket, command engine, DB
  - `src/frontend/templates/index.html` — main UI
  - `src/frontend/static/js/{voice.js, app.js, ui.js}` — voice, app logic, UI events

### 🎮 Using Ballsy

- Click the orb to start/stop listening, or type in the input
- Examples:
  - “Who is Marie Curie?”
  - “5 + 10” then “+ 3”
  - “Open YouTube” / “Play Interstellar soundtrack on Spotify”
  - “Directions to Central Park” / “Find cafes on Maps”

Note: As a web app, native desktop apps cannot be opened; links open in your browser.

### 🔌 API

- `POST /api/command` — process text commands
- `POST /api/voice` — process uploaded audio (WAV)
- `GET /api/settings/{user_id}` — read settings
- `PUT /api/settings/{user_id}` — update settings
- `GET /api/history/{user_id}?limit=10` — recent command history
- `WS /ws/voice/{client_id}` — real‑time command channel

Env vars:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
# Optional
HOST=0.0.0.0
PORT=8000
```

### 🧪 Testing (manual)

- Verify mic permissions and speak a few commands
- Try math, search, maps, and media commands
- Toggle dark mode; check WebSocket live responses

### 🐳 Docker (optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -U fastapi uvicorn[standard] flask python-dotenv mistralai SpeechRecognition pydantic python-multipart websockets jinja2
EXPOSE 8000
ENV PORT=8000
CMD ["python", "run.py"]
```

### 🔒 Security & notes

- Keep `MISTRAL_API_KEY` in `.env` or your platform’s secrets
- SQLite file is local; do not commit it
- CORS is open by default for local/dev; restrict in production

### 🙏 Credits

- Mistral AI, FastAPI, SpeechRecognition, Jinja2, and the open‑source community

### 🧩 Sticker board

Add some flair to your issues/PRs and screenshots:

- Core vibe: 🎤🧠✨🚀🌙💬
- UI/voice: 🔊🎛️🟣🔵🟢🟠
- Web/search: 🌐🔎🗺️🧭
- Fun: 🦾🔥🕶️💥

Copy‑paste packs:

- Starter: `🎤 🧠 ✨`
- Power: `🎤 🧠 ✨ 🚀 🌐 🔎`
- Night mode: `🌙 🎤 🟣 💬`

— Made with ❤️ by Pravar Chauhan

Ballsy — your witty, wise AI companion
