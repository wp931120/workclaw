"""User model."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str = Field(default="")
    role: UserRole = Field(default=UserRole.user)
    api_key_hash: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)