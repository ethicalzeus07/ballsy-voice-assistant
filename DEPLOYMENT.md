# Ballsy Voice Assistant - GCP Deployment Guide

This guide provides step-by-step instructions for deploying Ballsy Voice Assistant to Google Cloud Platform using Terraform.

## Prerequisites

1. **Google Cloud Account** with:
   - A GCP project created
   - Billing enabled (free trial credits work)
   - `gcloud` CLI installed and authenticated
   - Terraform installed (>= 1.0)

2. **Local Setup**:
   ```bash
   # Verify gcloud is authenticated
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   
   # Verify Terraform
   terraform version
   ```

3. **Gemini API Key**:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Keep it ready for step 3

## Deployment Steps

### Step 1: Set Environment Variables

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
```

### Step 2: Initialize and Apply Terraform

```bash
cd infra

# Initialize Terraform
terraform init

# Review the plan
terraform plan \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION"

# Apply infrastructure (this will take 5-10 minutes)
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION"
```

**What this creates:**
- Cloud SQL PostgreSQL instance (db-f1-micro)
- Artifact Registry Docker repository
- Secret Manager secrets (containers)
- Cloud Run service (not yet deployed)
- IAM service account with proper permissions

### Step 3: Set Secret Values

After Terraform creates the secret containers, set the actual secret values:

```bash
# Set Gemini API key
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key \
  --data-file=- \
  --project=$PROJECT_ID

# Verify the database URL secret was created by Terraform
gcloud secrets versions access latest \
  --secret=database-url \
  --project=$PROJECT_ID
```

### Step 4: Build and Push Docker Image

```bash
# Get the image URL from Terraform output
IMAGE_URL=$(terraform output -raw artifact_registry_url)

# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build and push the image
gcloud builds submit --tag $IMAGE_URL:latest \
  --project=$PROJECT_ID \
  --region=$REGION
```

**Alternative:** If you prefer to build locally:

```bash
# Authenticate Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build locally
docker build -t $IMAGE_URL:latest .

# Push to Artifact Registry
docker push $IMAGE_URL:latest
```

### Step 5: Update Cloud Run Service

The Cloud Run service is already created by Terraform, but you need to update it with the new image:

```bash
# Get service name
SERVICE_NAME=$(terraform output -raw cloud_run_service_name)

# Update the service with the new image
gcloud run services update $SERVICE_NAME \
  --image=$IMAGE_URL:latest \
  --region=$REGION \
  --project=$PROJECT_ID
```

**Or** update via Terraform by setting the image tag variable and re-running `terraform apply`.

### Step 6: Run Database Migrations

Connect to Cloud SQL and run migrations:

```bash
# Get connection details
DB_CONNECTION=$(terraform output -raw database_instance_connection_name)
DB_NAME=$(terraform output -raw database_name)
DB_USER=$(terraform output -raw database_user)
DB_PASSWORD=$(terraform output -raw database_password)

# Option 1: Using Cloud SQL Proxy (recommended for local)
# Install Cloud SQL Proxy if needed:
# https://cloud.google.com/sql/docs/postgres/connect-instance-auth-proxy

# Start proxy in background
cloud_sql_proxy -instances=$DB_CONNECTION=tcp:5432 &

# Set DATABASE_URL for migrations
export DATABASE_URL="postgresql+psycopg2://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"

# Run migrations
python scripts/migrate_db.py

# Stop proxy
pkill cloud_sql_proxy

# Option 2: Using gcloud sql connect (requires authorized network or Cloud Shell)
gcloud sql connect $DB_CONNECTION --user=$DB_USER --database=$DB_NAME
# Then run: alembic upgrade head
```

**Alternative:** Run migrations from Cloud Shell:

```bash
# Open Cloud Shell
gcloud cloud-shell ssh

# Clone your repo
git clone YOUR_REPO_URL
cd ballsy-voice-assistant-main

# Set DATABASE_URL (use the connection name format)
export DATABASE_URL="postgresql+psycopg2://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$DB_CONNECTION"

# Install dependencies and run migrations
pip install -r requirements.txt
python scripts/migrate_db.py
```

### Step 7: Test the Deployment

```bash
# Get the Cloud Run URL
SERVICE_URL=$(terraform output -raw cloud_run_url)

# Test health endpoint
curl $SERVICE_URL/health

# Test readiness endpoint
curl $SERVICE_URL/ready

# Open in browser
echo "Open this URL in your browser: $SERVICE_URL"
```

## Post-Deployment

### View Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
  --limit 50 \
  --project=$PROJECT_ID
```

### Monitor Costs

- Check billing dashboard: https://console.cloud.google.com/billing
- Cloud SQL db-f1-micro is very cheap (~$7/month)
- Cloud Run scales to zero when not in use (free tier: 2 million requests/month)

### Update CORS Origins

If you need to restrict CORS:

```bash
# Update Terraform variable
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION" \
  -var="cors_origins=https://yourdomain.com,https://www.yourdomain.com"
```

Then update the Cloud Run service:

```bash
gcloud run services update $SERVICE_NAME \
  --update-env-vars CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com" \
  --region=$REGION \
  --project=$PROJECT_ID
```

## Troubleshooting

### Cloud Run can't connect to Cloud SQL

- Verify the service account has `roles/cloudsql.client`
- Check that Cloud SQL instance has private IP enabled
- Verify the `DATABASE_URL` uses the Unix socket format: `postgresql+psycopg2://user:pass@/dbname?host=/cloudsql/INSTANCE_CONNECTION_NAME`

### Secrets not accessible

- Verify service account has `roles/secretmanager.secretAccessor`
- Check secret versions exist: `gcloud secrets versions list SECRET_NAME`

### Database connection errors

- Verify migrations ran successfully
- Check Cloud SQL instance is running: `gcloud sql instances describe INSTANCE_NAME`
- Test connection using Cloud SQL Proxy locally

### Image build fails

- Check Cloud Build logs: `gcloud builds list --limit=5`
- Verify Dockerfile syntax
- Ensure all dependencies are in `pyproject.toml`

## Cost Optimization

This setup is optimized for the free tier:

- **Cloud Run**: Scales to zero, 2M requests/month free
- **Cloud SQL**: db-f1-micro is the smallest tier (~$7/month)
- **Artifact Registry**: 0.5 GB free storage
- **Secret Manager**: First 6 secrets free
- **Logging**: 50 GB free per month

**Estimated monthly cost**: ~$7-10 (mostly Cloud SQL)

## Cleanup

To destroy all resources:

```bash
cd infra
terraform destroy \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION"
```

**Warning**: This will delete the database and all data!

## Next Steps

- Set up custom domain
- Configure Cloud CDN for static assets
- Set up monitoring alerts
- Enable automated backups
- Configure CI/CD pipeline

