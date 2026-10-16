from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    temporal_address: str
    cinema_service_url: str
    task_queue: str = "reservations"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True
    )


settings = Settings()  # type: ignore