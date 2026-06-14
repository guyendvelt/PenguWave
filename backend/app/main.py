"""PenguWave backend API — application entrypoint.

Wires up the FastAPI app, a strict CORS whitelist, consistent error responses,
and the domain routers.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.routers import auth, events, users

app = FastAPI(title="PenguWave API", version="0.1.0")

# ADR-7: explicit origin whitelist; credentials allowed for cookie-based auth.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """All errors use the contract's consistent shape: {"error": "..."}."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation failures return 400 (per the contract) with a readable message."""
    errors = exc.errors()
    if errors:
        first = errors[0]
        loc = ".".join(str(p) for p in first.get("loc", []) if p != "body")
        msg = first.get("msg", "Invalid request")
        detail = f"{loc}: {msg}" if loc else msg
    else:
        detail = "Invalid request"
    return JSONResponse(status_code=400, content={"error": detail})


app.include_router(auth.router)
app.include_router(events.router)
app.include_router(users.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe — confirms the API is up. Requires no auth."""
    return {"status": "ok"}
