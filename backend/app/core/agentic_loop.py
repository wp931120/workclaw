"""Agentic loop - the core reasoning loop (inspired by Easy Agent agenticLoop)."""

import json
import uuid
import time
from datetime import datetime
from typing import AsyncGenerator, Any, Optional
from app.capabilities.base import Capability, CapabilityContext, CapabilityResult
from app.capabilities.registry import get_capability_registry
from app.services.model_provider import ModelProvider
from app.models.database import async_session_factory


class SSEventType:
    TEXT_DELTA = "text_delta"
    CAPABILITY_CALL = "capability_call"
    CAPABILITY_RESULT = "capability_result"
    USAGE = "usage"
    DONE = "done"
    ERROR = "error"


class AgenticLoop:
    """
    Core agentic loop - handles the reasoning → tool call → observe cycle.

    Inspired by Easy Agent's agenticLoop.ts:
    1. Call LLM with current messages and available tools
    2. Stream text output
    3. If LLM requests a tool, check permissions and execute
    4. Feed tool result back to LLM
    5. Repeat until no more tool calls
    """

    MAX_TOOL_TURNS = 20

    def __init__(
        self,
        model_provider: ModelProvider,
        permission_mode: str = "moderate",
    ):
        self.model_provider = model_provider
        self.permission_mode = permission_mode
        self.capability_registry = get_capability_registry()

    async def query(
        self,
        messages: list[dict],
        user_id: str,
        session_id: str,
        system: Optional[str] = None,
        model_profile: str = "claude-glm-5.1",
    ) -> AsyncGenerator[dict, None]:
        """
        Execute the agentic query loop.

        Yields SSE events:
        - text_delta: streaming text from LLM
        - capability_call: LLM wants to call a capability (skill_call_start)
        - capability_result: capability execution result (skill_call_result)
        - usage: token usage update
        - done: query completed
        - error: error occurred
        """
        # Refresh enabled skills from database before each query
        if async_session_factory is not None:
            try:
                self.capability_registry.refresh_enabled_from_db(async_session_factory)
            except Exception:
                # Continue with cached or all-enabled fallback
                pass

        tool_calls = []
        tool_turns = 0

        while tool_turns < self.MAX_TOOL_TURNS:
            # Call LLM with system prompt
            async for event in self.model_provider.stream_chat(
                messages=messages,
                tools=self._build_tools_schema(),
                model_profile=model_profile,
                system=system,
            ):
                event_type = event.get("type")

                if event_type == "content_block_delta":
                    event_data = event.get("data", {})
                    delta = event_data.get("delta", {})
                    # Text delta from LLM
                    if "text" in delta:
                        yield {"type": SSEventType.TEXT_DELTA, "data": {"content": delta["text"]}}
                    # Tool input delta
                    if "input" in delta and tool_calls:
                        tool_calls[-1].setdefault("input_raw", "")
                        tool_calls[-1]["input_raw"] += delta["input"]

                elif event_type == "content_block_start":
                    block = event.get("data", {}).get("content_block", {})
                    if block.get("type") == "tool_use":
                        tool_calls.append({
                            "id": block.get("id"),
                            "name": block.get("name"),
                            "input": {},
                            "input_raw": "",
                        })

                elif event_type == "content_block_stop":
                    # Parse accumulated tool input JSON
                    if tool_calls and tool_calls[-1].get("input_raw"):
                        try:
                            tool_calls[-1]["input"] = json.loads(tool_calls[-1]["input_raw"])
                        except json.JSONDecodeError:
                            tool_calls[-1]["input"] = {}
                        del tool_calls[-1]["input_raw"]

                elif event_type == "message_delta":
                    # Usage update
                    usage = event.get("data", {}).get("usage", {})
                    if usage:
                        yield {"type": SSEventType.USAGE, "data": usage}

                elif event_type == "message_stop":
                    # Message complete - if no tool calls, we're done
                    if not tool_calls:
                        yield {"type": SSEventType.DONE, "data": {}}
                        return
                    # Otherwise, process tool calls
                    break

            # Process tool calls
            if not tool_calls:
                break

            # Execute each tool call
            for tool_call in tool_calls:
                tool_name = tool_call.get("name")
                tool_input = tool_call.get("input", {})
                tool_id = tool_call.get("id")
                call_start_time = time.time()

                # Find capability
                capability = self.capability_registry.find(tool_name)
                if not capability:
                    yield {"type": SSEventType.ERROR, "data": {"message": f"Capability not found: {tool_name}"}}
                    continue

                # Check permission
                permission_result = await self._check_permission(capability, tool_input)
                if not permission_result["allowed"]:
                    yield {
                        "type": SSEventType.CAPABILITY_RESULT,
                        "data": {
                            "name": tool_name,
                            "result": {"success": False, "error": f"Permission denied: {permission_result['reason']}"},
                            "duration_ms": 0,
                        },
                    }
                    continue

                # Emit capability call event with more details
                yield {
                    "type": SSEventType.CAPABILITY_CALL,
                    "data": {
                        "name": tool_name,
                        "title": capability.description.split(" - ")[0] if " - " in capability.description else capability.name,
                        "input": tool_input,
                        "call_id": tool_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                }

                # Execute capability
                context = CapabilityContext(
                    user_id=user_id,
                    session_id=session_id,
                    current_time=datetime.utcnow().isoformat(),
                )
                result = await capability.call(tool_input, context)

                # Calculate duration
                duration_ms = int((time.time() - call_start_time) * 1000)

                # Emit capability result with more details
                yield {
                    "type": SSEventType.CAPABILITY_RESULT,
                    "data": {
                        "name": tool_name,
                        "result": result,
                        "duration_ms": duration_ms,
                        "call_id": tool_id,
                    }
                }

                # Add tool result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{"id": tool_id, "name": tool_name, "input": tool_input}],
                })
                messages.append({
                    "role": "user",
                    "content": None,
                    "tool_calls": None,
                    "tool_call_id": tool_id,
                })

                # Add tool result content
                tool_result_content = json.dumps(result)
                messages.append({
                    "role": "user",
                    "content": tool_result_content,
                })

            tool_calls = []
            tool_turns += 1

        yield {"type": SSEventType.DONE, "data": {}}

    def _build_tools_schema(self) -> list[dict]:
        """Build the tools schema for the LLM."""
        capabilities = self.capability_registry.get_enabled()
        return [
            {
                "name": cap.name,
                "description": cap.description,
                "input_schema": cap.input_schema,
            }
            for cap in capabilities
        ]

    async def _check_permission(self, capability: Capability, input: dict) -> dict:
        """Check if the capability call is allowed based on permission mode."""
        is_read_only = capability.is_read_only()
        is_dangerous = capability.is_dangerous()

        if self.permission_mode == "strict":
            # Strict: need approval for everything except basic queries
            if is_read_only and not is_dangerous:
                return {"allowed": True, "reason": "read-only"}
            return {"allowed": False, "reason": "strict mode requires approval"}

        elif self.permission_mode == "moderate":
            # Moderate: allow read-only, need approval for writes
            if is_read_only and not is_dangerous:
                return {"allowed": True, "reason": "read-only"}
            if is_dangerous:
                return {"allowed": False, "reason": "dangerous operation requires approval"}
            return {"allowed": True, "reason": "moderate mode"}

        else:  # trusted
            # Trusted: allow all
            return {"allowed": True, "reason": "trusted mode"}