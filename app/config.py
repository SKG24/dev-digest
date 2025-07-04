# File: app/config.py
import os
from pathlib import Path
from typing import Optional
import logging
from functools import lru_cache

class Settings:
    """Application configuration settings"""
    
    # Application
    APP_NAME: str = "Dev Digest"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-digest-secret-key-change-in-production")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/users.db")
    DATABASE_ECHO: bool = DEBUG
    
    # GitHub API
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_BASE_URL: str = "https://api.github.com"
    GITHUB_RATE_LIMIT: int = 5000  # requests per hour
    
    # Stack Overflow API
    STACKOVERFLOW_BASE_URL: str = "https://api.stackexchange.com/2.3"
    STACKOVERFLOW_SITE: str = "stackoverflow"
    
    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")
    
    # Admin
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Scheduling
    DIGEST_TIME: str = "20:00"  # 8 PM UTC
    SCHEDULER_TIMEZONE: str = "UTC"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = "logs"
    LOG_FILE: str = "app.log"
    
    # Performance
    MAX_ITEMS_PER_SECTION: int = 10
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 3
    
    # Security
    SESSION_TIMEOUT: int = 24 * 60 * 60  # 24 hours
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # URLs
    APP_URL: str = os.getenv("APP_URL", "http://localhost:8000")
    
    def __init__(self):
        # Create necessary directories
        os.makedirs(self.LOG_DIR, exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Validate required settings
        if not self.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        if not all([self.SMTP_HOST, self.SMTP_USER, self.SMTP_PASSWORD]):
            raise ValueError("SMTP configuration is required")

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()