# Ballsy Production Deployment

This guide deploys Ballsy with a Render backend and a Vercel frontend.

## Target Setup

- Render runs the FastAPI backend.
- Neon Free Postgres stores production data.
- Vercel hosts the static frontend.
- NVIDIA NIM provides AI responses.
- Browser Web Speech handles text-to-speech, so there is no hosted TTS cost.

## 1. Database on Neon

Create a Neon project named `ballsy`, then copy its pooled connection string. It should look like this:

```env
DATABASE_URL=postgresql://user:password@ep-example.region.aws.neon.tech/ballsy?sslmode=require
```

Use the pooled connection string if Neon offers both pooled and direct options. Render free services can restart and reconnect often, so pooling is friendlier.

## 2. Backend on Render

Create a new Render Web Service from this repository, or use the included `render.yaml` blueprint.

Render settings:

```text
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: uvicorn src.backend.app:app --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

Set these Render environment variables:

```env
ENVIRONMENT=production
PYTHON_VERSION=3.11.9
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

Important production note: Render free web services can sleep after inactivity. That is okay for demos, but first requests after sleep may feel slow.

## 3. Frontend on Vercel

Create a Vercel project from the same repository.

Vercel should use the included `vercel.json`:

```json
{
  "buildCommand": "bash scripts/build_frontend.sh",
  "outputDirectory": "src/frontend/dist",
  "cleanUrls": true,
  "trailingSlash": false
}
```

Set this Vercel environment variable:

```env
BALLSY_BACKEND_URL=https://your-render-service.onrender.com
```

Deploy the frontend. The build script copies the existing HTML/CSS/JS app into `src/frontend/dist` and injects the backend URL.

## 4. Connect CORS and Hosts

After Vercel gives you the final frontend URL, update Render:

```env
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

After Render gives you the final backend host, update Render:

```env
ALLOWED_HOSTS=your-render-service.onrender.com
```

After Render gives you the final backend URL, update Vercel:

```env
BALLSY_BACKEND_URL=https://your-render-service.onrender.com
```

Redeploy both services after changing these variables.

## 5. Verify Production

Backend checks:

```bash
curl https://your-render-service.onrender.com/health
curl https://your-render-service.onrender.com/ready
```

Frontend checks:

- Open the Vercel URL.
- Type a message and confirm Ballsy responds.
- Click the orb and allow microphone permission.
- Confirm the page does not scroll down as the conversation grows.
- Confirm audio comes from browser WebTTS and does not require Cloudflare, Gemini, or Google Cloud TTS.

## 6. Recommended Launch Checklist

- Keep `.env` and provider keys out of git.
- Use production-only CORS origins instead of `*`.
- Use production-only allowed hosts instead of `*`.
- Keep WebTTS enabled unless you intentionally switch to a hosted TTS provider.
- Confirm Render logs do not show missing `NVIDIA_API_KEY`.
- Confirm Render logs can connect to Neon with SSL enabled.
- Confirm the first Render request after sleep is acceptable for your use case.
- Add a custom domain only after the Render/Vercel deploy works on default URLs.
