"""
Centralized configuration module for Ballsy Voice Assistant.
Loads environment variables and provides type-safe configuration.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # Server
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./voice_assistant.db"  # Default for local dev
    )
    
    # AI (Gemini)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]
    
    # System Prompt
    SYSTEM_PROMPT: str = (
        "Your name is Ballsy. You talk like Ryan Reynolds. "
        "You are the reflection of Robert Greene and his books. "
        "You are a chill, smart best friend who's read every psychology book, "
        "lifts at 6 AM, pulls girls like a magician, and makes people laugh during breakdowns. "
        "You always give honest advice, use real psychology (no cheesy lines), "
        "talk like a confident big brother, and you're funny but wise."
    )
    
    # Voice settings
    VOICE: str = os.getenv("VOICE", "Jamie")
    VOICE_SPEED: int = int(os.getenv("VOICE_SPEED", "130"))
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "30"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    MAX_SESSIONS: int = int(os.getenv("MAX_SESSIONS", "1000"))
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production (Cloud Run)."""
        return os.getenv("K_SERVICE") is not None or os.getenv("GAE_ENV") is not None
    
    @classmethod
    def is_sqlite(cls) -> bool:
        """Check if using SQLite database."""
        return cls.DATABASE_URL.startswith("sqlite")


# Global config instance
config = Config()

