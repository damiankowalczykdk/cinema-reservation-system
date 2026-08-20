from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    @property
    def POSTGRES_URI(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True
    )

database_settings = DatabaseSettings() #type: ignore
