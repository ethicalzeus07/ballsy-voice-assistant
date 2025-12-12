### 🎤 Ballsy Voice Assistant

Full‑stack AI voice assistant with a Siri‑like UI, powered by **Google Gemini AI** — witty, confident, and psychologically grounded. Not just an assistant, Ballsy is a friend: playfully roasts you, listens, and gives honest, useful advice after real back‑and‑forth. Speak or type for concise, context‑aware answers and action‑ready commands (open sites, maps, media) in a slick animated interface.

**🚀 Now deployed on Google Cloud Platform (Cloud Run) with PostgreSQL and Gemini AI!**

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-enabled-4285F4?logo=google)
![GCP Cloud Run](https://img.shields.io/badge/GCP-Cloud%20Run-4285F4?logo=googlecloud)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?logo=git)
![Made with Love](https://img.shields.io/badge/made%20with-❤️-ff69b4)

### ✨ Features

- **Voice recognition**: One‑shot browser speech recognition with real‑time UI states
- **AI answers**: Google Gemini AI for concise, context‑aware responses
- **Smart commands**: Search the web, open services (YouTube, Netflix, Spotify), maps/directions, news
- **Math**: Inline calculations and chained operations (e.g., + 10)
- **WebSocket + REST**: Real‑time updates and HTTP fallbacks
- **Siri‑like UI**: Animated orb, typing indicator, dark mode
- **Multi-user support**: Multiple users can use the system simultaneously without conflicts
- **Security protections**: Rate limiting, DDoS protection, input validation, and session management
- **Cloud-native**: Deployed on GCP Cloud Run with PostgreSQL (Cloud SQL) and Secret Manager

### 🤘 Why Ballsy feels different

- **Friend‑first persona**: More than a tool — Ballsy teases and motivates (light roasting), actually listens, and offers genuine, practical advice as the conversation unfolds.
- **Crafted voice**: Witty, confident, and psychologically grounded (think Ryan Reynolds' delivery with Robert Greene's clarity). Replies feel human, helpful, and entertaining — not generic.
- **Context‑aware by design**: Each request includes recent conversation turns, so Ballsy remembers the thread (within a server session) and stays in character.
- **Concise on purpose**: Defaults to single‑sentence, high‑signal answers for speed and clarity; expands only when needed.
- **Action‑first responses**: Recognized intents (YouTube, Spotify, Maps, news, etc.) return actions (`open_url`, `search`) so the UI can do things immediately, not just talk.
- **Grounded honesty**: When uncertain, it deliberately falls back to helpful searches instead of guessing.

**Model**: `gemini-2.0-flash-exp` (cost-efficient Flash model with automatic fallback)

### 🚀 Quick start (Local Development)

**Prerequisites:**
- Python 3.8+
- Microphone access + Internet
- `GEMINI_API_KEY` ([Get one here](https://makersuite.google.com/app/apikey))

**1) Clone and enter the project**
```bash
git clone https://github.com/ethicalzeus07/ballsy-voice-assistant.git
cd ballsy-voice-assistant
```

**2) Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3) Install dependencies**
```bash
pip install -r requirements.txt
# Or manually:
pip install -U fastapi uvicorn[standard] flask python-dotenv google-genai SpeechRecognition pydantic python-multipart websockets jinja2 sqlalchemy psycopg2-binary alembic
```

**4) Configure your API key**
```bash
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
echo "DATABASE_URL=sqlite:///./voice_assistant.db" >> .env  # SQLite for local dev
```

**5) Run the app**
```bash
python run.py
# then open http://localhost:8000
```

