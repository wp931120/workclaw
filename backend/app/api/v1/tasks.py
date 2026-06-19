"""Tasks API - manage tasks/todos."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from enum import Enum

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


# In-memory task storage
_tasks: dict[str, dict] = {}


@router.get("/tasks")
async def list_tasks(status: Optional[TaskStatus] = None):
    """List all tasks, optionally filtered by status."""
    tasks = list(_tasks.values())
    if status:
        tasks = [t for t in tasks if t["status"] == status.value]
    return {"tasks": tasks, "count": len(tasks)}


@router.post("/tasks")
async def create_task(request: TaskCreate):
    """Create a new task."""
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "user_id": "dev_user",
        "title": request.title,
        "description": request.description,
        "status": TaskStatus.pending.value,
        "priority": request.priority.value,
        "due_date": request.due_date,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    _tasks[task_id] = task
    return task


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a task by ID."""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, request: TaskUpdate):
    """Update a task."""
    task = _tasks.get(task_id)
    if not task:
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
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del _tasks[task_id]
    return {"status": "deleted"}