"""Skills API - manage user skill preferences."""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.models.database import async_session_factory
from app.models.skill import Skill
from app.capabilities.registry import get_capability_registry

router = APIRouter()


def _use_db() -> bool:
    """Check if database is available."""
    return async_session_factory is not None


# Pydantic models for API
class SkillResponse(BaseModel):
    id: str
    name: str
    title: str
    description: str
    category: str
    enabled: bool
    read_only: bool
    is_dangerous: bool
    icon: Optional[str] = None


class SkillUpdate(BaseModel):
    enabled: Optional[bool] = None


class SkillListResponse(BaseModel):
    skills: List[SkillResponse]
    count: int


# Mapping of capability name to display title and icon
CAPABILITY_DISPLAY_INFO: dict[str, dict] = {
    "schedule": {"title": "日程管理", "icon": "calendar"},
    "todo": {"title": "待办任务", "icon": "check"},
    "doc_summary": {"title": "文档摘要", "icon": "file-text"},
    "email_draft": {"title": "邮件起草", "icon": "mail"},
    "meeting_notes": {"title": "会议纪要", "icon": "users"},
    "knowledge_search": {"title": "知识搜索", "icon": "search"},
    "file_parse": {"title": "文件解析", "icon": "file"},
}


def _get_display_info(capability_name: str) -> dict:
    """Get display title and icon for a capability."""
    return CAPABILITY_DISPLAY_INFO.get(capability_name, {"title": capability_name, "icon": "tool"})


async def _ensure_skills_initialized() -> None:
    """Ensure all capabilities have corresponding skill entries in DB."""
    if not _use_db():
        return

    registry = get_capability_registry()
    capabilities = registry.list_all()

    async with async_session_factory() as session:
        for cap in capabilities:
            # Check if skill exists
            from sqlmodel import select
            stmt = select(Skill).where(Skill.name == cap.name)
            result = await session.exec(stmt)
            existing = result.first()

            if not existing:
                # Create skill entry
                skill = Skill(name=cap.name, enabled=True, user_scope="dev_user")
                session.add(skill)

        await session.commit()


@router.get("", response_model=SkillListResponse)
async def list_skills():
    """List all skills with their current enabled status."""
    await _ensure_skills_initialized()

    registry = get_capability_registry()
    capabilities = registry.list_all()

    if _use_db():
        from sqlmodel import select
        async with async_session_factory() as session:
            stmt = select(Skill).where(Skill.user_scope == "dev_user")
            result = await session.exec(stmt)
            db_skills = {s.name: s for s in result.all()}

            skills = []
            for cap in capabilities:
                display_info = _get_display_info(cap.name)
                skill_db = db_skills.get(cap.name)

                skills.append(SkillResponse(
                    id=str(skill_db.id) if skill_db else "",
                    name=cap.name,
                    title=display_info["title"],
                    description=cap.description,
                    category=cap.category,
                    enabled=skill_db.enabled if skill_db else True,
                    read_only=cap.is_read_only,
                    is_dangerous=cap.is_dangerous,
                    icon=display_info["icon"],
                ))

            return {"skills": skills, "count": len(skills)}
    else:
        # In-memory fallback
        skills = []
        for cap in capabilities:
            display_info = _get_display_info(cap.name)
            skills.append(SkillResponse(
                id=cap.name,
                name=cap.name,
                title=display_info["title"],
                description=cap.description,
                category=cap.category,
                enabled=True,
                read_only=cap.is_read_only,
                is_dangerous=cap.is_dangerous,
                icon=display_info["icon"],
            ))

        return {"skills": skills, "count": len(skills)}


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str):
    """Get a single skill by ID or name."""
    await _ensure_skills_initialized()

    registry = get_capability_registry()
    capabilities = registry.list_all()

    # Try to find capability by name first
    cap = registry.find(skill_id)
    skill_db = None

    if not cap and _use_db():
        # Try as UUID
        try:
            skill_uuid = uuid.UUID(skill_id)
            from sqlmodel import select
            async with async_session_factory() as session:
                stmt = select(Skill).where(Skill.id == skill_uuid, Skill.user_scope == "dev_user")
                result = await session.exec(stmt)
                skill_db = result.first()
                if skill_db:
                    cap = registry.find(skill_db.name)
        except ValueError:
            pass

    if not cap:
        raise HTTPException(status_code=404, detail="Skill not found")

    display_info = _get_display_info(cap.name)

    # Get enabled status from DB
    enabled = True
    if _use_db():
        from sqlmodel import select
        async with async_session_factory() as session:
            stmt = select(Skill).where(Skill.name == cap.name, Skill.user_scope == "dev_user")
            result = await session.exec(stmt)
            skill_record = result.first()
            if skill_record:
                enabled = skill_record.enabled

    return SkillResponse(
        id=str(skill_db.id) if skill_db else skill_id,
        name=cap.name,
        title=display_info["title"],
        description=cap.description,
        category=cap.category,
        enabled=enabled,
        read_only=cap.is_read_only,
        is_dangerous=cap.is_dangerous,
        icon=display_info["icon"],
    )


@router.patch("/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: str, update: SkillUpdate):
    """Update a skill (currently only enabled status)."""
    await _ensure_skills_initialized()

    registry = get_capability_registry()
    skill_db = None
    cap = None

    if _use_db():
        from sqlmodel import select

        # First try as name
        async with async_session_factory() as session:
            stmt = select(Skill).where(Skill.name == skill_id, Skill.user_scope == "dev_user")
            result = await session.exec(stmt)
            skill_db = result.first()

            # If not found, try as UUID
            if not skill_db:
                try:
                    skill_uuid = uuid.UUID(skill_id)
                    stmt = select(Skill).where(Skill.id == skill_uuid, Skill.user_scope == "dev_user")
                    result = await session.exec(stmt)
                    skill_db = result.first()
                except ValueError:
                    pass

        if not skill_db:
            raise HTTPException(status_code=404, detail="Skill not found")

        # Update enabled status if provided
        if update.enabled is not None:
            async with async_session_factory() as session:
                # Re-fetch for update
                from sqlmodel import select
                stmt = select(Skill).where(Skill.id == skill_db.id)
                result = await session.exec(stmt)
                skill_db = result.first()

                if skill_db:
                    skill_db.enabled = update.enabled
                    skill_db.updated_at = datetime.utcnow()
                    await session.commit()
                    await session.refresh(skill_db)

        cap = registry.find(skill_db.name)
    else:
        raise HTTPException(status_code=503, detail="Database not available")

    if not cap:
        raise HTTPException(status_code=404, detail="Capability not found")

    display_info = _get_display_info(cap.name)

    return SkillResponse(
        id=str(skill_db.id),
        name=cap.name,
        title=display_info["title"],
        description=cap.description,
        category=cap.category,
        enabled=skill_db.enabled,
        read_only=cap.is_read_only,
        is_dangerous=cap.is_dangerous,
        icon=display_info["icon"],
    )


@router.post("/{skill_id}/toggle", response_model=SkillResponse)
async def toggle_skill(skill_id: str):
    """Toggle a skill's enabled status."""
    # First get current state
    try:
        skill = await get_skill(skill_id)
    except HTTPException:
        raise

    # Toggle
    new_enabled = not skill.enabled

    # Use update endpoint
    update = SkillUpdate(enabled=new_enabled)
    return await update_skill(skill_id, update)