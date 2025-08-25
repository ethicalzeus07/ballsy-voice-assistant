#!/usr/bin/env python3
"""
Replit-optimized launcher for Ballsy Voice Assistant
"""
import os
import subprocess
import sys
from pathlib import Path

def main():
    """Main entry point for Replit deployment"""
    print("🎤 Starting Ballsy Voice Assistant on Replit...")
    
    # Set environment variables for Replit
    os.environ['HOST'] = '0.0.0.0'
    os.environ['PORT'] = '5000'
    
    # Create .env if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        with open('.env', 'w') as f:
            f.write('MISTRAL_API_KEY=W7ubHcUDajunz3zrREm7zXya31Nlj9n2\n')
        print("✅ Created .env file")
    
    # Use run.py with port 5000 for Replit
    try:
        subprocess.run([sys.executable, 'run.py', '--frontend-port', '5000'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Ballsy shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
