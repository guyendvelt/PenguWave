"""Security primitives: password hashing (bcrypt) and JWT tokens (PyJWT).

ADR-3 / ADR-7. The JWT signing key comes from the environment only — there is no
usable default. Calling the token helpers without `SECRET_KEY` set raises.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Malformed/empty hash → treat as a non-match rather than erroring.
        return False


def _signing_key() -> str:
    if not settings.secret_key:
        raise RuntimeError(
            "SECRET_KEY is not set. Set it in the environment before using auth."
        )
    return settings.secret_key


def create_access_token(subject: str) -> str:
    """Create a signed JWT whose `sub` claim is the user id."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, _signing_key(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT. Raises jwt.PyJWTError on invalid/expired tokens."""
    return jwt.decode(token, _signing_key(), algorithms=[settings.jwt_algorithm])
