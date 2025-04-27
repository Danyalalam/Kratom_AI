from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    API_TITLE: str = "Kratom AI Recommendation API"
    API_DESCRIPTION: str = "API for recommending Kratom dosage based on user characteristics"
    API_VERSION: str = "0.1.0"
    
    # MongoDB configuration
    MONGODB_URL: str 
    
    # Gemini API configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # Email configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = Settings()