"""User management endpoints. Admin-only (ADR-4): the router-level dependency
rejects non-admins with 403. Passwords are never returned."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.deps import get_current_user, require_role
from app.core.security import hash_password
from app.models.user import ROLE_ADMIN, STATUS_ACTIVE, User
from app.schemas.auth import UserPublic
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)


@router.get("", response_model=list[UserPublic])
def list_users(session: Session = Depends(get_session)) -> list[User]:
    return session.exec(select(User)).all()


@router.post("", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, session: Session = Depends(get_session)) -> User:
    if session.exec(select(User).where(User.email == body.email)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )
    user = User(
        id=f"usr-{uuid.uuid4().hex[:8]}",
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        status=STATUS_ACTIVE,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: str, body: UserUpdate, session: Session = Depends(get_session)
) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if body.role is not None:
        user.role = body.role
    if body.status is not None:
        user.status = body.status
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    # Guard against an admin locking themselves out by deleting their own account.
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"message": "User deleted"}
