"""Normalize DATABASE_URL for SQLAlchemy and hosted PostgreSQL (e.g. Render)."""

from __future__ import annotations

import os


def normalize_database_url(url: str) -> str:
    if not url:
        return url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Render sets RENDER=true; managed Postgres typically requires TLS from the web service.
    if (
        os.environ.get("RENDER") == "true"
        and url.startswith("postgresql")
        and "sslmode=" not in url
    ):
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url
