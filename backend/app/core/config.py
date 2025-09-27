"""Application configuration settings."""

import os
from typing import List


class Settings:
    """Application settings."""
    
    # Application
    APP_NAME: str = "Review Radar"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "chrome-extension://*"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./review_radar.db"
    
    # ML Models
    SENTIMENT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Scraping
    MAX_REVIEWS_PER_PRODUCT: int = 500
    SCRAPING_DELAY: float = 1.0  # seconds between requests
    USER_AGENT: str = "Review Radar Bot 1.0"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    
    def __init__(self):
        """Initialize settings with environment variable overrides."""
        # Override with environment variables if available
        self.APP_NAME = os.getenv("APP_NAME", self.APP_NAME)
        self.DEBUG = os.getenv("DEBUG", str(self.DEBUG)).lower() == "true"
        self.HOST = os.getenv("HOST", self.HOST)
        self.PORT = int(os.getenv("PORT", str(self.PORT)))
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
        self.SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", self.SENTIMENT_MODEL)
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", self.EMBEDDING_MODEL)
        self.MAX_REVIEWS_PER_PRODUCT = int(os.getenv("MAX_REVIEWS_PER_PRODUCT", str(self.MAX_REVIEWS_PER_PRODUCT)))
        self.SCRAPING_DELAY = float(os.getenv("SCRAPING_DELAY", str(self.SCRAPING_DELAY)))
        self.USER_AGENT = os.getenv("USER_AGENT", self.USER_AGENT)


# Global settings instance
settings = Settings()