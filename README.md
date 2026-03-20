<div align="center">

# 🎤 Ballsy Voice Assistant


<br/>

Full-stack AI voice assistant with a Siri-like UI, powered by **Google Gemini AI** — witty, confident, and psychologically grounded. Speak or type for concise, context-aware answers and action-ready commands (open sites, maps, media) in a slick animated interface.

**☁️ Deployed on Google Cloud Run + PostgreSQL (Cloud SQL) + Gemini AI**

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-enabled-4285F4?logo=google)
![GCP Cloud Run](https://img.shields.io/badge/GCP-Cloud%20Run-4285F4?logo=googlecloud)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?logo=git)

</div>

---


</details>

---

## ✨ Features

- **Voice recognition**: One-shot browser speech recognition with real-time UI states  
- **AI answers**: Google Gemini AI for concise, context-aware responses  
- **Smart commands**: Search the web, open services (YouTube, Netflix, Spotify), maps/directions, news  
- **Math**: Inline calculations and chained operations (e.g., `+ 10`)  
- **WebSocket + REST**: Real-time updates and HTTP fallbacks  
- **Siri-like UI**: Animated orb, typing indicator, dark mode  
- **Multi-user support**: Multiple users can use the system simultaneously without conflicts  
- **Security protections**: Rate limiting, DDoS protection, input validation, and session management  
- **Cloud-native**: Deployed on GCP Cloud Run with PostgreSQL (Cloud SQL) and Secret Manager  

---

## 🤘 Why Ballsy feels different

- **Friend-first persona**: Teases and motivates (light roasting), listens, and gives practical advice after real back-and-forth.  
- **Crafted voice**: Witty, confident, and psychologically grounded.  
- **Context-aware by design**: Each request includes recent conversation turns, so Ballsy stays on-thread (within a server session).  
- **Concise on purpose**: Defaults to high-signal answers; expands only when needed.  
- **Action-first responses**: Recognized intents return actions (`open_url`, `search`) so the UI can *do* things immediately.  
- **Grounded honesty**: When uncertain, it falls back to helpful searches instead of guessing.  

**Model**: `gemini-2.0-flash-exp`

---

## 🧠 Architecture (high-level)

```mermaid
flowchart LR
  U[User\nVoice / Text] --> F[Frontend\nHTML/CSS/JS Orb UI]
  F -->|WebSocket| B[Backend\nFastAPI]
  F -->|REST Fallback| B
  B --> G[Gemini AI\nResponse + Intent]
  B --> D[(PostgreSQL\nCloud SQL)]
  B --> S[Security Layer\nRate limit, validation,\nsessions, trusted hosts]
  G --> B --> F
````

---

## 🚀 Quick start (Local Development)

**Prerequisites**

* Python 3.8+
* Microphone access + Internet
* `GEMINI_API_KEY` ([https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey))

### 1) Clone and enter the project

```bash
git clone https://github.com/ethicalzeus07/ballsy-voice-assistant.git
cd ballsy-voice-assistant
```

### 2) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
# Or manually:
pip install -U fastapi uvicorn[standard] flask python-dotenv google-genai SpeechRecognition pydantic python-multipart websockets jinja2 sqlalchemy psycopg2-binary alembic
```

### 4) Configure environment variables

```bash
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
echo "DATABASE_URL=sqlite:///./voice_assistant.db" >> .env  # SQLite for local dev
```

### 5) Run the app

```bash
python run.py
# then open http://localhost:8000
```

**Dev reload (alternative)**

```bash
uvicorn src.backend.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## ☁️ Deploy to Google Cloud Platform

Ballsy is production-ready on GCP. Deploy with Terraform.

**Prerequisites**

* GCP project with billing enabled
* `gcloud` CLI installed and authenticated
* Terraform (>= 1.0)
* Gemini API key

**Quick Deploy**

```bash
# See detailed instructions in DEPLOYMENT.md
cd infra
terraform init
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="region=us-central1"
```

**What gets deployed**

* ☁️ **Cloud Run** - Serverless container hosting
* 🗄️ **Cloud SQL (PostgreSQL)** - Managed database
* 🔐 **Secret Manager** - Secure API key storage
* 📦 **Artifact Registry** - Docker image storage
* 🔑 **IAM Roles** - Least privilege access

**Full deployment guide**: `DEPLOYMENT.md`

---

## 🏗️ Project structure (key files)

* `src/backend/app.py` — API, WebSocket, command engine, DB
* `src/backend/config.py` — Centralized configuration
* `src/backend/database.py` — SQLAlchemy models and DB operations
* `src/backend/ai/gemini_client.py` — Gemini AI integration
* `src/frontend/templates/index.html` — main UI
* `src/frontend/static/js/{voice.js, app.js, ui.js}` — voice, app logic, UI events
* `infra/` — Terraform infrastructure as code

---

## 🎮 Using Ballsy

* Click the orb to start/stop listening, or type in the input
* Examples:

  * “Who is Marie Curie?”
  * “5 + 10” then “+ 3”
  * “Open YouTube” / “Play Interstellar soundtrack on Spotify”
  * “Directions to Central Park” / “Find cafes on Maps”

**Note**: As a web app, native desktop apps cannot be opened; links open in your browser.

---

## 🛡️ Security Features

* **Rate Limiting**: 30 requests per minute per user
* **DDoS Protection**: Max 1000 concurrent sessions with automatic cleanup
* **Input Validation**: Command length limits and sanitization
* **Session Management**: Auto cleanup of expired sessions (1 hour timeout)
* **CORS Protection**: Configurable origins (restricted in production)
* **Trusted Hosts**: Only allowed hosts can access the API
* **Security Headers**: XSS protection, content type validation, frame protection
* **Secret Management**: API keys stored in GCP Secret Manager (production)
* **IAM Roles**: Least privilege access for Cloud Run service account

---

## 🧪 Testing Multi-User Support

```bash
python test_concurrent_users.py
```

Simulates 3 users sending commands concurrently to verify session isolation.

---

## 🧪 Security Testing

```bash
python test_security.py
```

Tests:

* Rate limiting
* Input validation and sanitization
* Session isolation
* DDoS protection
* Concurrent user support

---

## 🔌 API

* `GET /health` — Health check endpoint
* `GET /ready` — Readiness check (includes DB connectivity)
* `POST /api/command` — process text commands
* `POST /api/voice` — process uploaded audio (WAV)
* `GET /api/settings/{user_id}` — read settings
* `PUT /api/settings/{user_id}` — update settings
* `GET /api/history/{user_id}?limit=10` — recent command history
* `WS /ws/voice/{client_id}` — real-time command channel

**Environment Variables**

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Database (local dev uses SQLite, production uses PostgreSQL)
DATABASE_URL=sqlite:///./voice_assistant.db
# DATABASE_URL=postgresql+psycopg2://user:pass@host/db

# Optional
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=*
GEMINI_MODEL=gemini-2.0-flash-exp
LOG_LEVEL=INFO
```

---

## 🐳 Docker

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

**Build and run locally**

```bash
docker build -t ballsy-voice-assistant .
docker run -p 8000:8080 -e GEMINI_API_KEY=your_key -e DATABASE_URL=sqlite:///./voice_assistant.db ballsy-voice-assistant
```

---

## 📊 Database Migrations (Alembic)

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Or helper script
python scripts/migrate_db.py
```

---

## 📚 Documentation

* `DEPLOYMENT.md` — Complete GCP deployment guide
* `MIGRATION_SUMMARY.md` — Migration details from Mistral/SQLite to Gemini/PostgreSQL
* `plan.md` — Architecture and migration planning
* `user_guide.md` — User-facing documentation

---

## 🚀 What's New (v2.0)

* ✅ Migrated from Mistral AI to **Google Gemini API**
* ✅ Replaced SQLite with **PostgreSQL (Cloud SQL)**
* ✅ Deployed on **GCP Cloud Run** (serverless)
* ✅ Added **Terraform infrastructure as code**
* ✅ Implemented **centralized configuration**
* ✅ Added **health/readiness endpoints**
* ✅ Improved **error handling and logging**
* ✅ **Secret Manager** integration for secure key storage

---

## 🧩 Sticker board

* Core vibe: 🎤🧠✨🚀🌙💬
* UI/voice: 🔊🎛️🟣🔵🟢🟠
* Web/search: 🌐🔎🗺️🧭
* Cloud: ☁️🗄️🔐📦
* Fun: 🦾🔥🕶️💥

Copy-paste packs:

* Starter: `🎤 🧠 ✨`
* Power: `🎤 🧠 ✨ 🚀 🌐 🔎`
* Night mode: `🌙 🎤 🟣 💬`
* Cloud: `☁️ 🎤 🗄️ ✨`

---

— Made with ❤️ by Pravar Chauhan

**Ballsy — your witty, wise AI companion**

```

