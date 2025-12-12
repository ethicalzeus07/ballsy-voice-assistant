# Google Cloud Deployment Guide
## Step-by-Step Instructions for Ballsy Voice Assistant

---

## Prerequisites

1. Google Cloud account with billing enabled
2. Google Cloud SDK (`gcloud`) installed and configured
3. Docker installed (for building container images)
4. Domain name (optional, for custom domain)

---

## Step 1: Prepare Your Application

### 1.1 Update Dependencies
Ensure `requirements.txt` includes all production dependencies (already created).

### 1.2 Code Changes Required

#### Database Migration (CRITICAL)
You need to replace SQLite with PostgreSQL. Here's what needs to change:

**Current code (SQLite):**
```python
import sqlite3

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # ...
```

**Production code (PostgreSQL):**
```python
import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()
```

**Note:** This requires significant code changes. Consider using SQLAlchemy for easier migration.

#### Session Storage Migration
Replace in-memory sessions with Redis:

```python
import redis

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

# Replace user_sessions dict with Redis
def _get_user_session(self, user_id):
    session_key = f"session:{user_id}"
    session_data = redis_client.get(session_key)
    if not session_data:
        # Create new session
        session_data = {...}
        redis_client.setex(session_key, 3600, json.dumps(session_data))
    return json.loads(session_data)
```

#### Add Health Check Endpoints
Add to `src/backend/app.py`:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    # Check database connection
    try:
        # Test database connection
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service not ready")
```

### 1.3 Update Environment Configuration
Update CORS and security settings:

```python
# In app.py, replace:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remove this
    # ...
)

# With:
allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins[0] else [],
    # ...
)
```

---

## Step 2: Set Up Google Cloud Project

### 2.1 Create Project
```bash
gcloud projects create ballsy-voice-assistant --name="Ballsy Voice Assistant"
gcloud config set project ballsy-voice-assistant
```

### 2.2 Enable Required APIs
```bash
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    redis.googleapis.com \
    secretmanager.googleapis.com \
    compute.googleapis.com \
    containerregistry.googleapis.com
```

### 2.3 Set Up Billing
Link your billing account to the project (via Cloud Console).

---

## Step 3: Create Database (Cloud SQL)

### 3.1 Create PostgreSQL Instance
```bash
gcloud sql instances create ballsy-db \
    --database-version=POSTGRES_15 \
    --tier=db-n1-standard-1 \
    --region=us-central1 \
    --root-password=YOUR_SECURE_PASSWORD \
    --storage-type=SSD \
    --storage-size=20GB \
    --storage-auto-increase \
    --backup \
    --enable-bin-log
```

### 3.2 Create Database
```bash
gcloud sql databases create ballsy_db --instance=ballsy-db
```

### 3.3 Create Database User
```bash
gcloud sql users create ballsy_user \
    --instance=ballsy-db \
    --password=YOUR_SECURE_PASSWORD
```

### 3.4 Get Connection String
```bash
# Get private IP (for VPC)
gcloud sql instances describe ballsy-db --format="value(ipAddresses[0].ipAddress)"

# Connection string format:
# postgresql://ballsy_user:password@PRIVATE_IP:5432/ballsy_db
```

### 3.5 Run Migrations
You'll need to create and run database migrations. Consider using Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize (if not already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Run migration (after connecting to Cloud SQL)
alembic upgrade head
```

---

## Step 4: Create Redis (Memorystore)

### 4.1 Create Redis Instance
```bash
gcloud redis instances create ballsy-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0 \
    --tier=basic
```

### 4.2 Get Redis Connection Info
```bash
gcloud redis instances describe ballsy-redis --region=us-central1 \
    --format="value(host)"
```

---

## Step 5: Set Up Secret Manager

### 5.1 Store Secrets
```bash
# Mistral API Key
echo -n "your_mistral_api_key" | gcloud secrets create mistral-api-key --data-file=-

# Database Password
echo -n "your_db_password" | gcloud secrets create db-password --data-file=-

# Database Connection String (optional, or construct from secrets)
echo -n "postgresql://user:pass@host:5432/db" | gcloud secrets create database-url --data-file=-
```

