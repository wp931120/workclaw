"""File parsing capability - upload and parse various file types."""

from app.capabilities.base import Capability, CapabilityContext, CapabilityResult, CapabilityCategory
from typing import Any


class FileParseCapability(Capability):
    """File parsing capability for uploading and analyzing files."""

    name = "file_parse"
    description = "Parse and analyze uploaded files (PDF, TXT, DOCX, etc.)"
    input_schema = {
        "type": "object",
        "properties": {
            "file_id": {"type": "string", "description": "ID of uploaded file to parse"},
            "analysis_type": {"type": "string", "enum": ["basic", "full", "extract_tables"], "description": "Type of analysis", "default": "basic"},
        },
        "required": ["file_id"],
    }
    category = CapabilityCategory.file

    async def call(self, input: dict[str, Any], context: CapabilityContext) -> CapabilityResult:
        file_id = input.get("file_id", "")
        analysis_type = input.get("analysis_type", "basic")

        # Mock: return parsing result
        # TODO: integrate with real file parsing (PyMuPDF/python-docx)
        return {
            "success": True,
            "content": f"文件解析完成 (ID: {file_id})\n\n文件类型: PDF\n页数: 15\n主要章节:\n- 概述\n- 技术架构\n- 实现细节\n- 结论",
            "data": {"file_id": file_id, "analysis_type": analysis_type, "pages": 15},
        }

    def is_read_only(self) -> bool:
        return True