"""Task model."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: Optional[uuid.UUID] = Field(default=None, foreign_key="sessions.id")
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str
    description: str = Field(default="")
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    due_date: Optional[datetime] = Field(default=None)
    parent_task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
