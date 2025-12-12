# Production Deployment Analysis for Google Cloud
## Ballsy Voice Assistant - Complete Technical Specification

---

## 📋 Executive Summary

**Application Type:** Full-stack AI Voice Assistant (Web Application)  
**Primary Framework:** FastAPI (Python 3.8+)  
**AI Service:** Mistral AI (mistral-large-latest)  
**Deployment Target:** Google Cloud Platform  
**Expected Load:** Multi-user concurrent sessions (up to 1000 concurrent sessions)

---

## 🏗️ Application Architecture

### Current Architecture
- **Backend:** FastAPI application with REST API + WebSocket support
- **Frontend:** Static HTML/CSS/JavaScript (served by FastAPI)
- **Database:** SQLite (development) - **NEEDS PRODUCTION UPGRADE**
- **Session Management:** In-memory (per-user session state)
- **Speech Recognition:** Google Speech-to-Text API (via SpeechRecognition library)
- **AI Integration:** Mistral AI API (external service)

### Architecture Components

1. **API Layer**
   - REST endpoints: `/api/command`, `/api/voice`, `/api/history`, `/api/settings`
   - WebSocket endpoint: `/ws/voice/{client_id}`
   - Static file serving: Frontend assets

2. **Application Layer**
   - Command processing with per-user session memory
   - Speech recognition processing
   - AI response generation
   - Math calculation engine
   - External service integration (YouTube, Spotify, Maps, etc.)

3. **Data Layer**
   - SQLite database (users, conversations, messages, settings, command_history)
   - In-memory session storage (user_sessions dictionary)
   - Rate limiting storage (in-memory deque)

4. **Security Layer**
   - Rate limiting: 30 requests/minute per user
   - Session management: 1000 max concurrent sessions, 1-hour timeout
   - Input validation: 1000 character limit
   - CORS protection
   - Trusted host middleware

---

## 💻 Technology Stack & Dependencies

### Python Dependencies
```
fastapi>=0.100.0
uvicorn[standard]>=0.20.0
flask>=2.3.0
python-dotenv>=1.0.0
mistralai>=0.4.0
SpeechRecognition>=3.10.0
pydantic>=2.0.0
python-multipart>=0.0.6
websockets>=11.0.0
jinja2>=3.1.0
```

### External Services
- **Mistral AI API:** Required for AI responses
- **Google Speech-to-Text:** Used via SpeechRecognition library (requires internet)
- **No other external dependencies** (all other integrations are URL-based)

### Frontend Technologies
- Vanilla JavaScript (no build process required)
- HTML5/CSS3
- WebSocket client (native browser API)
- Web Audio API (browser-based speech recognition)

---

## 📊 Resource Requirements

### CPU Requirements
- **Base Load:** 1-2 vCPU for idle state
- **Per Request:** ~0.1-0.3 vCPU per concurrent request
- **Speech Processing:** ~0.2-0.5 vCPU per audio file processing
- **AI API Calls:** Minimal CPU (mostly I/O wait)
- **Recommended:** 2-4 vCPU for production (supports 50-100 concurrent users)

### Memory Requirements
- **Base Application:** ~200-300 MB
- **Per User Session:** ~1-5 MB (conversation history, rate limit tracking)
- **Max Concurrent Sessions:** 1000 users × 5 MB = ~5 GB (worst case)
- **Database:** SQLite is file-based, minimal memory footprint
- **Recommended:** 4-8 GB RAM for production
- **Peak Memory:** ~8-10 GB with 1000 concurrent sessions

### Storage Requirements
- **Application Code:** ~50-100 MB
- **Dependencies:** ~500 MB (Python packages)
- **Database:** SQLite file grows with usage
  - Initial: < 1 MB
  - Per 1000 conversations: ~10-50 MB
  - Per 10,000 commands: ~5-20 MB
  - **Recommended:** 10-20 GB for database + logs
- **Temporary Files:** Audio files (cleaned up immediately, ~1-5 MB temp space needed)
- **Logs:** ~100-500 MB/month depending on traffic
- **Total Recommended:** 20-50 GB persistent disk

### Network Requirements
- **Inbound:** 
  - REST API: ~1-5 KB per request
  - WebSocket: ~0.5-2 KB per message
  - Audio uploads: ~50-200 KB per file
