#!/usr/bin/env python3
"""
Entrypoint for Render deployment.

- Loads environment variables for local development.
- Imports and runs the FastAPI app (which also serves your frontend).
- Listens on the port assigned by Render (via $PORT), defaulting to 8000 locally.
"""

import os
from dotenv import load_dotenv
import uvicorn
from src.backend.app import app  # Your FastAPI app, which should serve "/"

# Load .env locally. Render injects production environment variables.
load_dotenv()

if __name__ == "__main__":
    # Render sets the PORT environment variable automatically.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        # reload=True  # Leave this commented out on Render (only use for local dev)
    )
