"""Session model."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from enum import Enum


class PermissionMode(str, Enum):
    strict = "strict"
    moderate = "moderate"
    trusted = "trusted"


class SessionStatus(str, Enum):
    active = "active"
    archived = "archived"


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(default="New Session")
    model_profile: str = Field(default="anthropic")
    permission_mode: PermissionMode = Field(default=PermissionMode.moderate)
    status: SessionStatus = Field(default=SessionStatus.active)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
