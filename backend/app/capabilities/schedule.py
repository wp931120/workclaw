"""Schedule capability - calendar and scheduling assistant."""

from app.capabilities.base import Capability, CapabilityContext, CapabilityResult, CapabilityCategory
from datetime import datetime, timedelta
from typing import Any


class ScheduleCapability(Capability):
    """Schedule capability for calendar management."""

    name = "schedule"
    description = "Manage calendar events - check availability, create meetings, schedule events"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["check", "create", "list", "update", "delete"], "description": "The action to perform"},
            "title": {"type": "string", "description": "Event title"},
            "description": {"type": "string", "description": "Event description"},
            "start_time": {"type": "string", "description": "Start time in ISO format"},
            "end_time": {"type": "string", "description": "End time in ISO format"},
            "event_id": {"type": "string", "description": "Event ID for update/delete actions"},
        },
        "required": ["action"],
    }
    category = CapabilityCategory.schedule

    async def call(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        action = input.get("action", "list")

        # Mock implementation - TODO: integrate with real calendar (Google/Outlook)
        if action == "check":
            return await self._check_availability(input, context)
        elif action == "create":
            return await self._create_event(input, context)
        elif action == "list":
            return await self._list_events(input, context)
        elif action == "update":
            return await self._update_event(input, context)
        elif action == "delete":
            return await self._delete_event(input, context)
        else:
            return {"success": False, "error": f"Unknown action: {action}", "content": ""}

    async def _check_availability(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        return {
            "success": True,
            "content": "时间段可用，没有冲突。",
            "data": {"available": True, "conflicts": []},
        }

    async def _create_event(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        event_id = f"evt_{hash(input.get('title', ''))}"
        return {
            "success": True,
            "content": f"已创建日程: {input.get('title', '新日程')}",
            "data": {"event_id": event_id, "status": "created"},
        }

    async def _list_events(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        return {
            "success": True,
            "content": "今日日程:\n- 10:00 团队会议\n- 14:00 项目评审",
            "data": {"events": [{"title": "团队会议", "time": "10:00"}, {"title": "项目评审", "time": "14:00"}]},
        }

    async def _update_event(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        return {
            "success": True,
            "content": f"已更新日程: {input.get('title', '')}",
            "data": {"status": "updated"},
        }

    async def _delete_event(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        return {
            "success": True,
            "content": "已删除日程",
            "data": {"status": "deleted"},
        }

    def is_dangerous(self) -> bool:
        return False


class TodoCapability(Capability):
    """Todo capability for task management."""

    name = "todo"
    description = "Manage todo items - create, list, update, complete, delete tasks"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "list", "update", "complete", "delete"], "description": "The action to perform"},
            "title": {"type": "string", "description": "Task title"},
            "description": {"type": "string", "description": "Task description"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Task priority"},
            "due_date": {"type": "string", "description": "Due date in ISO format"},
            "task_id": {"type": "string", "description": "Task ID for update/complete/delete"},
        },
        "required": ["action"],
    }
    category = CapabilityCategory.todo

    async def call(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        action = input.get("action", "list")

        if action == "create":
            return await self._create_task(input, context)
        elif action == "list":
            return await self._list_tasks(input, context)
        elif action == "update":
            return await self._update_task(input, context)
        elif action == "complete":
            return await self._complete_task(input, context)
        elif action == "delete":
            return await self._delete_task(input, context)
        else:
            return {"success": False, "error": f"Unknown action: {action}", "content": ""}

    async def _create_task(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        task_id = f"task_{hash(input.get('title', ''))}"
        return {
            "success": True,
            "content": f"已创建待办: {input.get('title', '新任务')}",
            "data": {"task_id": task_id, "status": "created"},
        }

    async def _list_tasks(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        return {
            "success": True,
            "content": "当前待办:\n- [高] 完成项目报告\n- [中] 回复邮件\n- [低] 整理文档",
            "data": {"tasks": [{"title": "完成项目报告", "priority": "high"}, {"title": "回复邮件", "priority": "medium"}]},
        }

    async def _update_task(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        return {
            "success": True,
            "content": f"已更新待办: {input.get('title', '')}",
            "data": {"status": "updated"},
        }

    async def _complete_task(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        return {
            "success": True,
            "content": "已完成任务",
            "data": {"status": "completed"},
        }

    async def _delete_task(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        return {
            "success": True,
            "content": "已删除任务",
            "data": {"status": "deleted"},
        }

    def is_dangerous(self) -> bool:
        return False