from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Project Info
    PROJECT_NAME: str = "Todo Demo Backend"
    VERSION: str = "0.1.0"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://*.railway.app",
    ]
    
    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:5433/todo_db"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()

