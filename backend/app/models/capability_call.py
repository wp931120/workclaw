"""Capability call audit log model."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional
import sqlalchemy


class CapabilityCallStatus(str, Enum):
    approved = "approved"
    denied = "denied"
    error = "error"
    completed = "completed"


class CapabilityCall(SQLModel, table=True):
    __tablename__ = "capability_calls"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="sessions.id", index=True)
    message_id: uuid.UUID = Field(foreign_key="messages.id")
    capability_name: str = Field(index=True)
    input_data: Optional[str] = Field(default=None, description="JSON input data")
    output_data: Optional[str] = Field(default=None, description="JSON output data")
    status: CapabilityCallStatus = Field(default=CapabilityCallStatus.approved)
    created_at: datetime = Field(default_factory=datetime.utcnow)