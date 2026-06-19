"""Capabilities API - list available capabilities."""

from fastapi import APIRouter
from app.capabilities.registry import get_capability_registry

router = APIRouter()


@router.get("/capabilities")
async def list_capabilities():
    """List all registered capabilities."""
    registry = get_capability_registry()
    capabilities = registry.list_all()
    return {
        "capabilities": [cap.to_dict() for cap in capabilities],
        "count": len(capabilities),
    }