- **Outbound:**
  - Mistral AI API: ~1-5 KB per request
  - Google Speech API: ~50-200 KB per audio file
- **Bandwidth:** 
  - Base: ~1-5 Mbps
  - Peak (100 concurrent users): ~50-100 Mbps
  - **Recommended:** Standard network tier (1 Gbps)

### Database I/O
- **SQLite:** File-based, single-writer limitation
- **Read Operations:** Low (mostly history retrieval)
- **Write Operations:** Medium (command history, settings)
- **Concurrent Writes:** SQLite handles limited concurrency
- **⚠️ CRITICAL:** SQLite is NOT suitable for production with concurrent writes
- **Recommendation:** Migrate to PostgreSQL or Cloud SQL

---

## 🗄️ Database Requirements

### Current Database Schema (SQLite)
- `users` table: User profiles
- `conversations` table: Conversation sessions
- `messages` table: Message history
- `settings` table: User preferences
- `command_history` table: Command logs

### Production Database Recommendations

#### Option 1: Cloud SQL (PostgreSQL) - **RECOMMENDED**
- **Instance Type:** db-f1-micro (1 vCPU, 0.6 GB RAM) for small scale
- **Instance Type:** db-n1-standard-1 (1 vCPU, 3.75 GB RAM) for production
- **Storage:** 20 GB SSD (auto-grow enabled)
- **Backup:** Automated daily backups (7-day retention)
- **High Availability:** Optional (for production)
- **Connection Pooling:** Required (PgBouncer or SQLAlchemy pool)

#### Option 2: Cloud SQL (MySQL)
- Similar specs to PostgreSQL
- Better compatibility with some ORMs

#### Option 3: Firestore (NoSQL)
- Serverless, auto-scaling
- Good for session data
- May require schema redesign

### Database Migration Requirements
- **Current:** SQLite with direct file access
- **Production:** Requires connection string configuration
- **Code Changes Needed:**
  - Replace `sqlite3` with `psycopg2` or `asyncpg` for PostgreSQL
  - Update connection management
  - Add connection pooling
  - Update all SQL queries (SQLite → PostgreSQL syntax differences)

---

## 🔐 Security Requirements

### Current Security Features
- Rate limiting: 30 requests/minute per user
- Session timeout: 1 hour
- Input validation: 1000 character limit
- CORS middleware (currently allows all origins - **NEEDS PRODUCTION CONFIG**)
- Trusted host middleware (currently allows all hosts - **NEEDS PRODUCTION CONFIG**)

### Production Security Requirements

#### 1. API Security
- **HTTPS:** Required (TLS 1.2+)
- **API Keys:** Optional (for external API access)
- **Authentication:** Currently none - **RECOMMEND ADDING**
- **Authorization:** Currently none - **RECOMMEND ADDING**

#### 2. Secrets Management
- **MISTRAL_API_KEY:** Must be stored in Google Secret Manager
- **Database Credentials:** Must be stored in Secret Manager
- **No hardcoded secrets:** ✅ Already using environment variables

#### 3. Network Security
- **Firewall Rules:** Restrict access to specific IPs if needed
- **VPC:** Recommended for production
- **Private IP:** For internal services
- **Load Balancer:** HTTPS termination

#### 4. CORS Configuration
- **Current:** Allows all origins (`*`)
- **Production:** Restrict to specific domains
- **Environment Variable:** `CORS_ORIGINS` (comma-separated)

#### 5. Input Sanitization
- ✅ Already implemented (command length, basic sanitization)
- **Enhancement:** Add SQL injection protection (use parameterized queries - already done)
- **Enhancement:** Add XSS protection for user-generated content

#### 6. Rate Limiting
- ✅ Already implemented (in-memory)
- **Enhancement:** Use Redis for distributed rate limiting (multi-instance deployments)

#### 7. DDoS Protection
- **Current:** Max 1000 concurrent sessions (in-memory)
- **Production:** Use Cloud Armor for DDoS protection
- **Recommendation:** Enable Cloud CDN for static assets

---

## 📈 Scaling Considerations

### Current Limitations
1. **SQLite Database:** Single-writer limitation, not suitable for horizontal scaling
2. **In-Memory Sessions:** Lost on server restart, not shared across instances
3. **In-Memory Rate Limiting:** Not shared across instances
4. **Single Instance:** No load balancing

