"""Tasks API - manage tasks/todos with database persistence."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from enum import Enum
from sqlmodel import select

from app.models.database import async_session_factory
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority

router = APIRouter()


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = None


# In-memory fallback for tests when DB not initialized
_tasks: dict[str, dict] = {}


def _use_db() -> bool:
    """Check if database is available."""
    return async_session_factory is not None


async def get_dev_user_id() -> str:
    """Get the dev user ID for local development."""
    if async_session_factory is None:
        return "dev_user"

    async with async_session_factory() as session:
        stmt = select(User).where(User.email == "dev@workclaw.local")
        result = await session.exec(stmt)
        user = result.first()
        if user:
            return str(user.id)

        # Create dev user if not exists
        user = User(email="dev@workclaw.local", name="Dev User")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return str(user.id)


@router.get("/tasks")
async def list_tasks(status: Optional[TaskStatus] = None):
    """List all tasks, optionally filtered by status."""
    user_id = await get_dev_user_id()

    if _use_db():
        async with async_session_factory() as session:
            stmt = select(Task).where(Task.user_id == uuid.UUID(user_id))
            if status:
                stmt = stmt.where(Task.status == TaskStatus(status.value))
            stmt = stmt.order_by(Task.created_at.desc())
            result = await session.exec(stmt)
            tasks = result.all()

            return {
                "tasks": [
                    {
                        "id": str(t.id),
                        "user_id": str(t.user_id),
                        "title": t.title,
                        "description": t.description,
                        "status": t.status.value,
                        "priority": t.priority.value,
                        "due_date": t.due_date.isoformat() if t.due_date else None,
                        "created_at": t.created_at.isoformat(),
                        "updated_at": t.updated_at.isoformat(),
                    }
                    for t in tasks
                ],
                "count": len(tasks),
            }
    else:
        # In-memory fallback
        user_tasks = [t for t in _tasks.values() if t["user_id"] == user_id]
        if status:
            user_tasks = [t for t in user_tasks if t["status"] == status.value]
        return {"tasks": user_tasks, "count": len(user_tasks)}


@router.post("/tasks")
async def create_task(request: TaskCreate):
    """Create a new task."""
    user_id = await get_dev_user_id()

    if _use_db():
        async with async_session_factory() as session:
            task = Task(
                user_id=uuid.UUID(user_id),
                title=request.title,
                description=request.description,
                priority=TaskPriority(request.priority.value),
                status=TaskStatus.pending,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
    else:
        # In-memory fallback
        task_id = str(uuid.uuid4())
        now = datetime.utcnow()
        task = {
            "id": task_id,
            "user_id": user_id,
            "title": request.title,
            "description": request.description,
            "status": TaskStatus.pending.value,
            "priority": request.priority.value,
            "due_date": request.due_date,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        _tasks[task_id] = task
        return task


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a task by ID."""
    user_id = await get_dev_user_id()

    if _use_db():
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task ID")

        async with async_session_factory() as session:
            stmt = select(Task).where(Task.id == task_uuid, Task.user_id == uuid.UUID(user_id))
            result = await session.exec(stmt)
            task = result.first()

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            return {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
    else:
        # In-memory fallback
        task = _tasks.get(task_id)
        if not task or task["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, request: TaskUpdate):
    """Update a task."""
    user_id = await get_dev_user_id()

    if _use_db():
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task ID")

        async with async_session_factory() as session:
            stmt = select(Task).where(Task.id == task_uuid, Task.user_id == uuid.UUID(user_id))
            result = await session.exec(stmt)
            task = result.first()

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            if request.title is not None:
                task.title = request.title
            if request.description is not None:
                task.description = request.description
            if request.status is not None:
                task.status = TaskStatus(request.status.value)
            if request.priority is not None:
                task.priority = TaskPriority(request.priority.value)
            if request.due_date is not None:
                task.due_date = datetime.fromisoformat(request.due_date)

            task.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(task)

            return {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
    else:
        # In-memory fallback
        task = _tasks.get(task_id)
        if not task or task["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Task not found")

        if request.title is not None:
            task["title"] = request.title
        if request.description is not None:
            task["description"] = request.description
        if request.status is not None:
            task["status"] = request.status.value
        if request.priority is not None:
            task["priority"] = request.priority.value
        if request.due_date is not None:
            task["due_date"] = request.due_date

        task["updated_at"] = datetime.utcnow().isoformat()
        return task


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task."""
    user_id = await get_dev_user_id()

    if _use_db():
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task ID")

        async with async_session_factory() as session:
            stmt = select(Task).where(Task.id == task_uuid, Task.user_id == uuid.UUID(user_id))
            result = await session.exec(stmt)
            task = result.first()

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            await session.delete(task)
            await session.commit()

            return {"status": "deleted"}
    else:
        # In-memory fallback
        task = _tasks.get(task_id)
        if not task or task["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Task not found")
        del _tasks[task_id]
        return {"status": "deleted"}