"""Capability bootstrap - register all built-in capabilities."""

from app.capabilities.registry import get_capability_registry
from app.capabilities.schedule import ScheduleCapability, TodoCapability
from app.capabilities.document import DocSummaryCapability, EmailDraftCapability, MeetingNotesCapability
from app.capabilities.knowledge import KnowledgeSearchCapability
from app.capabilities.file_parse import FileParseCapability


def bootstrap_capabilities() -> None:
    """Register all built-in capabilities."""
    registry = get_capability_registry()

    # Register all capabilities
    capabilities = [
        ScheduleCapability(),
        TodoCapability(),
        DocSummaryCapability(),
        EmailDraftCapability(),
        MeetingNotesCapability(),
        KnowledgeSearchCapability(),
        FileParseCapability(),
    ]

    for cap in capabilities:
        registry.register(cap)
        print(f"Registered capability: {cap.name}")