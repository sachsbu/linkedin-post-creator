import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    APP_NAME: str = "Automated LinkedIn Tech Post Generator"
    ENV: str = "development"
    
    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # gemini, openai, ollama
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.7
    
    # Storage & Outputs
    BASE_DIR: Path = BASE_DIR
    OUTPUT_FOLDER: Path = ROOT_DIR / "output"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/linkedin_creator.db"
    
    # News Source API Endpoints
    HN_API_BASE: str = "https://hacker-news.firebaseio.com/v0"
    
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), str(BASE_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()


# Ensure output folder exists
settings.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
