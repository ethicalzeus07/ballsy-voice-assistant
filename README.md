# Ballsy Voice Assistant

A real-time voice conversation AI assistant with a minimal, beautiful orb interface. Speak naturally, get intelligent responses instantly. Powered by NVIDIA NIM, deployed on Render + Vercel, built with FastAPI and vanilla JavaScript.

## 🎤 Live Demo

**Try it now:** [https://ballsy-voice-assistant-main.vercel.app/](https://ballsy-voice-assistant-main.vercel.app/)

Just click the orb and speak. No sign-up required.

## ✨ Features

- **Voice-First Interface** — Click the orb, speak naturally, get AI responses read aloud instantly
- **Real-Time WebSocket** — Low-latency conversation with streaming responses
- **Browser-Based TTS** — Native Web Speech API means no extra dependencies or latency
- **Smart Command Processing** — Understands searches, web queries, math, maps, and natural conversation
- **Minimal, Beautiful UI** — Responsive design with smooth animations and glass morphism
- **Production-Ready** — Deployed on free tier: Render (backend), Vercel (frontend), Neon (database)

## 🏗️ Architecture

```
User (voice/text)
    ↓
Vercel Frontend (vanilla JS + Web Speech)
    ↓
Render FastAPI Backend (REST + WebSocket)
    ↓
NVIDIA NIM LLM (chat completions)
    ↓
Neon Postgres (conversation history)
```

## 🚀 Quick Start (Local Development)

### 1. Setup Python environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```

Edit `.env` with your NVIDIA API key:
```env
NVIDIA_API_KEY=your_nvidia_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=mistralai/mistral-nemotron
DATABASE_URL=sqlite:///./voice_assistant.db
```

### 3. Run locally
```bash
python run.py
```

Open browser to `http://localhost:8000` and click the orb to start talking.

## 🔧 Tech Stack

| Layer | Tech |
|-------|------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Web Speech API |
| **Backend** | FastAPI, Python 3.x, SQLAlchemy, Pydantic |
| **AI Model** | NVIDIA NIM (Mistral Nemotron) via OpenAI-compatible API |
| **Database** | PostgreSQL (Neon) in production, SQLite locally |
| **Deployment** | Vercel (frontend), Render (backend), Neon (database) |
| **Real-Time** | WebSocket protocol for streaming responses |

## 📁 Project Structure

```
src/
├── backend/
│   ├── app.py              # FastAPI app, routes, WebSocket, command processing
│   ├── config.py           # Environment configuration
│   ├── database.py         # SQLAlchemy models
│   ├── ai/
│   │   ├── nvidia_client.py    # NVIDIA NIM chat completions
│   │   └── gemini_client.py    # Google Gemini (fallback)
│   └── tts.py              # TTS providers (Google Cloud, Cloudflare)
│
└── frontend/
    ├── templates/
    │   └── index.html      # Main orb UI
    └── static/
        ├── css/styles.css  # Orb styling, responsive layout
        └── js/
            ├── voice.js    # Speech recognition, WebTTS, API
            └── ui.js       # UI utilities

scripts/
├── build_frontend.sh       # Frontend build for Vercel
└── migrate_db.py          # Database migrations

Deployment configs:
├── render.yaml            # Render backend blueprint
├── vercel.json           # Vercel frontend config
└── Dockerfile            # Container image for deployment
```

## 🌐 Production Deployment

### Environment (Render Backend)
```env
ENVIRONMENT=production
NVIDIA_API_KEY=your_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=mistralai/mistral-nemotron
DATABASE_URL=postgresql://user:password@neon-db-url/ballsy?sslmode=require
CORS_ORIGINS=https://your-vercel-domain.vercel.app
ALLOWED_HOSTS=your-render-service.onrender.com
```

### Deployment Guides
- **Backend:** Render web service (see `render.yaml`)
- **Database:** Neon Postgres free tier
- **Frontend:** Vercel (auto-deploy on git push)

For detailed deployment steps, see deployment configuration files in the repo.

## 🔐 Security

- API keys stored in environment variables only (never committed)
- CORS configured for allowed origins
- HTTPS enforced in production
- Database credentials in Neon managed environment

## 📝 License

MIT License - Feel free to use, modify, and deploy for personal or commercial projects.

## 🎯 Notes

- **Active Stack:** NVIDIA NIM for AI, Browser Web Speech for TTS
- **Fallbacks:** Includes Google Gemini and Google Cloud TTS as optional alternatives
- **No Secrets in Repo:** `.env.example` shows required keys but actual values go in environment variables
- **Browser Support:** Works best in Chrome, Edge, Safari (Web Speech API support varies)
