import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    # Application Config (loaded directly from .env)
    APP_NAME: str
    ENV: str
    
    # LLM Settings (loaded directly from .env)
    LLM_PROVIDER: str
    GEMINI_MODEL: str
    OPENAI_MODEL: str
    OLLAMA_MODEL: str
    TEMPERATURE: float
    
    # API Keys & Endpoints (loaded directly from .env)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = ""
    HN_API_BASE: str = "https://hacker-news.firebaseio.com/v0"
    
    # Internal Paths & Storage
    BASE_DIR: Path = BASE_DIR
    OUTPUT_FOLDER: Path = ROOT_DIR / "output"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/linkedin_creator.db"
    
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), str(BASE_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure output folder exists
settings.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
