You are an expert DevOps + backend engineer working inside Cursor on a Python FastAPI WebSocket app.

Goal: 
Take my existing “Ballsy Voice Assistant” repo and get it fully ready to deploy on Google Cloud Platform (GCP) using Terraform from the CLI, optimized to run mostly within the GCP free tier and my $300 free trial credits. Use Cloud Run, Cloud SQL (Postgres), Secret Manager, Artifact Registry, and Gemini (cheap Flash model) as the AI backend. By the end, I should be able to run a clear sequence of CLI commands to provision infra and deploy.

==================================================
PROJECT CONTEXT
==================================================

Tech stack (current):
- Backend: FastAPI (Python 3.8+), WebSockets
- Current AI: Mistral API
- Current DB: SQLite (file-based, local)
- Repo structure (important):
  - src/backend/app.py   → main FastAPI app (WebSockets and HTTP)
  - run.py               → app entrypoint / launcher
  - pyproject.toml       → Python dependencies and tool config

Target stack on GCP:
- Compute: Cloud Run (fully managed)
- Container: Python 3.11 slim image, FastAPI + Uvicorn, WebSocket support
- Database: Cloud SQL for PostgreSQL (small/cheap instance)
- Secrets: Secret Manager for API keys and DB URL
- Container registry: Artifact Registry (Docker)
- AI: Gemini API via the official `google-generativeai` Python SDK, using a cheap Flash model like `gemini-1.5-flash` or the cheapest current Flash/Flash-Lite equivalent
- Authentication / IAM: Minimal IAM roles for Cloud Run service account (Cloud SQL client + Secret Manager access)
- Region: us-central1
- Billing constraints:
  - Optimize for Cloud Run always-free tier usage (small CPU + RAM, scale to zero)
  - Use a small Cloud SQL instance and minimal storage
  - No Memorystore/Redis for now; emulate rate limiting and light session state in-memory or via Postgres

==================================================
HIGH-LEVEL REQUIREMENTS
==================================================

Working inside this repo, you must:

1) ANALYZE THE EXISTING CODEBASE
   - Find all the places where:
     - SQLite is used (DB connection strings, models, migrations, etc.)
     - Mistral API is called
     - In-memory session or rate limiting logic exists
   - Briefly summarize the current architecture in a short markdown section (plan.md) that you create at the repo root:
     - What endpoints exist (especially WebSockets)
     - Where DB is initialized
     - Where AI calls happen
     - How env vars/config are currently handled

2) REPLACE SQLITE WITH POSTGRESQL (CLOUD SQL-FRIENDLY)
   - Introduce SQLAlchemy (if not already present) and a clean DB layer that uses Postgres:
     - Use an async or sync pattern consistent with the current code style; do not half-mix.
   - Replace SQLite connection URLs with a `DATABASE_URL` env variable.
   - Assume that in production on Cloud Run, the URL will look like:
     - `postgresql+psycopg2://<user>:<password>@/<dbname>?host=/cloudsql/<INSTANCE_CONNECTION_NAME>`
   - Make sure the DB initialization is friendly for:
     - Local dev with a local Postgres or SQLite (you can keep a dev mode if that’s simpler)
     - Production with Cloud SQL (Postgres)
   - Add a simple migration mechanism:
     - If no migration tooling exists, set up Alembic:
       - Configure alembic.ini and env.py
       - Create initial migration from the current SQLAlchemy models
     - Provide a simple CLI command or script (like `python -m scripts.migrate_db` or `alembic upgrade head`) that I can run locally against the Cloud SQL instance or locally against a local Postgres.

3) REPLACE MISTRAL WITH GEMINI
   - Find all Mistral client usages and refactor to use Google’s Gemini API:
     - Add dependency: `google-generativeai` (via pyproject.toml)
     - Configure Gemini client with `GEMINI_API_KEY` from environment.
     - Use a cost-effective model such as `gemini-1.5-flash` (or the cheapest Flash/Flash-Lite model that is currently recommended and available).
   - Encapsulate the AI logic:
     - Write a helper module, for example `src/backend/ai/gemini_client.py`, that exposes functions like `async def generate_reply(prompt: str) -> str`.
     - Make sure error handling is robust (timeouts, API errors, etc.).
   - For WebSocket streaming:
     - If the current code uses streamed responses with Mistral, adapt the streaming logic to the Gemini client (or at least preserve the same public behavior even if internally it’s not streaming at first).

