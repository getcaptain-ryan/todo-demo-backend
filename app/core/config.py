from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Any


class Settings(BaseSettings):
    """Application settings"""

    # Project Info
    PROJECT_NAME: str = "Todo Demo Backend"
    VERSION: str = "0.1.0"

    # CORS Settings - stored as comma-separated string, parsed to list
    # Using str type to avoid Pydantic trying to JSON-parse it from .env
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3002,http://localhost:5173,http://localhost:8080,https://*.railway.app"

    @field_validator('ALLOWED_ORIGINS', mode='after')
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string to list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace from each origin
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        if isinstance(v, list):
            return v
        return [str(v)]

    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:5433/todo_db"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        # Don't try to parse ALLOWED_ORIGINS as JSON
        env_parse_none_str="null"
    )


settings = Settings()

