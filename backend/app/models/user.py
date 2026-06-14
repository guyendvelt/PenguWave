"""User table.

Roles are limited to `admin` and `viewer` (ADR-4). Passwords are never stored
in plain text — only the bcrypt hash (hashing is wired up in the auth task).
Allowed values for role/status are enforced at the API/schema layer.
"""
from sqlmodel import Field, SQLModel

# Roles (ADR-4)
ROLE_ADMIN = "admin"
ROLE_VIEWER = "viewer"
ROLES = (ROLE_ADMIN, ROLE_VIEWER)

# Account status
STATUS_ACTIVE = "active"
STATUS_DISABLED = "disabled"
STATUSES = (STATUS_ACTIVE, STATUS_DISABLED)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default=ROLE_VIEWER)
    status: str = Field(default=STATUS_ACTIVE)
