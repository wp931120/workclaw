"""Session orchestrator - manages multi-turn conversations (inspired by Easy Agent QueryEngine)."""

from datetime import datetime
from typing import AsyncGenerator
import uuid


class SessionOrchestrator:
    """
    Manages multi-turn conversation sessions.

    This is the "QueryEngine" of WorkClaw - it manages conversation state,
    builds system prompts, handles session lifecycle, and orchestrates the agentic loop.
    """

    def __init__(self):
        pass

    async def create_session(
        self,
        user_id: str,
        title: str = "New Session",
        model_profile: str = "anthropic",
        permission_mode: str = "moderate",
    ) -> dict:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        return {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "model_profile": model_profile,
            "permission_mode": permission_mode,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

    async def build_system_prompt(
        self,
        user_name: str,
        available_capabilities: list[dict],
    ) -> str:
        """Build the system prompt with identity, context, and available capabilities."""
        capabilities_text = "\n".join([
            f"- {cap['name']}: {cap['description']}"
            for cap in available_capabilities
        ])
        prompt = f"""你是 WorkClaw，一个专业的 AI 办公助手。你的目标是通过对话式交互，帮助用户完成日常办公任务。

当前用户: {user_name}
可用能力:
{capabilities_text}

使用指南:
1. 用户请求涉及日程、待办、文档等操作时，使用相应的能力
2. 对于需要用户确认的操作（如发送邮件），明确告知需要确认
3. 保持回答简洁、专业、友好
4. 如果用户请求的能力不可用或遇到错误，清晰告知原因

现在开始帮助��户。
"""
        return prompt

    async def prepare_messages(
        self,
        session_id: str,
        user_input: str,
        system_prompt: str,
        history: list[dict],
    ) -> list[dict]:
        """Prepare messages for the LLM, including system prompt and history."""
        messages = [{"role": "system", "content": system_prompt}]
        # Add history (truncated if needed)
        for msg in history[-20:]:  # Last 20 messages
            messages.append(msg)
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        return messages