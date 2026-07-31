from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "StoreFlow API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./storeflow.db"
    cors_origins: list[str] = [
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
    ]
    auth_secret_key: str = "change-this-development-secret-before-deploying"
    access_token_minutes: int = 480
    demo_admin_email: str = "admin@storeflow.demo"
    demo_admin_password: str = "StoreFlow123!"
    demo_admin_name: str = "Northside Store Owner"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
