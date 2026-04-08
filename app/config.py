from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from openai import OpenAI, AsyncOpenAI


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql://user:password@localhost/storekeeper_db"

    # JWT — set SECRET_KEY in .env (see env.example). Maps JWT signing to this field.
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        validation_alias=AliasChoices("SECRET_KEY", "secret_key"),
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Redis (sessions, queues, cache — wire clients where needed)
    redis_url: str = Field(
        default="redis://127.0.0.1:6379/0",
        validation_alias=AliasChoices("REDIS_URL", "redis_url"),
    )

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # File Upload
    max_file_size_mb: int = 10
    allowed_file_types: list[str] = ["pdf", "jpg", "jpeg", "png", "tiff"]
    upload_dir: str = "./uploads"

    # AI/ML
    openrouter_api_key: str = ""
    ai_model: str = "google/gemini-2.5-flash-preview"



settings = Settings()

# OpenRouter clients
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key
)

async_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key
)

