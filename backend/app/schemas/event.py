"""Event response schema.

Reads snake_case columns from the ORM and serializes them back to the contract's
camelCase keys (assetHostname, assetIp, sourceIp). FastAPI serializes responses
with by_alias=True, so the JSON keys use the aliases below.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    timestamp: datetime
    severity: str
    title: str
    description: Optional[str] = None
    asset_hostname: Optional[str] = Field(default=None, serialization_alias="assetHostname")
    asset_ip: Optional[str] = Field(default=None, serialization_alias="assetIp")
    source_ip: Optional[str] = Field(default=None, serialization_alias="sourceIp")
    tags: list[str] = []
