"""Application configuration."""

from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "G Shepherds API"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./test.db"

settings = Settings()
