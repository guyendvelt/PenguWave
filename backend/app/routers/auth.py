"""Authentication endpoints (ADR-3).

The JWT is delivered in an HttpOnly cookie — it is never exposed to JavaScript.
Per our decision, login returns the user object only (no token in the body),
a documented deviation from the contract's example response.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import get_session
from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.models.user import STATUS_ACTIVE, User
from app.schemas.auth import LoginRequest, UserPublic

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/login")
def login(
    body: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
) -> dict:
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if user.status != STATUS_ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )

    _set_session_cookie(response, create_access_token(subject=user.id))
    return {"user": UserPublic.model_validate(user)}


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(key=settings.cookie_name, path="/")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)) -> User:
    return user
