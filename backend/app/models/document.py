"""Document model."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Any, Optional, Dict


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    filename: str
    file_path: str
    file_type: str = Field(default="")
    summary: Optional[str] = Field(default=None)
    metadata_: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type_": __import__("sqlalchemy").JSON}, alias="metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)