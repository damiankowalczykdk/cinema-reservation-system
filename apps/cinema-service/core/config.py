from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    port: int = 8001

    model_config = SettingsConfigDict(
        env_file='.env',
        extra="ignore",
        frozen=True
    )

settings = Settings()