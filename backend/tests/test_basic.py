"""Simple test to verify basic functionality."""

import asyncio
import sys
sys.path.insert(0, '/Users/wp931120/project/my_work/workclaw/backend')

from app.capabilities.bootstrap import bootstrap_capabilities
from app.capabilities.registry import get_capability_registry
from app.core.orchestrator import SessionOrchestrator
from app.services.model_provider import ModelProvider


async def test_capabilities():
    """Test capability registry."""
    bootstrap_capabilities()
    registry = get_capability_registry()
    capabilities = registry.list_all()

    print(f"Registered {len(capabilities)} capabilities:")
    for cap in capabilities:
        print(f"  - {cap.name}: {cap.description[:50]}...")

    # Test finding a capability
    schedule_cap = registry.find("schedule")
    print(f"\nFound capability 'schedule': {schedule_cap is not None}")

    return len(capabilities) > 0


async def test_orchestrator():
    """Test session orchestrator."""
    orchestrator = SessionOrchestrator()

    # Test session creation
    session = await orchestrator.create_session(
        user_id="test_user",
        title="Test Session",
    )
    print(f"\nCreated session: {session['id'][:8]}...")

    # Test system prompt building
    caps = [
        {"name": "schedule", "description": "Manage calendar"},
        {"name": "todo", "description": "Manage tasks"},
    ]
    prompt = await orchestrator.build_system_prompt("Test User", caps)
    print(f"System prompt length: {len(prompt)} chars")

    return True


async def test_model_provider():
    """Test model provider."""
    provider = ModelProvider()

    # Test mock stream
    messages = [
        {"role": "user", "content": "查看我的日程"}
    ]

    print("\nTesting model provider mock stream...")
    async for event in provider.stream_chat(messages):
        if event.get("type") == "content_block_start":
            block = event.get("data", {}).get("content_block", {})
            if block.get("type") == "tool_use":
                print(f"  Tool call: {block.get('name')}")
        if event.get("type") == "message_stop":
            print("  Stream complete")
            break

    return True


async def main():
    print("=" * 50)
    print("WorkClaw Basic Tests")
    print("=" * 50)

    # Test 1: Capabilities
    print("\n[1] Testing Capabilities...")
    try:
        result = await test_capabilities()
        print(f"  Result: {'PASS' if result else 'FAIL'}")
    except Exception as e:
        print(f"  Result: FAIL - {e}")

    # Test 2: Orchestrator
    print("\n[2] Testing Orchestrator...")
    try:
        result = await test_orchestrator()
        print(f"  Result: {'PASS' if result else 'FAIL'}")
    except Exception as e:
        print(f"  Result: FAIL - {e}")

    # Test 3: Model Provider
    print("\n[3] Testing Model Provider...")
    try:
        result = await test_model_provider()
        print(f"  Result: {'PASS' if result else 'FAIL'}")
    except Exception as e:
        print(f"  Result: FAIL - {e}")

    print("\n" + "=" * 50)
    print("Tests Complete")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())