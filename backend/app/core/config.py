"""Application configuration.

All values are read from environment variables (optionally via a local `.env`
file, which is gitignored). No secrets are hardcoded here — auth-related secrets
(e.g. the JWT signing key) will be added in the auth task and must come from the
environment with no usable default.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Local PostgreSQL connection string (ADR-2). Overridden via env in real use.
    database_url: str = "postgresql://localhost:5432/penguwave"

    # Comma-separated list of allowed CORS origins (ADR-7: strict whitelist).
    cors_origins: str = "http://localhost:5173"

    # --- Auth (ADR-3) ---
    # JWT signing key. No usable default: must be supplied via the environment.
    # The app still boots without it (e.g. /health); auth operations raise if unset.
    secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Session cookie. `secure` must be True in production (HTTPS only).
    cookie_name: str = "pw_session"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    # --- Seed credentials (env-only; never committed) ---
    seed_admin_email: Optional[str] = None
    seed_admin_password: Optional[str] = None
    seed_viewer_email: Optional[str] = None
    seed_viewer_password: Optional[str] = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
