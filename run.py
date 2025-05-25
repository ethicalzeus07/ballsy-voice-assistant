#!/usr/bin/env python3
"""
Integration script for the full-stack voice assistant with Siri-like UI.
This script sets up the complete application, including:
- Backend FastAPI server
- Frontend Flask server for serving the UI
- Database initialization
- Environment setup
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import argparse
from pathlib import Path

# Define paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "src" / "backend"
FRONTEND_DIR = ROOT_DIR / "src" / "frontend"
ENV_FILE = ROOT_DIR / ".env"

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not ENV_FILE.exists():
        with open(ENV_FILE, "w") as f:
            f.write("MISTRAL_API_KEY=W7ubHcUDajunz3zrREm7zXya31Nlj9n2\n")
        print("Created .env file with default Mistral API key")

def install_dependencies():
    """Install required Python dependencies"""
    print("Installing dependencies...")
    requirements = [
        "fastapi",
        "uvicorn",
        "flask",
        "python-dotenv",
        "mistralai",
        "SpeechRecognition",
        "pydantic",
        "python-multipart",
        "websockets",
        "jinja2"
    ]
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + requirements)
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def start_backend_server(port=8000):
    """Start the backend FastAPI server"""
    print(f"Starting backend server on port {port}...")
    backend_script = BACKEND_DIR / "app.py"
    
    # Run in a separate process
    process = subprocess.Popen(
        [sys.executable, str(backend_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(2)
    
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"Backend server failed to start: {stderr}")
        sys.exit(1)
    
    print(f"Backend server running on http://localhost:{port}")
    return process

def create_flask_app():
    """Create a Flask app to serve the frontend"""
    from flask import Flask, render_template, send_from_directory
    
    app = Flask(__name__, 
                template_folder=str(FRONTEND_DIR / "templates"),
                static_folder=str(FRONTEND_DIR / "static"))
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory(str(FRONTEND_DIR / "static"), path)
    
    return app

def start_frontend_server(port=5000):
    """Start the frontend Flask server"""
    print(f"Starting frontend server on port {port}...")
    
    # Create and configure Flask app
    app = create_flask_app()
    
    # Start in a separate thread
    thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False))
    thread.daemon = True
    thread.start()
    
    print(f"Frontend server running on http://localhost:{port}")
    return thread

def open_browser(url):
    """Open the browser to the specified URL"""
    print(f"Opening browser to {url}")
    webbrowser.open(url)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Voice Assistant with Siri-like UI")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend server port")
    parser.add_argument("--frontend-port", type=int, default=5000, help="Frontend server port")
    args = parser.parse_args()
    
    # Setup
    create_env_file()
    install_dependencies()
    
    # Start servers
    backend_process = start_backend_server(port=args.backend_port)
    frontend_thread = start_frontend_server(port=args.frontend_port)
    
    # Open browser
    if not args.no_browser:
        time.sleep(1)  # Give servers a moment to start
        open_browser(f"http://localhost:{args.frontend_port}")
    
    print("\nVoice Assistant is now running!")
    print("Press Ctrl+C to stop the servers and exit")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
