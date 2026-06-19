"""Knowledge base capability - search and retrieve information."""

from app.capabilities.base import Capability, CapabilityContext, CapabilityResult, CapabilityCategory
from typing import Any


class KnowledgeSearchCapability(Capability):
    """Knowledge base search capability."""

    name = "knowledge_search"
    description = "Search the knowledge base for relevant information"
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "number", "description": "Maximum results to return", "default": 5},
        },
        "required": ["query"],
    }
    category = CapabilityCategory.knowledge

    async def call(self, input: dict[str, Any], context: CapabilityContext) -> CapabilityResult:
        query = input.get("query", "")
        limit = input.get("limit", 5)

        # Mock: return sample results
        # TODO: integrate with real vector search (Elasticsearch/Pinecone/etc.)
        results = [
            {
                "title": "公司休假政策",
                "content": "员工每年享有15天带薪年假...",
                "relevance": 0.95,
            },
            {
                "title": "报销流程",
                "content": "费用报销需填写报销单并附发票...",
                "relevance": 0.85,
            },
        ]
        return {
            "success": True,
            "content": f"搜索结果: '{query}'\n\n1. 公司休假政策 (95%)\n2. 报销流程 (85%)",
            "data": {"query": query, "results": results[:limit]},
        }

    def is_read_only(self) -> bool:
        return True