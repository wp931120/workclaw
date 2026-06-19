"""Document capabilities - summary and analysis."""

from app.capabilities.base import Capability, CapabilityContext, CapabilityResult, CapabilityCategory
from typing import Any


class DocSummaryCapability(Capability):
    """Document summary capability - summarize uploaded documents."""

    name = "doc_summary"
    description = "Summarize and extract key information from documents"
    input_schema = {
        "type": "object",
        "properties": {
            "document_id": {"type": "string", "description": "ID of the document to summarize"},
            "max_points": {"type": "number", "description": "Maximum number of key points to extract", "default": 5},
            "style": {"type": "string", "enum": ["brief", "detailed", "bullet"], "description": "Summary style", "default": "brief"},
        },
        "required": ["document_id"],
    }
    category = CapabilityCategory.document

    async def call(self, input: dict[str, Any], context: CapabilityContext) -> CapabilityResult:
        doc_id = input.get("document_id", "")
        max_points = input.get("max_points", 5)
        style = input.get("style", "brief")

        # Mock: generate summary
        # TODO: integrate with real document processing (PDF/TXT parsing + LLM summarization)
        summary_content = f"文档摘要 (ID: {doc_id}):\n\n这是一份关于项目进度的报告。主要内容包括：\n1. 当前项目状态良好\n2. 下一阶段计划已确定\n3. 风险点已识别并有应对措施\n\n共提取了 {max_points} 个关键点。"
        return {
            "success": True,
            "content": summary_content,
            "data": {"document_id": doc_id, "points_extracted": max_points, "style": style},
        }

    def is_read_only(self) -> bool:
        return True


class EmailDraftCapability(Capability):
    """Email draft capability - generate email drafts."""

    name = "email_draft"
    description = "Draft emails based on context and user intent"
    input_schema = {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "intent": {"type": "string", "description": "What the user wants to convey"},
            "tone": {"type": "string", "enum": ["formal", "casual", "friendly"], "description": "Email tone", "default": "formal"},
        },
        "required": ["to", "intent"],
    }
    category = CapabilityCategory.email

    async def call(self, input: dict[str, Any], context: CapabilityContext) -> CapabilityResult:
        to = input.get("to", "")
        subject = input.get("subject", "无主题")
        intent = input.get("intent", "")
        tone = input.get("tone", "formal")

        # Mock: generate draft
        # TODO: integrate with real email service (SMTP/Graph API)
        draft_content = f"""收件人: {to}
主题: {subject}

{intent}，

此致敬礼

[AI 草稿 - 请确认后发送]
"""
        return {
            "success": True,
            "content": f"已生成邮件草稿:\n{draft_content}",
            "data": {"to": to, "subject": subject, "tone": tone, "status": "draft"},
            "needs_approval": True,  # Sending emails requires approval
        }

    def is_dangerous(self) -> bool:
        return True  # Email sending is dangerous


class MeetingNotesCapability(Capability):
    """Meeting notes capability - generate and structure meeting notes."""

    name = "meeting_notes"
    description = "Summarize meeting notes and extract action items"
    input_schema = {
        "type": "object",
        "properties": {
            "document_id": {"type": "string", "description": "ID of meeting notes document"},
            "extract_actions": {"type": "boolean", "description": "Extract action items", "default": True},
            "create_tasks": {"type": "boolean", "description": "Create tasks from action items", "default": False},
        },
        "required": ["document_id"],
    }
    category = CapabilityCategory.meeting

    async def call(self, input: dict[str, Any], context: CapabilityContext) -> CapabilityResult:
        doc_id = input.get("document_id", "")
        extract_actions = input.get("extract_actions", True)
        create_tasks = input.get("create_tasks", False)

        # Mock: generate meeting notes summary
        notes_content = f"""会议纪要 (ID: {doc_id}):

议程:
- 项目进度回顾
- 下阶段计划讨论
- 问题与风险

关键讨论:
1. 当前开发进度符合预期
2. 需要增加测试资源
3. 下周一前完成功能A

行动项:
[ ] 张三 - 完成功能A (周一前)
[ ] 李四 - 增加测试用例 (周二前)
[ ] 王五 - 更新文档 (周三前)
"""
        return {
            "success": True,
            "content": notes_content,
            "data": {"document_id": doc_id, "actions_extracted": extract_actions, "tasks_created": create_tasks},
        }

    def is_read_only(self) -> bool:
        # This capability is read-only unless create_tasks is True (handled at runtime)
        return True