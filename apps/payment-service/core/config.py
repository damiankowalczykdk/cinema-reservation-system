from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    postgres_payment_user: str
    postgres_payment_password: str
    postgres_payment_host: str
    postgres_payment_port: int
    postgres_payment_db: str

    stripe_secret_key: str
    stripe_webhook_secret: str

    frontend_url: str
    cinema_service_url: str

    http_timeout: int

    default_currency: str = "usd"

    @property
    def POSTGRES_URI(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_payment_user}:{self.postgres_payment_password}@{self.postgres_payment_host}:{self.postgres_payment_port}/{self.postgres_payment_db}"


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True
    )

settings = Settings() #type: ignore
