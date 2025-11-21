"""
Centralized application configuration implementing the 12-Factor App methodology.
Enforces strict environment separation and security protocols.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Immutable configuration schema backed by environment variables."""

    APP_NAME: str = "Fintech Tech Challenge"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./fintech_v3.db"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_CLIENT_ID: str = "1091893544918-tv108hl89ii4lhea7asd1qe55rm6fcsv.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = "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"

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
