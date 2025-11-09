from pydantic_settings import BaseSettings
from typing import Optional
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    APP_NAME: str = "AI Email Assistant"
    DEBUG: bool = True

    DATABASE_URL: str
    
    #Redis
    REDIS_URL: str = "redis://redis:6379/0"

    #security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    #Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    #AI API Keys
    GROQ_API_KEY: Optional[str] = None
    GOOGLE_AI_API_KEY: Optional[str] = None

    #AI Settings
    AI_MODEL: str = "llama3.3-70b-8192"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_EMAIL_LENGTH: int = 4000

    class Config:
        # env_file = ".env"
        env_file = ENV_FILE
        env_file_encoding = "utf-8"

settings = Settings()
