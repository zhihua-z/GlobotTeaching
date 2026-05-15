from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Globot Teaching API"
    debug: bool = True

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/globot_teaching"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/globot_teaching"

    # JWT
    secret_key: str = "change-me-to-a-random-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()