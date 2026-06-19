"""Auth API - simplified local auth for development."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config.settings import get_settings
import hashlib
from typing import Optional, Dict

router = APIRouter()


class TokenRequest(BaseModel):
    email: Optional[str] = None  # Optional for local dev


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict


@router.post("/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    """Get access token (simplified local dev auth)."""
    settings = get_settings()

    # In local dev mode, accept any email or use default
    email = request.email or settings.default_user_email

    # Generate a simple token (for dev only - real app would use proper JWT)
    token_data = f"{email}:{settings.secret_key}"
    token_hash = hashlib.sha256(token_data.encode()).hexdigest()[:32]

    return TokenResponse(
        access_token=token_hash,
        user={
            "email": email,
            "name": email.split("@")[0],
            "role": "user",
        },
    )