"""Chat API with SSE streaming."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import uuid

from app.core.orchestrator import SessionOrchestrator
from app.core.agentic_loop import AgenticLoop
from app.services.model_provider import ModelProvider
from app.capabilities.registry import get_capability_registry

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class SessionCreateRequest(BaseModel):
    title: str = "New Session"
    model_profile: str = "anthropic"
    permission_mode: str = "moderate"


# In-memory session storage (replace with DB in production)
_sessions: Dict[str, Dict] = {}
_messages: Dict[str, List[Dict]] = {}


@router.post("/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new session."""
    orchestrator = SessionOrchestrator()
    session = await orchestrator.create_session(
        user_id="dev_user",
        title=request.title,
        model_profile=request.model_profile,
        permission_mode=request.permission_mode,
    )
    session_id = session["id"]
    _sessions[session_id] = session
    _messages[session_id] = []
    return session


@router.get("/sessions")
async def list_sessions():
    """List all sessions."""
    return list(_sessions.values())


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a session by ID."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    del _sessions[session_id]
    if session_id in _messages:
        del _messages[session_id]
    return {"status": "deleted"}


@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    """Get messages for a session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return _messages.get(session_id, [])


@router.post("/sessions/{session_id}/chat")
async def chat(session_id: str, request: ChatRequest):
    """Send a message and get streaming response."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[session_id]
    messages = _messages.setdefault(session_id, [])

    # Get available capabilities
    registry = get_capability_registry()
    capabilities = [cap.to_dict() for cap in registry.list_all()]

    # Build system prompt
    orchestrator = SessionOrchestrator()
    system_prompt = await orchestrator.build_system_prompt(
        user_name="Dev User",
        available_capabilities=capabilities,
    )

    # Prepare messages
    all_messages = await orchestrator.prepare_messages(
        session_id=session_id,
        user_input=request.message,
        system_prompt=system_prompt,
        history=messages,
    )

    # Add user message
    all_messages.append({"role": "user", "content": request.message})

    # Create agentic loop
    model_provider = ModelProvider()
    agentic_loop = AgenticLoop(
        model_provider=model_provider,
        permission_mode=session.get("permission_mode", "moderate"),
    )

    # Stream response
    full_text = []

    async def event_generator():
        nonlocal full_text

        async for event in agentic_loop.query(
            messages=all_messages,
            user_id="dev_user",
            session_id=session_id,
        ):
            event_type = event.get("type")
            data = event.get("data", {})

            if event_type == "text_delta":
                text = data.get("content", "")
                full_text.append(text)
                yield f"event: text_delta\ndata: {json.dumps({'content': text})}\n\n"

            elif event_type == "capability_call":
                yield f"event: capability_call\ndata: {json.dumps(data)}\n\n"

            elif event_type == "capability_result":
                # Add capability result to content
                result = data.get("result", {})
                if result.get("content"):
                    full_text.append(f"\n\n{result['content']}")
                yield f"event: capability_result\ndata: {json.dumps(data)}\n\n"

            elif event_type == "usage":
                yield f"event: usage\ndata: {json.dumps(data)}\n\n"

            elif event_type == "done":
                # Save messages to history
                messages.append({"role": "user", "content": request.message})
                messages.append({"role": "assistant", "content": "".join(full_text)})
                yield f"event: done\ndata: {json.dumps({'message_id': str(uuid.uuid4())})}\n\n"

            elif event_type == "error":
                yield f"event: error\ndata: {json.dumps(data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )