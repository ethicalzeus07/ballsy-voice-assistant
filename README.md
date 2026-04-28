# Ballsy Voice Assistant

Ballsy is a full-stack voice assistant with a simple orb UI, fast browser speech input, browser Web Speech text-to-speech, and NVIDIA NIM for AI responses. It is designed to feel conversational, useful, and lightweight enough to deploy with a Render backend and Vercel frontend.

## What It Does

- Voice and text chat through a minimal web interface.
- NVIDIA-hosted model responses through an OpenAI-compatible API.
- Browser WebTTS for natural-ish, fast, no-extra-cost speech output.
- Smart command handling for searches, links, maps, media, math, and normal conversation.
- FastAPI backend with REST and WebSocket support.
- SQLAlchemy database support for local SQLite and production Postgres.
- Production config for Render backend and Vercel frontend.

## Architecture

```mermaid
flowchart LR
  U[User voice or text] --> F[Vercel frontend]
  F -->|REST or WebSocket| B[Render FastAPI backend]
  B --> N[NVIDIA NIM chat completions]
  B --> D[(Postgres in production or SQLite locally)]
  F --> T[Browser Web Speech TTS]
```

## Local Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` from the example and add your NVIDIA key:

```bash
cp .env.example .env
```

Minimum local `.env`:

```env
NVIDIA_API_KEY=your_nvidia_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=mistralai/mistral-nemotron
DATABASE_URL=sqlite:///./voice_assistant.db
USE_CLOUD_TTS=false
USE_CLOUDFLARE_TTS=false
ENABLE_GEMINI_TTS=false
```

Run the app:

```bash
python run.py
```

Then open `http://localhost:8000`.

## Production Deployment

The current free target setup is:

- Backend: Render web service running `uvicorn src.backend.app:app --host 0.0.0.0 --port $PORT`.
- Database: Neon Free Postgres.
- Frontend: Vercel static build from `scripts/build_frontend.sh`.
- AI: NVIDIA API key stored only in Render environment variables.
- Voice: Browser Web Speech API, so no TTS hosting is required.

See [DEPLOYMENT.md](./DEPLOYMENT.md) for exact Neon, Render, and Vercel steps.

## Important Environment Variables

Backend on Render:

```env
ENVIRONMENT=production
NVIDIA_API_KEY=your_nvidia_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=mistralai/mistral-nemotron
DATABASE_URL=postgresql://user:password@ep-example.region.aws.neon.tech/ballsy?sslmode=require
CORS_ORIGINS=https://your-vercel-app.vercel.app
ALLOWED_HOSTS=your-render-service.onrender.com
USE_CLOUD_TTS=false
USE_CLOUDFLARE_TTS=false
ENABLE_GEMINI_TTS=false
```

Frontend on Vercel:

```env
BALLSY_BACKEND_URL=https://your-render-service.onrender.com
```

## Project Structure

- `src/backend/app.py`: FastAPI app, API routes, WebSocket handling, command processing.
- `src/backend/ai/nvidia_client.py`: NVIDIA NIM chat completions client.
- `src/backend/config.py`: Environment-driven app configuration.
- `src/backend/database.py`: SQLAlchemy models and database setup.
- `src/frontend/templates/index.html`: Main Ballsy UI.
- `src/frontend/static/css/styles.css`: Orb UI and responsive layout styling.
- `src/frontend/static/js/voice.js`: Speech recognition, WebTTS, API calls.
- `scripts/build_frontend.sh`: Vercel static frontend build.
- `render.yaml`: Render backend/database blueprint.
- `vercel.json`: Vercel frontend config.

## Notes

The repo still contains older Google/Gemini and Google Cloud TTS modules as optional fallbacks, but the active production path is NVIDIA for AI and browser WebTTS for speech. Keep provider keys in `.env`, Render environment variables, or Vercel environment variables. Do not commit secrets.
