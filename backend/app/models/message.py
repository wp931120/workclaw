"""Message model."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON
from enum import Enum
from typing import Optional


class MessageRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="sessions.id", index=True)
    role: MessageRole
    content: str = Field(default="")
    tool_calls: Optional[str] = Field(default=None)
    tool_call_id: Optional[str] = Field(default=None)
    model_usage: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Use field serializer for JSON fields
    class Config:
        arbitrary_types_allowed = True