### Scaling Strategy

#### Vertical Scaling (Scale Up)
- **Easier:** Increase instance size
- **Limits:** Single point of failure
- **Cost:** More expensive at scale
- **Recommended For:** < 1000 concurrent users

#### Horizontal Scaling (Scale Out) - **RECOMMENDED FOR PRODUCTION**
- **Requirements:**
  - Shared database (PostgreSQL/Cloud SQL)
  - Shared session storage (Redis)
  - Shared rate limiting (Redis)
  - Load balancer (Cloud Load Balancing)
  - Stateless application (already stateless except for in-memory sessions)

### Scaling Components

#### 1. Application Instances
- **Min Instances:** 2 (for high availability)
- **Max Instances:** 10-20 (auto-scaling based on CPU/memory)
- **Instance Type:** e2-medium (2 vCPU, 4 GB RAM) or e2-standard-2 (2 vCPU, 8 GB RAM)

#### 2. Database Scaling
- **Cloud SQL:** Auto-increase storage, read replicas for read-heavy workloads
- **Connection Pooling:** Required for multiple app instances

#### 3. Session Storage
- **Current:** In-memory (lost on restart)
- **Production:** Redis (Memorystore)
  - **Instance Type:** basic-tier, 1 GB (supports ~1000 sessions)
  - **High Availability:** Standard tier for production

#### 4. Rate Limiting
- **Current:** In-memory per instance
- **Production:** Redis-based distributed rate limiting

#### 5. Static Assets
- **Current:** Served by FastAPI
- **Production:** Cloud CDN (Cloud Storage + Cloud CDN)
  - Reduces server load
  - Faster global delivery
  - Lower bandwidth costs

---

## ☁️ Google Cloud Service Recommendations

### Recommended Architecture

#### Option 1: Cloud Run (Serverless) - **BEST FOR START**
- **Service:** Cloud Run
- **Pros:**
  - Auto-scaling (0 to N instances)
  - Pay per request
  - No server management
  - Built-in HTTPS
  - Easy deployment
- **Cons:**
  - Cold starts (minimal for FastAPI)
  - 60-minute request timeout
  - WebSocket support (limited)
- **Configuration:**
  - CPU: 2 vCPU
  - Memory: 4 GB
  - Min instances: 1 (to avoid cold starts)
  - Max instances: 10
  - Timeout: 300 seconds
  - Concurrency: 80 requests per instance

#### Option 2: Compute Engine (VM) - **BEST FOR CONTROL**
- **Service:** Compute Engine
- **Instance Type:** e2-standard-2 (2 vCPU, 8 GB RAM)
- **OS:** Ubuntu 22.04 LTS or Container-Optimized OS
- **Boot Disk:** 50 GB SSD
- **Pros:**
  - Full control
  - Persistent connections (WebSocket)
  - No cold starts
  - Custom configurations
- **Cons:**
  - Manual scaling
  - Server management required
  - Higher base cost
- **Deployment:** Docker container or direct Python

#### Option 3: GKE (Kubernetes) - **BEST FOR SCALE**
- **Service:** Google Kubernetes Engine
- **Cluster:** Regional (3 zones)
- **Node Pool:** e2-standard-2 nodes (2-10 nodes)
- **Pros:**
  - Auto-scaling
  - High availability
  - Load balancing
  - Rolling updates
- **Cons:**
  - Complex setup
  - Higher operational overhead
  - Overkill for small scale
- **Recommended For:** > 10,000 concurrent users

#### Option 4: App Engine (Flexible) - **ALTERNATIVE**
- **Service:** App Engine Flexible Environment
- **Pros:**
  - Managed platform
  - Auto-scaling
  - Built-in monitoring
- **Cons:**
  - Less flexible than Cloud Run
  - Higher minimum cost
  - Being phased out in favor of Cloud Run

### Database Service
- **Cloud SQL (PostgreSQL):** db-n1-standard-1 (1 vCPU, 3.75 GB RAM, 20 GB SSD)
- **High Availability:** Optional (for production)
- **Backup:** Automated daily backups
- **Connection:** Private IP (VPC) or public IP with authorized networks

