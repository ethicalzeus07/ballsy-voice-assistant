# Ballsy Voice Assistant - Architecture Analysis

## Current Architecture Summary

### Endpoints

**REST API:**
- `POST /api/command` - Process text commands
- `POST /api/voice` - Process uploaded audio (WAV)
- `GET /api/history/{user_id}` - Get command history
- `GET /api/settings/{user_id}` - Get user settings
- `PUT /api/settings/{user_id}` - Update user settings
- `GET /` - Serve frontend HTML

**WebSocket:**
- `WS /ws/voice/{client_id}` - Real-time command channel

### Database (Current: SQLite)

**Location:** `voice_assistant.db` (file-based)

**Tables:**
- `users` - User accounts (id, username, created_at)
- `conversations` - Conversation sessions (id, user_id, started_at)
- `messages` - Message history (id, conversation_id, is_user, content, timestamp)
- `settings` - User preferences (id, user_id, voice, voice_speed, theme)
- `command_history` - Command logs (id, user_id, command, result, timestamp)

**Initialization:**
- `init_db()` function in `src/backend/app.py` (lines 90-139)
- Called during FastAPI lifespan startup
- Uses SQLite context manager `get_db_connection()` (lines 79-87)

### AI Integration (Current: Mistral)

**Client:** `mistralai.Mistral` initialized at module level (line 60)

**Model:** `mistral-large-latest`

**Usage Locations:**
1. `_get_info_or_search()` method (lines 759-840) - For "who is/what is" queries
2. `_ai_fallback()` method (lines 843-881) - General AI responses

**API Key:** Loaded from `MISTRAL_API_KEY` environment variable

### Session & Rate Limiting

**Location:** `CommandProcessor` class (lines 295-885)

**Rate Limiting:**
- In-memory per-user rate limiting using `deque` (line 302)
- 30 requests per minute per user (line 307)
- 60-second sliding window (line 306)
- Stored in `self.rate_limits: Dict[str, deque]`

**Session Management:**
- Per-user session memory in `self.user_sessions: Dict[str, Dict]` (line 299)
- Stores conversation history, last result, calculations
- Session timeout: 1 hour (line 305)
- Max sessions: 1000 (line 304)
- Automatic cleanup of expired sessions (lines 309-325)

### Configuration (Current)

**Environment Variables:**
- `MISTRAL_API_KEY` - Loaded via `dotenv` (line 55)
- `PORT` - Used in `run.py` (defaults to 8000)
- `HOST` - Not currently used, defaults to 0.0.0.0

**Constants:**
- `DB_PATH = "voice_assistant.db"` (line 71)
- `MISTRAL_MODEL = "mistral-large-latest"` (line 64)
- `SYSTEM_PROMPT` (lines 65-70)
- CORS: Currently allows all origins `["*"]` (line 180)
- Trusted hosts: Currently allows all `["*"]` (line 189)

### Logging

**Current Setup:**
- Basic logging to console and file (`voice_assistant.log`)
- Format: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
- Not structured for Cloud Logging

### Frontend

**Location:** `src/frontend/`
- Static files served via FastAPI StaticFiles
- Templates via Jinja2
- Main UI: `templates/index.html`

## Migration Plan

1. **Database:** SQLite → PostgreSQL (Cloud SQL)
   - Replace `sqlite3` with SQLAlchemy
   - Use `DATABASE_URL` environment variable
   - Support both local Postgres and Cloud SQL connection format

2. **AI:** Mistral → Gemini
   - Replace `mistralai` with `google-generativeai`
   - Use `gemini-1.5-flash` model
   - Create `src/backend/ai/gemini_client.py` module

3. **Configuration:** Centralize in `src/backend/config.py`
   - Load all env vars in one place
   - Type-safe config with defaults

4. **Health Checks:** Add `/health` and `/ready` endpoints

5. **CORS:** Make configurable via `CORS_ORIGINS` env var

6. **Logging:** Structure for Cloud Logging compatibility

7. **Migrations:** Set up Alembic for schema management

