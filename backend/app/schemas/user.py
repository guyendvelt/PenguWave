"""Request schemas for user management, with strict validation."""
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import ROLES, STATUSES

MIN_PASSWORD_LENGTH = 8


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

    @field_validator("password")
    @classmethod
    def password_long_enough(cls, v: str) -> str:
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"password must be at least {MIN_PASSWORD_LENGTH} characters"
            )
        return v

    @field_validator("role")
    @classmethod
    def role_allowed(cls, v: str) -> str:
        if v not in ROLES:
            raise ValueError(f"role must be one of {', '.join(ROLES)}")
        return v


class UserUpdate(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None

    @field_validator("role")
    @classmethod
    def role_allowed(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ROLES:
            raise ValueError(f"role must be one of {', '.join(ROLES)}")
        return v

    @field_validator("status")
    @classmethod
    def status_allowed(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in STATUSES:
            raise ValueError(f"status must be one of {', '.join(STATUSES)}")
        return v
