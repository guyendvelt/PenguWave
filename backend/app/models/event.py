"""Security event table.

Columns are snake_case (idiomatic SQL/Python); the API layer aliases them back
to the contract's camelCase (assetHostname, assetIp, sourceIp). `userId` from the
mock data is intentionally dropped — it is not part of the contract's event shape
and both roles can read all events (ADR-4). Tags are stored as a Postgres array.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel

# Allowed severities (enforced at the API/schema layer).
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


class Event(SQLModel, table=True):
    __tablename__ = "events"

    # Core identity fields are required.
    id: str = Field(primary_key=True)
    timestamp: datetime
    severity: str
    title: str
    # Non-core fields are nullable: real-world events may arrive incomplete and we
    # preserve them as-is rather than dropping or inventing data.
    description: Optional[str] = None
    asset_hostname: Optional[str] = None
    asset_ip: Optional[str] = None
    source_ip: Optional[str] = None
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String), nullable=False, server_default="{}"),
    )
