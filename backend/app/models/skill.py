"""Skill model - stores user skill enable/disable preferences."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class Skill(SQLModel, table=True):
    """User skill preference - controls which capabilities are enabled."""

    __tablename__ = "skills"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, description="Capability name this skill represents")
    enabled: bool = Field(default=True, description="Whether this skill is enabled for the user")
    user_scope: str = Field(default="dev_user", index=True, description="User scope for multi-tenant support")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "enabled": self.enabled,
            "user_scope": self.user_scope,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }