"""PenguWave backend API — application entrypoint.

Scaffold only: wires up the FastAPI app, a strict CORS whitelist, and a health
check. Domain routers (auth, events, users) are added in later tasks.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title="PenguWave API", version="0.1.0")

# ADR-7: explicit origin whitelist; credentials allowed for cookie-based auth.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe — confirms the API is up. Requires no auth."""
    return {"status": "ok"}
