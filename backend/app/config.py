from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Globot Teaching API"
    debug: bool = True

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/globot_teaching"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/globot_teaching"

    # JWT
    SECRET_KEY: str = "change-me-to-a-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()