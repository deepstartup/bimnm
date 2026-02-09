"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    app_name: str = "BI Modernization Platform"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str = "sqlite:///./app.db"

    # JWT
    secret_key: str = "your-secret-key-here-minimum-32-characters-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Server
    host: str = "0.0.0.0"
    port: int = 5010
    reload: bool = True

    # CORS
    cors_origins: str = "http://localhost:8090,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