### 5.2 Grant Access
```bash
# Get service account email (will be created with Cloud Run)
# Grant secret accessor role
gcloud secrets add-iam-policy-binding mistral-api-key \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

## Step 6: Build and Push Docker Image

### 6.1 Configure Docker for GCR
```bash
gcloud auth configure-docker
```

### 6.2 Build Image
```bash
docker build -t gcr.io/ballsy-voice-assistant/ballsy-app:latest .
```

### 6.3 Push to Container Registry
```bash
docker push gcr.io/ballsy-voice-assistant/ballsy-app:latest
```

---

## Step 7: Deploy to Cloud Run

### 7.1 Deploy Service
```bash
gcloud run deploy ballsy-app \
    --image gcr.io/ballsy-voice-assistant/ballsy-app:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80 \
    --set-env-vars "PORT=8080,HOST=0.0.0.0" \
    --set-secrets "MISTRAL_API_KEY=mistral-api-key:latest,DATABASE_URL=database-url:latest" \
    --add-cloudsql-instances ballsy-voice-assistant:us-central1:ballsy-db \
    --vpc-connector projects/ballsy-voice-assistant/locations/us-central1/connectors/redis-connector
```

**Note:** You may need to create a VPC connector for private IP access to Redis.

### 7.2 Alternative: Deploy with YAML
Create `cloud-run-service.yaml`:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ballsy-app
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/cloudsql-instances: "ballsy-voice-assistant:us-central1:ballsy-db"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: gcr.io/ballsy-voice-assistant/ballsy-app:latest
        ports:
        - name: http1
          containerPort: 8080
        env:
        - name: PORT
          value: "8080"
        - name: HOST
          value: "0.0.0.0"
        - name: MISTRAL_API_KEY
          valueFrom:
            secretKeyRef:
              name: mistral-api-key
              key: latest
        resources:
          limits:
            cpu: "2"
            memory: 4Gi
```

Deploy:
```bash
gcloud run services replace cloud-run-service.yaml --region us-central1
```

---

## Step 8: Set Up Load Balancer (Optional but Recommended)

### 8.1 Reserve Static IP
```bash
gcloud compute addresses create ballsy-lb-ip --global
```

### 8.2 Create Load Balancer
Use Cloud Console or Terraform. Configuration:
- Backend: Cloud Run service (ballsy-app)
- Frontend: HTTPS with SSL certificate
- Health check: `/health` endpoint

### 8.3 Configure DNS
Point your domain to the load balancer IP.

---

## Step 9: Configure Monitoring

### 9.1 Create Uptime Check
```bash
gcloud monitoring uptime-checks create ballsy-uptime \
    --display-name="Ballsy Uptime Check" \
    --http-check-path="/health" \
    --period=60s
```

### 9.2 Set Up Alerts
Create alert policies in Cloud Console for:
- High error rate (> 5%)
- High latency (p95 > 2s)
- Resource exhaustion (CPU > 80%, Memory > 90%)

---

## Step 10: Test Deployment

### 10.1 Test Health Endpoint
```bash
curl https://YOUR_SERVICE_URL/health
```

### 10.2 Test API Endpoint
```bash
curl -X POST https://YOUR_SERVICE_URL/api/command \
    -H "Content-Type: application/json" \
    -d '{"command": "hello", "user_id": 1}'
```

### 10.3 Monitor Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

---

## Troubleshooting

### Database Connection Issues
- Verify Cloud SQL instance is running
- Check firewall rules allow Cloud Run access
- Verify connection string format
- Check service account permissions

### Redis Connection Issues
- Verify VPC connector is configured
- Check Redis instance is in same region
- Verify private IP access

### Secret Access Issues
- Verify service account has `secretAccessor` role
- Check secret names match exactly
- Verify secret versions

### High Latency
- Check database query performance
- Monitor Redis connection pool
- Review Cloud Run metrics
- Consider increasing instance size

---

## Next Steps

1. **Set up CI/CD:** Use Cloud Build for automated deployments
2. **Enable CDN:** Use Cloud CDN for static assets
3. **Add Authentication:** Implement user authentication
4. **Scale Testing:** Load test with expected traffic
5. **Backup Strategy:** Verify automated backups are working
6. **Documentation:** Document runbooks for operations team

---

## Cost Optimization Tips

1. **Use Cloud Run:** Pay per request, no idle costs
2. **Right-size instances:** Start small, scale up as needed
3. **Use committed use discounts:** For predictable workloads
4. **Enable auto-scaling:** Scale down during low traffic
5. **Use Cloud CDN:** Reduce origin server load
6. **Monitor costs:** Set up billing alerts

---

*For detailed technical specifications, see PRODUCTION_DEPLOYMENT_ANALYSIS.md*

