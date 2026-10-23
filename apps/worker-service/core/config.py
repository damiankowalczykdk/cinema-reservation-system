from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    temporal_address: str
    cinema_service_url: str
    task_queue: str = "reservations"

    smtp_host: str
    smtp_port: int
    smtp_sender: str

    frontend_url: str

    WARSAW: ZoneInfo = ZoneInfo("Europe/Warsaw")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)


settings = Settings()  # type: ignore
