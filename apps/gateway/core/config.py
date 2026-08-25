from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Auth0Settings(BaseSettings):
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_audience: str
    auth0_callback_url: str
    app_base_url: str = "http://localhost:3000"

    secret_key: str

    http_timeout: int
    cinema_service_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True
    )


@lru_cache
def get_settings() -> Auth0Settings:
    return Auth0Settings() #type: ignore

settings = get_settings()

