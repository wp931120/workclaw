"""Model provider service for LLM communication."""

import os
import json
import uuid
import asyncio
from typing import AsyncGenerator, Optional, List, Dict, Any
import httpx
from app.config.settings import get_settings
from app.config.model_profiles import get_profile, ModelProfile


# Fallback to Claude settings if env not set
CLAUDE_SETTINGS_PATH = os.path.expanduser("~/.claude/settings.json")


def _load_claude_settings() -> Dict[str, Any]:
    """Load settings from ~/.claude/settings.json for fallback values."""
    try:
        if os.path.exists(CLAUDE_SETTINGS_PATH):
            with open(CLAUDE_SETTINGS_PATH, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _get_api_token(profile: ModelProfile) -> Optional[str]:
    """Get API token from env or fallback to Claude settings."""
    # First check env
    token = os.environ.get(profile.api_key_env)
    if token:
        return token

    # Fallback to Claude settings
    claude_settings = _load_claude_settings()
    env_config = claude_settings.get("env", {})
    # Check for common token env names
    for key in ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"]:
        if key in env_config:
            return env_config[key]

    return None


class ModelProvider:
    """Unified model provider that supports multiple backends."""

    def __init__(self):
        self.settings = get_settings()

    async def stream_chat(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        model_profile: str = "anthropic",
        system: Optional[str] = None,
    ) -> AsyncGenerator[Dict, None]:
        """Stream chat completion from the configured model."""
        profile = get_profile(model_profile)
        if not profile:
            raise ValueError(f"Unknown model profile: {model_profile}")

        # If system is passed separately, add it to messages for extraction
        if system:
            messages = [{"role": "system", "content": system}] + messages

        if profile.protocol == "anthropic":
            async for event in self._stream_anthropic(messages, tools, profile):
                yield event
        elif profile.protocol == "openai-chat":
            async for event in self._stream_openai(messages, tools, profile):
                yield event
        else:
            raise ValueError(f"Unsupported protocol: {profile.protocol}")

    async def _stream_anthropic(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]],
        profile: ModelProfile,
    ) -> AsyncGenerator[Dict, None]:
        """Stream from Anthropic-compatible API (e.g., GLM via cucloud gateway)."""
        api_token = _get_api_token(profile)
        if not api_token:
            print("[ModelProvider] No API token found, falling back to mock")
            async for event in self._mock_stream(messages, tools):
                yield event
            return

        base_url = profile.base_url or get_settings().anthropic_base_url
        model = profile.model

        # Extract system message if present
        system_prompt = None
        filtered_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
            else:
                filtered_messages.append(msg)

        # Build request payload
        payload = {
            "model": model,
            "max_tokens": profile.max_tokens,
            "messages": filtered_messages,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt

        # Add tools if provided
        if tools:
            payload["tools"] = tools

        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_token,
            "anthropic-version": "2023-06-01",
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/v1/messages",
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        print(f"[ModelProvider] API error {response.status_code}: {error_text}")
                        # Fallback to mock on error
                        async for event in self._mock_stream(messages, tools):
                            yield event
                        return

                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if not data_str or data_str == "[DONE]":
                            continue
                        try:
                            event_data = json.loads(data_str)
                            event_type = event_data.get("type")

                            if event_type == "message_start":
                                yield {"type": "message_start", "data": event_data.get("message", {})}
                            elif event_type == "content_block_start":
                                yield {"type": "content_block_start", "data": event_data}
                            elif event_type == "content_block_delta":
                                delta = event_data.get("delta", {})
                                yield {"type": "content_block_delta", "data": {"delta": delta}}
                            elif event_type == "content_block_stop":
                                yield {"type": "content_block_stop", "data": {}}
                            elif event_type == "message_delta":
                                yield {"type": "message_delta", "data": event_data.get("delta", {})}
                            elif event_type == "message_stop":
                                yield {"type": "message_stop", "data": {}}
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"[ModelProvider] Request failed: {e}")
            async for event in self._mock_stream(messages, tools):
                yield event

    async def _stream_openai(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]],
        profile: ModelProfile,
    ) -> AsyncGenerator[Dict, None]:
        """Stream from OpenAI-compatible API."""
        api_key = os.environ.get(profile.api_key_env, "")
        if not api_key:
            # Mock: simulate streaming response
            async for event in self._mock_stream(messages, tools):
                yield event
            return

        # TODO: implement real OpenAI API call
        async for event in self._mock_stream(messages, tools):
            yield event

    async def _mock_stream(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]],
    ) -> AsyncGenerator[Dict, None]:
        """Mock streaming for development/demo."""
        # Get last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            return

        user_lower = user_message.lower()

        # Simulate thinking
        yield {"type": "message_start", "data": {"id": f"msg_{uuid.uuid4().hex[:8]}"}}

        # Determine if we need to call a tool based on user message
        tool_name = None
        tool_input: Dict[str, Any] = {}

        if any(kw in user_lower for kw in ["日程", "会议", "安排", "calendar", "schedule"]):
            tool_name = "schedule"
            tool_input = {"action": "list"}
        elif any(kw in user_lower for kw in ["待办", "任务", "todo", "task"]):
            tool_name = "todo"
            tool_input = {"action": "list"}
        elif any(kw in user_lower for kw in ["摘要", "总结", "summarize", "summary"]):
            tool_name = "doc_summary"
            tool_input = {"document_id": "doc_123", "max_points": 5}
        elif any(kw in user_lower for kw in ["邮件", "email", "写邮件"]):
            tool_name = "email_draft"
            tool_input = {"to": "example@example.com", "intent": user_message, "subject": "主题"}
        elif any(kw in user_lower for kw in ["搜索", "知识库", "search", "知识"]):
            tool_name = "knowledge_search"
            tool_input = {"query": user_message, "limit": 3}
        elif any(kw in user_lower for kw in ["会议纪要", "meeting notes"]):
            tool_name = "meeting_notes"
            tool_input = {"document_id": "meeting_123", "extract_actions": True}

        if tool_name and tools:
            # First emit some text
            text_responses = {
                "schedule": "好的，让我查看一下您的日程安排。",
                "todo": "让我查看一下您的待办事项。",
                "doc_summary": "我来为您总结这份文档。",
                "email_draft": "我来帮您起草邮件。",
                "knowledge_search": "让我在知识库中搜索相关信息。",
                "meeting_notes": "我来整理这份会议纪要。",
            }
            response_text = text_responses.get(tool_name, "好的，让我来处理。")

            for char in response_text:
                yield {"type": "content_block_delta", "data": {"delta": {"text": char}}}
                await asyncio.sleep(0.02)

            yield {"type": "content_block_stop", "data": {}}

            # Then call the tool
            yield {
                "type": "content_block_start",
                "data": {"content_block": {"type": "tool_use", "id": f"tool_{uuid.uuid4().hex[:8]}", "name": tool_name}}}

            # Serialize tool input
            input_str = json.dumps(tool_input)
            for char in input_str:
                yield {"type": "content_block_delta", "data": {"delta": {"type": "input_json_delta", "input": char}}}

            yield {"type": "content_block_stop", "data": {}}
            yield {"type": "message_delta", "data": {"usage": {"output_tokens": 50, "input_tokens": 100}}}
            yield {"type": "message_stop", "data": {}}
        else:
            # Simple text response
            response_text = "好的，我可以帮助您管理日程、待办、文档摘要、邮件草稿、会议纪要和知识库检索。请告诉我您需要什么帮助？"

            for char in response_text:
                yield {"type": "content_block_delta", "data": {"delta": {"text": char}}}
                await asyncio.sleep(0.02)

            yield {"type": "content_block_stop", "data": {}}
            yield {"type": "message_delta", "data": {"usage": {"output_tokens": 50, "input_tokens": 100}}}
            yield {"type": "message_stop", "data": {}}