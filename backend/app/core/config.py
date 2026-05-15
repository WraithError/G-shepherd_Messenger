<<<<<<< Updated upstream
"""Application configuration."""

from pydantic import BaseSettings
=======
from pydantic_settings import BaseSettings

>>>>>>> Stashed changes

class Settings(BaseSettings):
    app_name: str = "G Shepherds API"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./test.db"

<<<<<<< Updated upstream
=======
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


>>>>>>> Stashed changes
settings = Settings()
