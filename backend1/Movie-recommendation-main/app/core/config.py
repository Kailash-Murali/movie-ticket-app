import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CineMate AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./cinemate.db"
    
    # AI LLM Provider settings
    LLM_API_KEY: Optional[str] = "mock-key"
    OPENROUTER_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_PROVIDER: str = "gemini" # gemini, openai, openrouter, or mock
    
    APP_ENV: str = "development"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
