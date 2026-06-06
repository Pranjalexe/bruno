"""
Configuration management using pydantic-settings.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class BrunoSettings(BaseSettings):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    data_dir: Path = Path.home() / ".bruno_data"
    default_model: str = "gemini-2.5-flash"
    embedding_model: str = "all-MiniLM-L6-v2"
    log_level: str = "INFO"
    mcp_servers: dict = {}

    model_config = SettingsConfigDict(
        env_prefix="BRUNO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> BrunoSettings:
    """Get cached settings."""
    settings = BrunoSettings()
    # Ensure data directory exists
    settings.data_dir = settings.data_dir.expanduser()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