4) IMPROVE APP CONFIG, HEALTH, CORS, LOGGING
   - Centralize configuration in a single config module (e.g. `src/backend/config.py`) that reads environment variables:
     - GEMINI_API_KEY
     - DATABASE_URL
     - CORS_ORIGINS (comma-separated list)
     - PORT (default 8080)
   - Add/verify:
     - `/health` endpoint → returns simple JSON `{"status": "ok"}`
     - `/ready` endpoint → performs a lightweight DB check if possible, returns `{"status": "ready"}` or error
   - CORS:
     - Don’t use `*` in production; read allowed origins from `CORS_ORIGINS`.
   - Logging:
     - Configure logging so that logs are structured and Cloud Logging-friendly:
       - Use Python’s `logging` module.
       - Make log messages include consistent keys (e.g. `request_id`, `path`, `user_id` if available).
   - Ensure WebSocket endpoints still work correctly after changes.

5) RATE LIMITING & LIGHT SESSION STATE WITHOUT REDIS
   - Replace any Redis-based or in-memory rate limiting in a way that is compatible with Cloud Run:
     - For now, a per-instance in-memory rate limit is acceptable, using a token bucket or sliding window algorithm.
     - Optionally, store minimal per-user counters in Postgres if you need cross-instance consistency.
   - Keep the design simple and cheap: no external cache service for now.

==================================================
TERRAFORM INFRASTRUCTURE REQUIREMENTS
==================================================

Create a Terraform-based infra setup under an `infra/` directory with clear structure, for example:

- infra/
  - main.tf
  - providers.tf
  - variables.tf
  - outputs.tf
  - artifact_registry.tf
  - cloud_run.tf
  - cloud_sql.tf
  - secrets.tf
  - iam.tf
  - project_services.tf
  - terraform.tfvars.example
  - (optional) versions.tf

General Terraform conventions:
- Use the `google` and `google-beta` providers.
- Parameterize:
  - `project_id`
  - `region` (default: `us-central1`)
  - `service_name` (for Cloud Run)
- Keep code clean, with modules separated logically if needed.

1) ENABLE REQUIRED SERVICES
   - Use `google_project_service` resources to enable at minimum:
     - run.googleapis.com
     - artifactregistry.googleapis.com
     - sqladmin.googleapis.com
     - secretmanager.googleapis.com
     - cloudbuild.googleapis.com
     - aiplatform.googleapis.com
     - logging.googleapis.com
     - monitoring.googleapis.com

2) ARTIFACT REGISTRY (DOCKER)
   - Create a Docker repository in Artifact Registry:
     - Name: something like `ballsy-backend`
     - Format: DOCKER
     - Region: us-central1
   - Output the full image URL (e.g. `us-central1-docker.pkg.dev/<project>/<repo>/<image>`).

3) CLOUD SQL FOR POSTGRES
   - Create a small, cost-optimized instance:
     - Resource: `google_sql_database_instance`
     - Engine: PostgreSQL 15 or later
     - Machine type: small tier (e.g. `db-f1-micro` or other cheapest current tier)
     - Storage: 20GB SSD, with auto-resize enabled
   - Create:
     - `google_sql_database` for `ballsydb`
     - `google_sql_user` with randomly generated password (use Terraform `random_password` resource).
   - Output:
     - `instance_connection_name`
     - DB name
     - DB user and generated password (marked as sensitive output)

4) SECRET MANAGER
   - Define:
     - A secret for `GEMINI_API_KEY` (value will be set manually outside Terraform, but the secret resource itself is created by Terraform).
     - A secret for `DATABASE_URL` which uses the instance connection name, user, and password generated by Terraform.
   - Terraform should:
     - Build the correct Postgres URL for Cloud Run using the instance connection name and create a secret version with that value.
   - Outputs:
     - Names of the secrets so they can be referenced from Cloud Run.

