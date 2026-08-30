from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EcoMentor"
    environment: str = "development"

    gemini_api_key: str = ""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "ecomentor"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
