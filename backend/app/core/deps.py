"""Auth dependencies: resolve the current user from the session cookie and
enforce role-based access (ADR-4)."""
import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_session
from app.core.security import decode_access_token
from app.models.user import STATUS_ACTIVE, User


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User:
    """Return the authenticated, active user or raise 401."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
    )

    token = request.cookies.get(settings.cookie_name)
    if not token:
        raise unauthorized
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise unauthorized

    user_id = payload.get("sub")
    user = session.get(User, user_id) if user_id else None
    if not user or user.status != STATUS_ACTIVE:
        raise unauthorized
    return user


def require_role(*roles: str):
    """Dependency factory: require the current user to hold one of `roles`."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )
        return user

    return checker