### Caching/Session Storage
- **Memorystore (Redis):** basic-tier, 1 GB RAM
- **Purpose:** Session storage, rate limiting, caching
- **Alternative:** Cloud Firestore (if going serverless)

### Load Balancing
- **Cloud Load Balancing:** HTTP(S) Load Balancer
- **Features:**
  - SSL termination
  - Health checks
  - Auto-scaling integration
  - Global distribution (optional)

### CDN & Static Assets
- **Cloud Storage:** Bucket for static assets
- **Cloud CDN:** Enable for the bucket
- **Benefits:** Faster delivery, lower server load

### Monitoring & Logging
- **Cloud Monitoring:** Application metrics, uptime checks
- **Cloud Logging:** Centralized logs
- **Error Reporting:** Automatic error tracking
- **Trace:** Distributed tracing (optional)

### Secrets Management
- **Secret Manager:** Store MISTRAL_API_KEY, database credentials
- **IAM:** Service account with minimal permissions

---

## 🔧 Configuration Requirements

### Environment Variables

#### Required
```bash
MISTRAL_API_KEY=your_mistral_api_key_here
DATABASE_URL=postgresql://user:pass@host:5432/dbname  # For PostgreSQL
REDIS_URL=redis://host:6379  # For Redis (if using)
PORT=8080  # Cloud Run uses PORT env var
HOST=0.0.0.0
```

#### Optional (Production)
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
MAX_REQUESTS_PER_MINUTE=30
MAX_CONCURRENT_SESSIONS=1000
SESSION_TIMEOUT=3600
MAX_COMMAND_LENGTH=1000
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Application Configuration Changes Needed

#### 1. Database Migration
- Replace SQLite with PostgreSQL
- Update connection management
- Add connection pooling
- Test all database operations

#### 2. Session Storage
- Replace in-memory sessions with Redis
- Update session management code
- Handle Redis connection failures gracefully

#### 3. Rate Limiting
- Move from in-memory to Redis-based
- Ensure atomic operations
- Handle Redis failures (fallback to per-instance)

#### 4. CORS Configuration
- Remove `allow_origins=["*"]`
- Use environment variable for allowed origins
- Configure per environment

#### 5. Logging
- Configure structured logging (JSON format)
- Send logs to Cloud Logging
- Set appropriate log levels

#### 6. Health Checks
- Add `/health` endpoint
- Add `/ready` endpoint (database connectivity check)
- Configure for load balancer

#### 7. Graceful Shutdown
- Handle SIGTERM signals
- Close database connections
- Close WebSocket connections
- Wait for in-flight requests

---

## 📦 Deployment Architecture

### Recommended: Cloud Run Deployment

#### Architecture Diagram
```
Internet
  ↓
Cloud Load Balancer (HTTPS)
  ↓
Cloud Run Service (2-10 instances, auto-scaling)
  ├── FastAPI Application
  ├── WebSocket Support
  └── Static File Serving
  ↓
Cloud SQL (PostgreSQL) - Private IP
  ↓
Memorystore (Redis) - Private IP
  ↓
Secret Manager (API Keys)
```

#### Deployment Steps
1. **Containerize Application**
   - Create Dockerfile
   - Build container image
   - Push to Container Registry

2. **Setup Database**
   - Create Cloud SQL instance
   - Run migrations
   - Configure connection

3. **Setup Redis**
   - Create Memorystore instance
   - Configure connection

4. **Deploy to Cloud Run**
   - Create service
   - Configure environment variables
   - Set up service account
   - Configure scaling

5. **Setup Load Balancer**
   - Create HTTPS load balancer
   - Configure SSL certificate
   - Point to Cloud Run service

6. **Configure DNS**
   - Point domain to load balancer IP
   - Verify SSL certificate

---

## 💰 Cost Estimation (Monthly)

### Small Scale (< 100 users/day)
- **Cloud Run:** ~$10-20 (pay per request)
- **Cloud SQL (db-f1-micro):** ~$7-10
- **Memorystore (Redis, 1 GB):** ~$30-40
- **Load Balancer:** ~$18 (base cost)
- **Cloud Storage + CDN:** ~$5-10
- **Networking:** ~$5-10
- **Total:** ~$75-100/month

