from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str

    cinema_service_url: str

    http_timeout_open_api: int
    http_timeout_cinema_service: int
    max_retries: int = 0

    max_tool_rounds: int = 5
    max_output_tokens: int = 3000

    WARSAW: ZoneInfo = ZoneInfo("Europe/Warsaw")

    redis_url: str

    conversation_ttl_seconds: int = 3600
    max_history_items: int = 50


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True
    )

settings = Settings() # type: ignore