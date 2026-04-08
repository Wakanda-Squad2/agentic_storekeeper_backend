import json

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from openai import OpenAI, AsyncOpenAI

from app.db_url import normalize_database_url

_DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://storekeeper-andela.vercel.app",
]


def _normalize_origin(origin: str) -> str:
    return origin.strip().rstrip("/")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql://user:password@localhost/storekeeper_db"

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, v: object) -> object:
        if isinstance(v, str) and v.strip():
            return normalize_database_url(v)
        return v

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

    # CORS — JSON array, comma-separated list, or a single origin.
    allowed_origins: list[str] = Field(default_factory=lambda: list(_DEFAULT_ORIGINS))

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, v: object) -> object:
        if v is None:
            return list(_DEFAULT_ORIGINS)
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return list(_DEFAULT_ORIGINS)
            if s.startswith("["):
                try:
                    return json.loads(s)
                except json.JSONDecodeError:
                    return list(_DEFAULT_ORIGINS)
            if "," in s:
                return [x.strip() for x in s.split(",") if x.strip()]
            return [s]
        return v

    @field_validator("allowed_origins", mode="after")
    @classmethod
    def _ensure_origins_normalized(cls, v: list[str]) -> list[str]:
        return [_normalize_origin(str(o)) for o in v]

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

