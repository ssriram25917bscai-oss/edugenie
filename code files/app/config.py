from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduGenie"
    environment: str = "development"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    demo_mode: bool = True

    local_explanation_enabled: bool = False
    local_explanation_model: str = "MBZUAI/LaMini-Flan-T5-783M"

    max_input_chars: int = 30000
    request_timeout_seconds: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