### Medium Scale (100-1000 users/day)
- **Cloud Run:** ~$50-100
- **Cloud SQL (db-n1-standard-1):** ~$50-70
- **Memorystore (Redis, 1 GB):** ~$30-40
- **Load Balancer:** ~$18
- **Cloud Storage + CDN:** ~$20-30
- **Networking:** ~$20-50
- **Total:** ~$190-300/month

### Large Scale (1000+ users/day)
- **Cloud Run:** ~$200-500
- **Cloud SQL (db-n1-standard-2):** ~$100-150
- **Memorystore (Redis, 2 GB):** ~$60-80
- **Load Balancer:** ~$18
- **Cloud Storage + CDN:** ~$50-100
- **Networking:** ~$50-200
- **Total:** ~$480-1050/month

**Note:** Costs vary based on actual usage, region, and traffic patterns.

---

## 🔍 Monitoring & Observability

### Required Metrics
1. **Application Metrics**
   - Request rate (requests/second)
   - Response time (p50, p95, p99)
   - Error rate (4xx, 5xx)
   - Active WebSocket connections
   - Active user sessions

2. **Resource Metrics**
   - CPU utilization
   - Memory usage
   - Network I/O
   - Disk I/O (database)

3. **Business Metrics**
   - Commands processed per minute
   - AI API call latency
   - Speech recognition success rate
   - User session duration

### Monitoring Tools
- **Cloud Monitoring:** Built-in metrics, custom metrics
- **Cloud Logging:** Centralized logs, log-based metrics
- **Error Reporting:** Automatic error tracking
- **Uptime Checks:** Health check monitoring
- **Dashboards:** Custom dashboards in Cloud Console

### Alerting
- **High Error Rate:** > 5% 5xx errors
- **High Latency:** p95 > 2 seconds
- **Resource Exhaustion:** CPU > 80%, Memory > 90%
- **Database Issues:** Connection failures, high query time
- **API Failures:** Mistral API failures, rate limits

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Migrate database from SQLite to PostgreSQL
- [ ] Implement Redis for session storage
- [ ] Update CORS configuration
- [ ] Add health check endpoints
- [ ] Configure structured logging
- [ ] Set up Secret Manager
- [ ] Create Dockerfile
- [ ] Test locally with Docker
- [ ] Set up CI/CD pipeline (optional)

### Infrastructure Setup
- [ ] Create Cloud SQL instance
- [ ] Create Memorystore Redis instance
- [ ] Create Secret Manager secrets
- [ ] Create service account with proper permissions
- [ ] Set up VPC (if using private IPs)
- [ ] Configure firewall rules

### Application Deployment
- [ ] Build and push Docker image
- [ ] Deploy to Cloud Run
- [ ] Configure environment variables
- [ ] Set up auto-scaling
- [ ] Configure health checks
- [ ] Test endpoints

### Post-Deployment
- [ ] Set up Cloud Load Balancer
- [ ] Configure SSL certificate
- [ ] Set up DNS
- [ ] Configure monitoring and alerts
- [ ] Set up backup strategy
- [ ] Document runbooks
- [ ] Load testing
- [ ] Security audit

---

## ⚠️ Critical Production Considerations

### 1. Database Migration (CRITICAL)
- **Current:** SQLite (not production-ready)
- **Action:** Migrate to Cloud SQL PostgreSQL
- **Impact:** High - Required for production

### 2. Session Storage (CRITICAL)
- **Current:** In-memory (lost on restart)
- **Action:** Migrate to Redis
- **Impact:** High - Required for multi-instance deployments

### 3. Rate Limiting (IMPORTANT)
- **Current:** In-memory (not shared)
- **Action:** Migrate to Redis-based
- **Impact:** Medium - Required for horizontal scaling

### 4. CORS Configuration (SECURITY)
- **Current:** Allows all origins
- **Action:** Restrict to specific domains
- **Impact:** High - Security risk

### 5. Authentication (RECOMMENDED)
- **Current:** None
- **Action:** Add user authentication (OAuth, JWT)
- **Impact:** Medium - Recommended for production

### 6. Error Handling (IMPORTANT)
- **Current:** Basic error handling
- **Action:** Enhance error handling, add retry logic
- **Impact:** Medium - Better user experience

### 7. Logging (IMPORTANT)
- **Current:** File-based logging
- **Action:** Configure Cloud Logging
- **Impact:** Medium - Required for debugging

