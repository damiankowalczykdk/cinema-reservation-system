from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    hold_minutes: float
    max_hold_minutes: float
    extend_minutes: float

    tmdb_api_token: str
    tmdb_base_address: str = "https://api.themoviedb.org/3"

    http_timeout: float = 5.0


    @property
    def POSTGRES_URI(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True
    )

database_settings = DatabaseSettings() #type: ignore
