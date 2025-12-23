from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "CBSE Learning Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    VERTEX_AI_PROJECT: Optional[str] = None
    VERTEX_AI_LOCATION: str = "us-central1"
    
    REDIS_URL: Optional[str] = None
    
    PUBSUB_PROJECT: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
