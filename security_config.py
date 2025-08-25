#!/usr/bin/env python3
"""
Security configuration for Ballsy Voice Assistant
Centralized security settings to prevent DDoS and abuse
"""

import os
from typing import List

class SecurityConfig:
    """Security configuration settings."""
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "30"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Session management
    MAX_CONCURRENT_SESSIONS = int(os.getenv("MAX_CONCURRENT_SESSIONS", "1000"))
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    
    # Input validation
    MAX_COMMAND_LENGTH = int(os.getenv("MAX_COMMAND_LENGTH", "1000"))
    MAX_AUDIO_FILE_SIZE = int(os.getenv("MAX_AUDIO_FILE_SIZE", "10 * 1024 * 1024"))  # 10MB
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000",
        "https://yourdomain.com"
    ]
    
    # Trusted hosts
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1", 
        "yourdomain.com"
    ]
    
    # API limits
    MAX_WEBHOOK_PAYLOAD_SIZE = int(os.getenv("MAX_WEBHOOK_PAYLOAD_SIZE", "1024 * 1024"))  # 1MB
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS origins from environment or default."""
        env_origins = os.getenv("CORS_ORIGINS")
        if env_origins:
            return [origin.strip() for origin in env_origins.split(",")]
        return cls.ALLOWED_ORIGINS
    
    @classmethod
    def get_allowed_hosts(cls) -> List[str]:
        """Get allowed hosts from environment or default."""
        env_hosts = os.getenv("ALLOWED_HOSTS")
        if env_hosts:
            return [host.strip() for host in env_hosts.split(",")]
        return cls.ALLOWED_HOSTS

# Security logging
SECURITY_LOG_FORMAT = "%(asctime)s - SECURITY - %(levelname)s - %(message)s"

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
}
