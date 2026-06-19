"""Chat API with SSE streaming and persistent storage."""

import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import uuid
from datetime import datetime
from sqlmodel import select, desc

from app.core.orchestrator import SessionOrchestrator
from app.core.agentic_loop import AgenticLoop
from app.services.model_provider import ModelProvider
from app.capabilities.registry import get_capability_registry
from app.models.database import async_session_factory
from app.models.user import User, UserRole
from app.models.session import Session as DBSession, SessionStatus, PermissionMode
from app.models.message import Message, MessageRole

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class SessionCreateRequest(BaseModel):
    title: str = "New Session"
    model_profile: str = "claude-glm-5.1"
    permission_mode: str = "moderate"


# In-memory fallback for tests when DB not initialized
_sessions: Dict[str, Dict] = {}
_messages: Dict[str, List[Dict]] = {}
_cached_dev_user: Optional[User] = None


async def get_dev_user() -> User:
    """Get or create the dev user for local development."""
    global _cached_dev_user

    if async_session_factory is None:
        # Fallback for tests - use cached mock user
        if _cached_dev_user is None:
            _cached_dev_user = User(id=uuid.uuid4(), email="dev@workclaw.local", name="Dev User")
        return _cached_dev_user
    async with async_session_factory() as session:
        stmt = select(User).where(User.email == "dev@workclaw.local")
        result = await session.exec(stmt)
        user = result.first()
        if user:
            return user
        # Create if not exists
        user = User(email="dev@workclaw.local", name="Dev User", role=UserRole.admin)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


def _use_db() -> bool:
    """Check if database is available."""
    return async_session_factory is not None


