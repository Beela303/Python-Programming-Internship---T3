from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Reading Room API"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./reading_room.db"
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