5) IAM & SERVICE ACCOUNTS
   - Create a dedicated service account for the Cloud Run service, e.g. `ballsy-run-sa`.
   - Grant it:
     - `roles/cloudsql.client` on the project or Cloud SQL instance.
     - `roles/secretmanager.secretAccessor` for the relevant secrets.
     - `roles/logging.logWriter` and `roles/monitoring.metricWriter` if needed (check what is minimally required).
   - Use Terraform IAM bindings for least-privilege access.

6) CLOUD RUN SERVICE (INFRA DEFINITION)
   - Define a Cloud Run service using `google_cloud_run_v2_service` (or the appropriate up-to-date resource) with:
     - Image: parameterized string (to be filled after `gcloud builds submit`), but default to something like `us-central1-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/${var.image_name}:latest`
     - Region: `var.region`
     - Service account: the dedicated service account created above
     - CPU: 1 vCPU
     - Memory: 2Gi
     - Concurrency: ~10 for WebSockets
     - Min instances: 0
     - Max instances: 3 (or configurable)
     - Port: 8080
   - Environment variables:
     - `PORT=8080`
     - `CORS_ORIGINS` (variable)
     - `DATABASE_URL` pulled from Secret Manager
     - `GEMINI_API_KEY` pulled from Secret Manager
   - Attach Cloud SQL:
     - Use the recommended annotation or field to connect Cloud Run to Cloud SQL via the instance connection name (e.g. annotation `run.googleapis.com/cloudsql-instances` for v2 or the equivalent).
   - Configure HTTPS:
     - Allow unauthenticated access for now (public endpoint).
   - Outputs:
     - Cloud Run service URL.

7) VARIABLES, OUTPUTS, AND EXAMPLE TFVARS
   - `variables.tf` should include:
     - `project_id`
     - `region` (default `us-central1`)
     - `service_name`
     - `artifact_registry_repo`
     - `image_name`
     - `cors_origins`
   - `outputs.tf` should expose:
     - Cloud Run URL
     - DB connection name
     - Secrets names
   - `terraform.tfvars.example` should include example values to make configuration easy.

==================================================
DEPLOYMENT FLOW (WHAT YOU MUST DOCUMENT)
==================================================

At the end, produce a markdown section in the root README or a new `DEPLOYMENT.md` that describes EXACT CLI STEPS for me to deploy from my local machine with gcloud already authenticated.

The deployment steps should look like this (you fill in exact commands and variable names):

1) Set environment variables locally:
   - `export PROJECT_ID=...`
   - `export REGION=us-central1`

2) Initialize Terraform:
   - `cd infra`
   - `terraform init`
   - `terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"`
   - `terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION"`

3) Set secret values that Terraform created containers for (if needed):
   - For example, using `gcloud secrets versions add` commands to set the actual GEMINI_API_KEY, etc.

4) Build and push the container image to Artifact Registry:
   - Root of repo: `gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/<repo-name>/<image-name>:<tag> .`

5) Update or apply the Cloud Run service with the built image:
   - Either:
     - Via Terraform by updating an image tag variable and re-running `terraform apply`
     - Or via a one-time `gcloud run deploy` that references the same settings as Terraform (if you choose that pattern, make sure Terraform is still the source of truth and this doesn’t cause drift).

6) Run DB migrations:
   - Document how to run migrations against the Cloud SQL instance:
     - Using `gcloud sql connect` to run `alembic upgrade head`, or
     - Running a small migration script locally using the Cloud SQL connection string.

7) Test:
   - Show example curl/websocket URL:
     - `curl $(terraform output -raw cloud_run_url)/health`
   - Confirm the app is healthy and AI calls work.

==================================================
DELIVERABLES AND STYLE
==================================================

When you respond:

1) Give me a short high-level plan bullet list.
2) Then start implementing changes in the repo step by step:
   - Modify Python app code and config files.
   - Add Alembic or migration script.
   - Create all Terraform files under `infra/`.
3) After changes, show:
   - The final Terraform directory tree.
   - The key Terraform resources (summaries).
   - The exact deployment commands I should run in order from a fresh clone with gcloud already authenticated.
4) Keep everything consistent and correct:
   - No hardcoded project_id.
   - Cloud Run config matches the app (port, environment variables).
   - DB URL format matches what the app expects.
   - Gemini model name and client usage are valid and up to date.

Start by scanning the repo and summarizing the existing architecture, then proceed with the implementation.
