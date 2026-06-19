"""Document model."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class DocumentType(str):
    """Document type enumeration."""
    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    md = "md"
    other = "other"


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    filename: str
    file_path: str
    file_type: str = Field(default="")
    summary: Optional[str] = Field(default=None)
    extra_data: Optional[str] = Field(default=None, description="Extra JSON data")
    created_at: datetime = Field(default_factory=datetime.utcnow)