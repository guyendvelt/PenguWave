"""Request/response schemas for authentication.

`UserPublic` is the safe representation returned to clients — it never includes
the password hash.
"""
from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    role: str
    status: str
