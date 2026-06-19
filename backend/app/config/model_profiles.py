"""Model profile definitions for multi-provider support."""

from pydantic import BaseModel
from typing import Literal, Optional, Dict


class ModelProfile(BaseModel):
    """A model profile defines how to connect to a specific LLM provider."""

    id: str
    protocol: Literal["anthropic", "openai-chat"]
    model: str
    base_url: Optional[str] = None
    api_key_env: str  # Environment variable name for API key/token
    max_tokens: int = 4096


# Built-in model profiles
BUILTIN_PROFILES: Dict[str, ModelProfile] = {
    "claude-glm-5.1": ModelProfile(
        id="claude-glm-5.1",
        protocol="anthropic",
        model="glm-5.1",
        base_url="https://aigw-gzgy2.cucloud.cn:8443",
        api_key_env="WORKCLAW_ANTHROPIC_AUTH_TOKEN",
    ),
    "anthropic": ModelProfile(
        id="anthropic",
        protocol="anthropic",
        model="glm-5.1",
        base_url="https://aigw-gzgy2.cucloud.cn:8443",
        api_key_env="WORKCLAW_ANTHROPIC_AUTH_TOKEN",
    ),
    "openai": ModelProfile(
        id="openai",
        protocol="openai-chat",
        model="gpt-4o",
        api_key_env="WORKCLAW_OPENAI_API_KEY",
    ),
}


def get_profile(profile_id: str) -> Optional[ModelProfile]:
    return BUILTIN_PROFILES.get(profile_id)