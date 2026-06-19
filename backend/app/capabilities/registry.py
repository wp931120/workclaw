"""Capability registry for managing available capabilities."""

from typing import Optional, List, Dict
from app.capabilities.base import Capability
from app.capabilities.registry_types import CapabilityInfo


class CapabilityRegistry:
    """Registry for all available capabilities (inspired by Easy Agent Tool Registry)."""

    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        self._capability_info: Dict[str, CapabilityInfo] = {}

    def register(self, capability: Capability) -> None:
        """Register a capability."""
        self._capabilities[capability.name] = capability
        self._capability_info[capability.name] = CapabilityInfo(
            name=capability.name,
            description=capability.description,
            input_schema=capability.input_schema,
            category=capability.category.value,
            is_read_only=capability.is_read_only(),
            is_dangerous=capability.is_dangerous(),
        )

    def find(self, name: str) -> Optional[Capability]:
        """Find a capability by name."""
        return self._capabilities.get(name)

    def list_all(self) -> List[CapabilityInfo]:
        """List all registered capabilities."""
        return list(self._capability_info.values())

    def get_enabled(self) -> List[CapabilityInfo]:
        """Get all enabled capabilities."""
        return [
            info for name, cap in self._capabilities.items() if cap.is_enabled()
            for info in [self._capability_info[name]]
        ]


# Global registry instance
_registry: Optional[CapabilityRegistry] = None


def get_capability_registry() -> CapabilityRegistry:
    """Get the global capability registry."""
    global _registry
    if _registry is None:
        _registry = CapabilityRegistry()
    return _registry