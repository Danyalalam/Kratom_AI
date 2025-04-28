from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    API_TITLE: str = "Kratom AI Recommendation API"
    API_DESCRIPTION: str = "API for recommending Kratom dosage based on user characteristics"
    API_VERSION: str = "0.1.0"
    
    # MongoDB configuration
    MONGODB_URL: str 
    
    # OpenAI API configuration
    OPENAI_API_KEY: str 
    OPENAI_MODEL: str = "gpt-4.1-nano" # Specify the desired OpenAI model
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    #SMTP configs
    EMAIL_FROM: str
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_PORT: str
    SMTP_SERVER: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = Settings()