import os
import sys

# Project root on sys.path before any app imports (Settings reads DATABASE_URL).
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.db_url import normalize_database_url

_raw = os.environ.get("DATABASE_URL")
if _raw:
    os.environ["DATABASE_URL"] = normalize_database_url(_raw)

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from alembic import context

from app.database import Base
from app.models.document import Document
from app.models.transaction import Transaction
from app.models.vendor import Vendor
from app.models.category import Category
from app.models.conversation import Conversation

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with DATABASE_URL from environment if available
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def get_database_url() -> str:
    """Prefer DATABASE_URL; otherwise alembic.ini (after set_main_option above)."""
    u = os.environ.get("DATABASE_URL", "").strip()
    if u:
        return normalize_database_url(u)
    return config.get_main_option("sqlalchemy.url")


def ensure_render_uses_real_database() -> None:
    if os.environ.get("RENDER") != "true":
        return
    u = os.environ.get("DATABASE_URL", "").strip()
    if not u:
        raise RuntimeError(
            "DATABASE_URL is not set on Render. Link PostgreSQL in the blueprint or paste the "
            "Internal/External Database URL from your Render Postgres (Environment → DATABASE_URL)."
        )
    if "localhost" in u or "127.0.0.1" in u:
        raise RuntimeError(
            "DATABASE_URL must not use localhost inside Render. Use your Render Postgres or Neon "
            "connection string from the database dashboard, not a value copied from local .env."
        )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    ensure_render_uses_real_database()
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    ensure_render_uses_real_database()
    connectable = create_engine(get_database_url(), poolclass=NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()