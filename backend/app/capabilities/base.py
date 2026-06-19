"""Capability base classes and registry - inspired by Easy Agent Tool pattern."""

from abc import ABC, abstractmethod
from typing import Any, TypedDict, Optional, Dict
from enum import Enum


class CapabilityCategory(str, Enum):
    schedule = "schedule"
    todo = "todo"
    document = "document"
    email = "email"
    meeting = "meeting"
    knowledge = "knowledge"
    file = "file"
    workflow = "workflow"
    notification = "notification"
    system = "system"


class CapabilityContext(TypedDict, total=False):
    """Context passed to capability when executing."""

    user_id: str
    session_id: str
    current_time: str


class CapabilityResult(TypedDict, total=False):
    """Result returned by capability execution."""

    success: bool
    content: str
    data: Dict[str, Any]
    error: Optional[str]
    needs_approval: bool


class Capability(ABC):
    """
    Base class for all capabilities (inspired by Easy Agent Tool interface).

    Capabilities are the "tools" that the AI agent can use to perform actions.
    They are registered in the CapabilityRegistry and called by the AgenticLoop.
    """

    name: str = ""
    description: str = ""
    input_schema: Dict[str, Any] = {}
    category: CapabilityCategory = CapabilityCategory.system

    @abstractmethod
    async def call(self, input: Dict[str, Any], context: CapabilityContext) -> CapabilityResult:
        """Execute the capability with given input and context."""
        ...

    def is_read_only(self) -> bool:
        """Whether this capability only reads data (affects permission decision)."""
        return True

    def is_enabled(self) -> bool:
        """Whether this capability is currently available."""
        return True

    def is_dangerous(self) -> bool:
        """
        Whether this capability requires strict authorization.
        Dangerous capabilities (e.g., sending emails) require user approval.
        """
        return False

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this capability's input."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }