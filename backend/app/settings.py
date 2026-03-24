"""
Application settings and configuration management.
"""

from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "ETI Backend"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/eti"

@validator('DATABASE_URL', pre=True)
def fix_database_url(cls, v):
    if v.startswith('postgres://'):
        v = v.replace('postgres://', 'postgresql+asyncpg://', 1)
    if v.startswith('postgresql://'):
        v = v.replace('postgresql://', 'postgresql+asyncpg://', 1)
    return v
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI / LLM
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Vector Search
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    TOP_K_CHUNKS: int = 5
    
    # RSS Ingestion
    RSS_FETCH_INTERVAL_MINUTES: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 30
    USER_AGENT: str = "ETI-Bot/0.1 (+https://github.com/yourusername/eti)"
    
    # Allowed CORS origins
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        # Look for .env in parent directory (project root)
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings()
