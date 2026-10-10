from zoneinfo import ZoneInfo
from openai import AsyncOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str

    cinema_service_url: str

    http_timeout_open_api: int
    http_timeout_cinema_service: int
    max_retries: int = 0

    WARSAW: ZoneInfo = ZoneInfo("Europe/Warsaw")

    @property
    def openai_client(self) -> AsyncOpenAI: #pragma: no cover
        return AsyncOpenAI(api_key=self.openai_api_key, timeout=self.http_timeout_open_api, max_retries=self.max_retries)


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True
    )

settings = Settings() # type: ignore