**Dev reload (alternative):**
```bash
uvicorn src.backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### ☁️ Deploy to Google Cloud Platform

Ballsy is production-ready on GCP! Deploy with one command using Terraform.

**Prerequisites:**
- GCP project with billing enabled
- `gcloud` CLI installed and authenticated
- Terraform installed (>= 1.0)
- Gemini API key

**Quick Deploy:**
```bash
# See detailed instructions in DEPLOYMENT.md
cd infra
terraform init
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="region=us-central1"
```

**What gets deployed:**
- ☁️ **Cloud Run** - Serverless container hosting
- 🗄️ **Cloud SQL (PostgreSQL)** - Managed database
- 🔐 **Secret Manager** - Secure API key storage
- 📦 **Artifact Registry** - Docker image storage
- 🔑 **IAM Roles** - Least privilege access

**Full deployment guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for step-by-step instructions.

### 🏗️ Architecture overview

- **Backend (FastAPI)**: REST + WebSocket, PostgreSQL persistence (Cloud SQL in production), Gemini AI integration
- **Frontend (HTML/CSS/JS)**: Served by FastAPI; animated orb, chat history, dark mode
- **Multi-user architecture**: Per-user session memory and unique user IDs to support concurrent usage
- **Database**: PostgreSQL (Cloud SQL) with SQLAlchemy ORM and Alembic migrations
- **Configuration**: Centralized config system with environment variable support
- **Key files**:
  - `src/backend/app.py` — API, WebSocket, command engine, DB
  - `src/backend/config.py` — Centralized configuration
  - `src/backend/database.py` — SQLAlchemy models and DB operations
  - `src/backend/ai/gemini_client.py` — Gemini AI integration
  - `src/frontend/templates/index.html` — main UI
  - `src/frontend/static/js/{voice.js, app.js, ui.js}` — voice, app logic, UI events
  - `infra/` — Terraform infrastructure as code

### 🎮 Using Ballsy

- Click the orb to start/stop listening, or type in the input
- Examples:
  - "Who is Marie Curie?"
  - "5 + 10" then "+ 3"
  - "Open YouTube" / "Play Interstellar soundtrack on Spotify"
  - "Directions to Central Park" / "Find cafes on Maps"

**Note**: As a web app, native desktop apps cannot be opened; links open in your browser.

### 🛡️ Security Features

Ballsy includes comprehensive security protections:

- **Rate Limiting**: 30 requests per minute per user to prevent abuse
- **DDoS Protection**: Maximum 1000 concurrent sessions with automatic cleanup
- **Input Validation**: Command length limits and sanitization
- **Session Management**: Automatic cleanup of expired sessions (1 hour timeout)
- **CORS Protection**: Configurable origins (restricted in production)
- **Trusted Hosts**: Only allowed hosts can access the API
- **Security Headers**: XSS protection, content type validation, frame protection
- **Secret Management**: API keys stored in GCP Secret Manager (production)
- **IAM Roles**: Least privilege access for Cloud Run service account

### 🧪 Testing Multi-User Support

To test that multiple users can use the system simultaneously:

```bash
# Run the concurrent users test
python test_concurrent_users.py
```

This will simulate 3 users sending commands concurrently to verify there are no rate limiting conflicts.

### 🛡️ Security Testing

To test the security protections (rate limiting, DDoS protection, input validation):

```bash
# Run the security test suite
python test_security.py
```

This will test:
- Rate limiting (30 requests per minute per user)
- Input validation and sanitization
- Session isolation between users
- DDoS protection (max 1000 concurrent sessions)
- Concurrent user support

### 🔌 API

- `GET /health` — Health check endpoint
- `GET /ready` — Readiness check (includes DB connectivity)
- `POST /api/command` — process text commands
- `POST /api/voice` — process uploaded audio (WAV)
- `GET /api/settings/{user_id}` — read settings
- `PUT /api/settings/{user_id}` — update settings
- `GET /api/history/{user_id}?limit=10` — recent command history
- `WS /ws/voice/{client_id}` — real‑time command channel

**Environment Variables:**
```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Database (local dev uses SQLite, production uses PostgreSQL)
DATABASE_URL=sqlite:///./voice_assistant.db  # Local
# DATABASE_URL=postgresql+psycopg2://user:pass@host/db  # Production

# Optional
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=*
GEMINI_MODEL=gemini-2.0-flash-exp
LOG_LEVEL=INFO
```

### 🧪 Testing (manual)

- Verify mic permissions and speak a few commands
- Try math, search, maps, and media commands
- Toggle dark mode; check WebSocket live responses
- Test health endpoints: `curl http://localhost:8000/health`

### 🐳 Docker

The included `Dockerfile` is optimized for Cloud Run deployment:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
ENV PORT=8080
CMD ["python", "run.py"]
```

**Build and run locally:**
```bash
docker build -t ballsy-voice-assistant .
docker run -p 8000:8080 -e GEMINI_API_KEY=your_key -e DATABASE_URL=sqlite:///./voice_assistant.db ballsy-voice-assistant
```

### 📊 Database Migrations

Ballsy uses Alembic for database schema management:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Or use the helper script
python scripts/migrate_db.py
```

### 🔒 Security & notes

- Keep `GEMINI_API_KEY` in `.env` (local) or GCP Secret Manager (production)
- Database credentials stored securely in Secret Manager (production)
- SQLite file is local only; do not commit it
- CORS is configurable via `CORS_ORIGINS` environment variable
- Terraform state files should not be committed (see `.gitignore`)

### 📚 Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete GCP deployment guide
- **[MIGRATION_SUMMARY.md](./MIGRATION_SUMMARY.md)** - Migration details from Mistral/SQLite to Gemini/PostgreSQL
- **[plan.md](./plan.md)** - Architecture and migration planning
- **[user_guide.md](./user_guide.md)** - User-facing documentation

### 🚀 What's New (v2.0)

- ✅ Migrated from Mistral AI to **Google Gemini API**
- ✅ Replaced SQLite with **PostgreSQL (Cloud SQL)**
- ✅ Deployed on **GCP Cloud Run** (serverless)
- ✅ Added **Terraform infrastructure as code**
- ✅ Implemented **centralized configuration**
- ✅ Added **health/readiness endpoints**
- ✅ Improved **error handling and logging**
- ✅ **Secret Manager** integration for secure key storage

### 🙏 Credits

- Google Gemini AI, FastAPI, SpeechRecognition, Jinja2, SQLAlchemy, and the open‑source community

### 🧩 Sticker board

Add some flair to your issues/PRs and screenshots:

- Core vibe: 🎤🧠✨🚀🌙💬
- UI/voice: 🔊🎛️🟣🔵🟢🟠
- Web/search: 🌐🔎🗺️🧭
- Cloud: ☁️🗄️🔐📦
- Fun: 🦾🔥🕶️💥

Copy‑paste packs:

- Starter: `🎤 🧠 ✨`
- Power: `🎤 🧠 ✨ 🚀 🌐 🔎`
- Night mode: `🌙 🎤 🟣 💬`
- Cloud: `☁️ 🎤 🗄️ ✨`

— Made with ❤️ by Pravar Chauhan

**Ballsy — your witty, wise AI companion**