@router.post("/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new session."""
    user = await get_dev_user()

    if _use_db():
        async with async_session_factory() as session:
            db_session = DBSession(
                user_id=user.id,
                title=request.title,
                model_profile=request.model_profile,
                permission_mode=PermissionMode(request.permission_mode),
                status=SessionStatus.active,
            )
            session.add(db_session)
            await session.commit()
            await session.refresh(db_session)

            return {
                "id": str(db_session.id),
                "user_id": str(db_session.user_id),
                "title": db_session.title,
                "model_profile": db_session.model_profile,
                "permission_mode": db_session.permission_mode.value,
                "status": db_session.status.value,
                "created_at": db_session.created_at.isoformat(),
                "updated_at": db_session.updated_at.isoformat(),
            }
    else:
        # In-memory fallback
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        session = {
            "id": session_id,
            "user_id": str(user.id),
            "title": request.title,
            "model_profile": request.model_profile,
            "permission_mode": request.permission_mode,
            "status": "active",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        _sessions[session_id] = session
        _messages[session_id] = []
        return session


@router.get("/sessions")
async def list_sessions():
    """List all sessions for the dev user."""
    user = await get_dev_user()

    if _use_db():
        async with async_session_factory() as session:
            stmt = (
                select(DBSession)
                .where(DBSession.user_id == user.id)
                .order_by(desc(DBSession.updated_at))
            )
            result = await session.exec(stmt)
            sessions = result.all()

            return [
                {
                    "id": str(s.id),
                    "user_id": str(s.user_id),
                    "title": s.title,
                    "model_profile": s.model_profile,
                    "permission_mode": s.permission_mode.value,
                    "status": s.status.value,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                }
                for s in sessions
            ]
    else:
        # In-memory fallback
        user_sessions = [s for s in _sessions.values() if s["user_id"] == str(user.id)]
        return sorted(user_sessions, key=lambda x: x["updated_at"], reverse=True)


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a session by ID."""
    user = await get_dev_user()

    if _use_db():
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID")

        async with async_session_factory() as session:
            stmt = select(DBSession).where(
                DBSession.id == session_uuid,
                DBSession.user_id == user.id,
            )
            result = await session.exec(stmt)
            db_session = result.first()

            if not db_session:
                raise HTTPException(status_code=404, detail="Session not found")

            return {
                "id": str(db_session.id),
                "user_id": str(db_session.user_id),
                "title": db_session.title,
                "model_profile": db_session.model_profile,
                "permission_mode": db_session.permission_mode.value,
                "status": db_session.status.value,
                "created_at": db_session.created_at.isoformat(),
                "updated_at": db_session.updated_at.isoformat(),
            }
    else:
        # In-memory fallback
        session = _sessions.get(session_id)
        if not session or session["user_id"] != str(user.id):
            raise HTTPException(status_code=404, detail="Session not found")
        return session


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    user = await get_dev_user()

    if _use_db():
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID")

        async with async_session_factory() as session:
            stmt = select(DBSession).where(
                DBSession.id == session_uuid,
                DBSession.user_id == user.id,
            )
            result = await session.exec(stmt)
            db_session = result.first()

            if not db_session:
                raise HTTPException(status_code=404, detail="Session not found")

            # Delete associated messages
            stmt = select(Message).where(Message.session_id == session_uuid)
            messages = await session.exec(stmt)
            for msg in messages.all():
                await session.delete(msg)

            await session.delete(db_session)
            await session.commit()

            return {"status": "deleted"}
    else:
        # In-memory fallback
        session = _sessions.get(session_id)
        if not session or session["user_id"] != str(user.id):
            raise HTTPException(status_code=404, detail="Session not found")
        del _sessions[session_id]
        if session_id in _messages:
            del _messages[session_id]
        return {"status": "deleted"}


@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    """Get messages for a session."""
    user = await get_dev_user()

    if _use_db():
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID")

        async with async_session_factory() as session:
            # Verify session belongs to user
            stmt = select(DBSession).where(
                DBSession.id == session_uuid,
                DBSession.user_id == user.id,
            )
            result = await session.exec(stmt)
            if not result.first():
                raise HTTPException(status_code=404, detail="Session not found")

            # Get messages
            stmt = (
                select(Message)
                .where(Message.session_id == session_uuid)
                .order_by(Message.created_at)
            )
            result = await session.exec(stmt)
            messages = result.all()

            return [
                {
                    "id": str(m.id),
                    "session_id": str(m.session_id),
                    "role": m.role.value,
                    "content": m.content,
                    "tool_calls": m.tool_calls,
                    "tool_call_id": m.tool_call_id,
                    "model_usage": m.model_usage,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
                if m.content
            ]
    else:
        # In-memory fallback
        session = _sessions.get(session_id)
        if not session or session["user_id"] != str(user.id):
            raise HTTPException(status_code=404, detail="Session not found")
        return _messages.get(session_id, [])


@router.post("/sessions/{session_id}/chat")
async def chat(session_id: str, request: ChatRequest):
    """Send a message and get streaming response."""
    user = await get_dev_user()

    # Validate session
    if _use_db():
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID")

        async with async_session_factory() as session:
            stmt = select(DBSession).where(
                DBSession.id == session_uuid,
                DBSession.user_id == user.id,
            )
            result = await session.exec(stmt)
            db_session = result.first()

            if not db_session:
                raise HTTPException(status_code=404, detail="Session not found")

            # Get existing messages
            stmt = (
                select(Message)
                .where(Message.session_id == session_uuid)
                .order_by(Message.created_at)
            )
            result = await session.exec(stmt)
            db_messages = result.all()

            history = []
            for m in db_messages:
                msg_dict = {"role": m.role.value, "content": m.content}
                if m.tool_calls:
                    msg_dict["tool_calls"] = m.tool_calls
                if m.tool_call_id:
                    msg_dict["tool_call_id"] = m.tool_call_id
                history.append(msg_dict)

            model_profile = db_session.model_profile
            permission_mode = db_session.permission_mode.value
    else:
        # In-memory fallback
        session = _sessions.get(session_id)
        if not session or session["user_id"] != str(user.id):
            raise HTTPException(status_code=404, detail="Session not found")

        history = _messages.get(session_id, [])
        model_profile = session.get("model_profile", "claude-glm-5.1")
        permission_mode = session.get("permission_mode", "moderate")

    # Get available capabilities
    registry = get_capability_registry()
    capabilities = [cap.to_dict() for cap in registry.list_all()]

    # Build system prompt
    orchestrator = SessionOrchestrator()
    system_prompt = await orchestrator.build_system_prompt(
        user_name=user.name or "Dev User",
        available_capabilities=capabilities,
    )

    # Prepare messages
    prepared = await orchestrator.prepare_messages(
        session_id=session_id,
        user_input=request.message,
        system_prompt=system_prompt,
        history=history,
    )

    # Create agentic loop
    model_provider = ModelProvider()
    agentic_loop = AgenticLoop(
        model_provider=model_provider,
        permission_mode=permission_mode,
    )

    # Stream response
    full_text = []
    message_id = str(uuid.uuid4())

    async def event_generator():
        nonlocal full_text

        # Save user message
        if _use_db():
            async with async_session_factory() as session:
                session_uuid = uuid.UUID(session_id)
                user_msg = Message(
                    session_id=session_uuid,
                    role=MessageRole.user,
                    content=request.message,
                )
                session.add(user_msg)
                await session.commit()
        else:
            _messages.setdefault(session_id, []).append({
                "role": "user",
                "content": request.message,
            })

        async for event in agentic_loop.query(
            messages=prepared["messages"],
            system=prepared["system"],
            user_id=str(user.id),
            session_id=session_id,
            model_profile=model_profile,
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
                result = data.get("result", {})
                if result.get("content"):
                    full_content = f"\n\n{result['content']}"
                    full_text.append(full_content)
                yield f"event: capability_result\ndata: {json.dumps(data)}\n\n"

            elif event_type == "usage":
                yield f"event: usage\ndata: {json.dumps(data)}\n\n"

            elif event_type == "done":
                # Save assistant message
                if _use_db():
                    async with async_session_factory() as session:
                        session_uuid = uuid.UUID(session_id)
                        assistant_msg = Message(
                            session_id=session_uuid,
                            role=MessageRole.assistant,
                            content="".join(full_text),
                        )
                        session.add(assistant_msg)

                        # Update session timestamp
                        stmt = select(DBSession).where(DBSession.id == session_uuid)
                        result = await session.exec(stmt)
                        db_session = result.first()
                        if db_session:
                            db_session.updated_at = datetime.utcnow()
                            if db_session.title == "New Session" and request.message:
                                db_session.title = request.message[:50]

                        await session.commit()
                else:
                    _messages.setdefault(session_id, []).append({
                        "role": "assistant",
                        "content": "".join(full_text),
                    })
                    session = _sessions.get(session_id)
                    if session:
                        session["updated_at"] = datetime.utcnow().isoformat()
                        if session["title"] == "New Session" and request.message:
                            session["title"] = request.message[:50]

                yield f"event: done\ndata: {json.dumps({'message_id': message_id, 'usage': data.get('usage', {})})}\n\n"

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