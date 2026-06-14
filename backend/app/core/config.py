"""Application configuration.

All values are read from environment variables (optionally via a local `.env`
file, which is gitignored). No secrets are hardcoded here — auth-related secrets
(e.g. the JWT signing key) will be added in the auth task and must come from the
environment with no usable default.
"""
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

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
