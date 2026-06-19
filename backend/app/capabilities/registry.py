"""Capability registry for managing available capabilities."""

from typing import Optional, List, Dict
from app.capabilities.base import Capability
from app.capabilities.registry_types import CapabilityInfo


class CapabilityRegistry:
    """Registry for all available capabilities (inspired by Easy Agent Tool Registry)."""

    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        self._capability_info: Dict[str, CapabilityInfo] = {}
        # In-memory cache of enabled skill names (for runtime lookup)
        self._enabled_skill_names: Optional[set] = None

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
        """Get all enabled capabilities based on user skill preferences."""
        # If no enabled skills set (not initialized), enable all
        if self._enabled_skill_names is None:
            return [
                info for name, cap in self._capabilities.items() if cap.is_enabled()
                for info in [self._capability_info[name]]
            ]

        # Return only enabled skills
        return [
            info for name, cap in self._capabilities.items()
            if cap.is_enabled() and name in self._enabled_skill_names
            for info in [self._capability_info[name]]
        ]

    def set_enabled_skills(self, skill_names: set) -> None:
        """Set the enabled skill names (called after skill preference changes)."""
        self._enabled_skill_names = skill_names

    def refresh_enabled_from_db(self, async_session_factory, user_scope: str = "dev_user") -> set:
        """Refresh enabled skills from database. Returns set of enabled skill names."""
        from sqlmodel import select

        if async_session_factory is None:
            # No DB, enable all
            self._enabled_skill_names = set(self._capabilities.keys())
            return self._enabled_skill_names

        import asyncio

        async def _get_enabled():
            async with async_session_factory() as session:
                stmt = select(Skill).where(Skill.user_scope == user_scope)
                result = await session.exec(stmt)
                return {s.name for s in result.all() if s.enabled}

        try:
            # Try to get existing event loop
            loop = asyncio.get_running_loop()
            # We're in async context - schedule the task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _get_enabled())
                self._enabled_skill_names = future.result()
        except RuntimeError:
            # No running loop, create new one
            self._enabled_skill_names = asyncio.run(_get_enabled())

        return self._enabled_skill_names or set(self._capabilities.keys())


# Global registry instance
_registry: Optional[CapabilityRegistry] = None


def get_capability_registry() -> CapabilityRegistry:
    """Get the global capability registry."""
    global _registry
    if _registry is None:
        _registry = CapabilityRegistry()
    return _registry