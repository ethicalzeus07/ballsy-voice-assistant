# Dockerfile for Ballsy Voice Assistant
# Production-ready container for Google Cloud deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn[standard]>=0.20.0 \
    flask>=2.3.0 \
    python-dotenv>=1.0.0 \
    google-genai>=0.2.0 \
    google-cloud-texttospeech>=2.21.0 \
    SpeechRecognition>=3.10.0 \
    pydantic>=2.0.0 \
    python-multipart>=0.0.6 \
    websockets>=11.0.0 \
    jinja2>=3.1.0 \
    sqlalchemy>=2.0.0 \
    psycopg2-binary>=2.9.0 \
    alembic>=1.12.0

# Copy application code
COPY . .

# Create directory for logs
RUN mkdir -p /app/logs

# Expose port (Cloud Run uses PORT env var, default 8080)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')" || exit 1

# Run the application
CMD ["python", "run.py"]
