"""Capability registry types."""

from app.capabilities.base import CapabilityCategory


class CapabilityInfo:
    """Information about a registered capability."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict,
        category: str,
        is_read_only: bool = True,
        is_dangerous: bool = False,
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.category = category
        self.is_read_only = is_read_only
        self.is_dangerous = is_dangerous

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "category": self.category,
            "is_read_only": self.is_read_only,
            "is_dangerous": self.is_dangerous,
        }