### 8. Backup Strategy (CRITICAL)
- **Current:** None
- **Action:** Set up automated database backups
- **Impact:** High - Data loss prevention

---

## 📝 Code Changes Required

### 1. Database Migration
```python
# Replace sqlite3 with asyncpg or psycopg2
# Update connection management
# Add connection pooling
```

### 2. Session Storage
```python
# Replace in-memory dict with Redis
# Update session management
# Add Redis connection handling
```

### 3. Rate Limiting
```python
# Replace in-memory deque with Redis
# Use Redis atomic operations
# Add fallback mechanism
```

### 4. Configuration
```python
# Use environment variables for all configs
# Remove hardcoded values
# Add configuration validation
```

### 5. Health Checks
```python
# Add /health endpoint
# Add /ready endpoint (database check)
```

### 6. Logging
```python
# Configure structured logging
# Send to Cloud Logging
# Add request ID tracking
```

---

## 🎯 Recommended Instance Sizes

### Development/Testing
- **Compute:** e2-micro (0.5-1 vCPU, 1 GB RAM)
- **Database:** db-f1-micro (shared CPU, 0.6 GB RAM)
- **Redis:** Not needed for dev

### Small Production (< 100 concurrent users)
- **Compute:** Cloud Run (2 vCPU, 4 GB RAM, 1-5 instances)
- **Database:** db-n1-standard-1 (1 vCPU, 3.75 GB RAM, 20 GB)
- **Redis:** Memorystore basic-tier (1 GB)

### Medium Production (100-500 concurrent users)
- **Compute:** Cloud Run (2 vCPU, 4 GB RAM, 2-10 instances)
- **Database:** db-n1-standard-2 (2 vCPU, 7.5 GB RAM, 50 GB)
- **Redis:** Memorystore standard-tier (2 GB, HA)

### Large Production (500+ concurrent users)
- **Compute:** GKE or Cloud Run (2-4 vCPU, 8 GB RAM, 5-20 instances)
- **Database:** db-n1-standard-4 (4 vCPU, 15 GB RAM, 100 GB, HA)
- **Redis:** Memorystore standard-tier (4 GB, HA)
- **Load Balancer:** Required
- **CDN:** Required

---

## 📚 Additional Resources

### Google Cloud Documentation
- Cloud Run: https://cloud.google.com/run/docs
- Cloud SQL: https://cloud.google.com/sql/docs
- Memorystore: https://cloud.google.com/memorystore/docs
- Secret Manager: https://cloud.google.com/secret-manager/docs

### Migration Guides
- SQLite to PostgreSQL: https://www.postgresql.org/docs/current/migration.html
- FastAPI Production: https://fastapi.tiangolo.com/deployment/

---

## ✅ Summary for Google Cloud AI Assistant

**Application Type:** FastAPI Python web application with WebSocket support  
**Current Database:** SQLite (needs migration to PostgreSQL)  
**Session Storage:** In-memory (needs migration to Redis)  
**Recommended Deployment:** Cloud Run (serverless) or Compute Engine (VM)  
**Database:** Cloud SQL PostgreSQL (db-n1-standard-1 minimum)  
**Caching:** Memorystore Redis (1 GB minimum)  
**Load Balancer:** Cloud Load Balancer (HTTPS)  
**CDN:** Cloud Storage + Cloud CDN (for static assets)  
**Secrets:** Secret Manager (for API keys)  
**Monitoring:** Cloud Monitoring + Cloud Logging  
**Scaling:** Auto-scaling (Cloud Run) or manual (Compute Engine)  
**Estimated Cost:** $75-300/month (small to medium scale)  

**Critical Changes Needed:**
1. Migrate SQLite → Cloud SQL PostgreSQL
2. Migrate in-memory sessions → Redis
3. Update CORS configuration
4. Add health check endpoints
5. Configure structured logging
6. Set up Secret Manager

**Instance Recommendations:**
- **Start Small:** Cloud Run (2 vCPU, 4 GB RAM) + db-n1-standard-1 + Redis 1 GB
- **Scale Up:** Add more Cloud Run instances, upgrade database, increase Redis size

---

*Document Version: 1.0*  
*Last Updated: 2024*  
*Prepared for: Google Cloud Production Deployment*

