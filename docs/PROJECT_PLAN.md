# WorkClaw 项目规划

> 版本：0.1.0-draft
> 日期：2026-06-19
> 状态：初始规划

## 1. 愿景

WorkClaw 是一个面向知识工作者的 AI 办公助手 Web 应用。它将大语言模型的能力封装为日常办公场景中的具体工具——日程管理、文档摘要、邮件草稿、会议纪要、知识库检索等——让用户通过对话式交互完成工作，而非切换多个 SaaS 工具。

**核心理念**：不是 coding agent，而是 office agent。不需要终端，而是浏览器即入口。

## 2. 范围

### In-Scope

- 对话式办公助手核心（Chat + Tool Use 循环）
- 办公能力模块：日程/待办、文档摘要、邮件草稿、会议纪要、知识库检索、文件上传解析、工作流任务、通知中心
- 能力/工具注册机制（Plugin 风格，可扩展）
- 会话管理（多会话、上下文压缩、持久化）
- 任务状态追踪
- 权限与安全边界（工具执行授权、数据隔离）
- Web 前后端分离架构
- 本地开发友好的简化认证，预留企业 SSO/OAuth 扩展点

### Out-of-Scope

- 代码编辑、文件系统操作、Shell 执行（这不是 coding agent）
- CLI 模式
- 移动端原生 App（初期 Web 响应式即可）
- 真实第三方办公账号集成（初版用 mock/stub，留接口）
- 多租户 SaaS 部署
- 实时音视频会议功能
- 复杂的 RBAC（初版简单角色即可）

## 3. 核心用户场景

1. **日程助理**：用户说"帮我安排明天下午的团队会议"，助手检查日历冲突、创建日程、发送邀请。
2. **文档摘要**：用户上传一份 PDF 报告，助手提取要点、生成摘要、归档到知识库。
3. **邮件草稿**：用户描述意图，助手根据上下文和历史风格草拟邮件，用户确认后发送。
4. **会议纪要**：用户上传会议录音转写或笔记，助手整理为结构化纪要，提取行动项并创建待办。
5. **知识库问答**：用户询问公司政策或项目文档，助手从知识库检索并回答。
6. **工作流编排**：用户描述多步骤任务，助手分解为子任务、追踪状态、通知相关人。

## 4. 架构设计

### 4.1 架构图

```
┌─────────────────────────────────────────────────┐
│                   Frontend (React)               │
│  ┌──────┐ ┌──────────┐ ┌────────┐ ┌───────────┐ │
│  │Dash- │ │Assistant  │ │Task    │ │Capability │ │
│  │board │ │Chat/Work  │ │List    │ │Panel      │ │
│  └──────┘ └──────────┘ └────────┘ └───────────┘ │
│           ↕ REST / WebSocket / SSE               │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────┼─────────────────────────────┐
│              Backend (FastAPI)                     │
│                                                     │
│  ┌─────────────┐   ┌──────────────┐               │
│  │ API Routes  │──▶│ Session      │               │
│  │ (v1/)       │   │ Orchestrator │               │
│  └─────────────┘   └──────┬───────┘               │
│                           │                         │
│  ┌─────────────┐   ┌──────▼───────┐               │
│  │ Auth &      │   │ Agentic Loop │               │
│  │ Permission  │   │ (LLM + Tools)│               │
│  └─────────────┘   └──────┬───────┘               │
│                           │                         │
│  ┌─────────────┐   ┌──────▼───────┐               │
│  │ Config      │   │ Capability   │               │
│  │ Manager     │   │ Registry     │               │
│  └─────────────┘   └──────┬───────┘               │
│                           │                         │
│  ┌─────────────────────────────────────────────┐  │
│  │          Capability Implementations          │  │
│  │ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐  │  │
│  │ │Sche│ │Doc │ │Mail│ │Meet│ │Know│ │File│  │  │
│  │ │dule│ │Sum │ │Drf │ │Note│ │Base│ │Pars│  │  │
│  │ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘  │  │
│  │ ┌────┐ ┌────┐ ┌────┐                        │  │
│  │ │Work│ │Noti│ │More│                        │  │
│  │ │flow│ │fica│ │... │                        │  │
│  │ └────┘ └────┘ └────┘                        │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────┐   ┌──────────────┐               │
│  │ Model       │   │ Data Layer   │               │
│  │ Provider    │   │ (SQLModel)   │               │
│  └─────────────┘   └──────────────┘               │
└─────────────────────────────────────────────────────┘
```

### 4.2 分层架构（借鉴 Easy Agent）

| 层 | Easy Agent | WorkClaw 适配 |
|---|---|---|
| 交互层 | React + Ink 终端 UI | React + TypeScript Web UI |
| 编排层 | QueryEngine（会话级控制器） | SessionOrchestrator（会话级控制器） |
| 核心循环 | AgenticLoop（模型→工具→结果循环） | AgenticLoop（模型→能力→结果循环） |
| 工具/能力 | Tool Registry + Tool 接口 | Capability Registry + Capability 接口 |
| 权限 | Permission Engine（default/plan/auto） | Permission Engine（strict/moderate/trusted） |
| 上下文 | SystemPrompt + Compaction | SystemPrompt + Compaction |
| 模型通信 | Provider Adapter（多协议） | ModelProvider（多后端，Anthropic/OpenAI/本地） |
| 持久化 | Session JSONL + FileHistory | SQLModel + SQLite/Postgres |
| 扩展 | Skills/MCP/Sub-Agent/Hooks | Capability Plugins（未来 MCP） |

### 4.3 核心运行流程

```
用户输入 → API Route → SessionOrchestrator
  → 构建 SystemPrompt（身份 + 上下文 + 可用能力）
  → AgenticLoop.query()
    → 调用 LLM（流式）
    → LLM 返回 tool_use → CapabilityRegistry.find()
    → PermissionEngine.check()
    → Capability.call() → 返回结果
    → 结果回填 → 继续循环
  → 流式输出 → WebSocket/SSE → 前端
```

## 5. 模块设计

### 5.1 后端模块

```
backend/app/
├── main.py                  # FastAPI app 入口
├── config/
│   ├── settings.py          # 配置管理（多源合并）
│   └── model_profiles.py    # 模型 Profile 定义
├── api/
│   └── v1/
│       ├── chat.py          # 对话 API（REST + SSE）
│       ├── sessions.py      # 会话管理
│       ├── capabilities.py  # 能力查询
│       ├── tasks.py         # 任务管理
│       ├── documents.py     # 文档上传/解析
│       ├── auth.py          # 认证
│       └── health.py        # 健康检查
├── core/
│   ├── orchestrator.py      # 会话编排器
│   ├── agentic_loop.py      # 核心 Agent 循环
│   ├── context.py           # 上下文/系统提示管理
│   └── compaction.py        # 上下文压缩
├── models/
│   ├── session.py           # 会话模型
│   ├── message.py           # 消息模型
│   ├── task.py              # 任务模型
│   ├── document.py          # 文档模型
│   └── user.py              # 用户模型
├── services/
│   ├── model_provider.py    # LLM 通信服务
│   ├── permission.py        # 权限引擎
│   ├── notification.py      # 通知服务
│   └── knowledge.py         # 知识库服务
├── capabilities/
│   ├── base.py              # Capability 基类
│   ├── registry.py          # 能力注册表
│   ├── schedule.py          # 日程能力
│   ├── todo.py              # 待办能力
│   ├── doc_summary.py       # 文档摘要能力
│   ├── email_draft.py       # 邮件草稿能力
│   ├── meeting_notes.py     # 会议纪要能力
│   ├── knowledge_search.py  # 知识库检索能力
│   ├── file_parse.py        # 文件解析能力
│   ├── workflow.py          # 工作流能力
│   └── notification.py      # 通知能力
└── tests/
```

### 5.2 前端模块

```
frontend/src/
├── App.tsx
├── main.tsx
├── api/
│   └── client.ts            # API 客户端（axios/fetch）
├── components/
│   ├── layout/
│   │   ├── AppLayout.tsx    # 主布局
│   │   ├── Sidebar.tsx      # 侧边栏
│   │   └── Header.tsx       # 顶栏
│   ├── chat/
│   │   ├── ChatPanel.tsx    # 对话面板
│   │   ├── MessageList.tsx  # 消息列表
│   │   ├── MessageItem.tsx  # 单条消息
│   │   └── ChatInput.tsx    # 输入框
│   ├── dashboard/
│   │   └── Dashboard.tsx    # 仪表盘
│   ├── tasks/
│   │   ├── TaskList.tsx     # 任务列表
│   │   └── TaskItem.tsx     # 任务项
│   └── capabilities/
│       └── CapabilityPanel.tsx  # 能力面板
├── pages/
│   ├── HomePage.tsx
│   ├── AssistantPage.tsx
│   └── TasksPage.tsx
├── hooks/
│   └── useChat.ts           # 对话 Hook
├── types/
│   └── index.ts             # 类型定义
└── styles/
    └── index.css            # 全局样式
```

## 6. 数据模型草案

### 6.1 User

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| email | String | 邮箱 |
| name | String | 显示名 |
| role | Enum(user, admin) | 角色 |
| api_key_hash | String? | API Key 哈希（本地模式） |
| created_at | DateTime | 创建时间 |

### 6.2 Session

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| user_id | UUID FK | 所属用户 |
| title | String | 会话标题 |
| model_profile | String | 使用的模型 Profile |
| permission_mode | Enum(strict, moderate, trusted) | 权限模式 |
| status | Enum(active, archived) | 状态 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 6.3 Message

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| session_id | UUID FK | 所属会话 |
| role | Enum(system, user, assistant, tool) | 角色 |
| content | Text | 内容 |
| tool_calls | JSON? | 工具调用信息 |
| tool_call_id | String? | 工具调用 ID |
| model_usage | JSON? | Token 用量 |
| created_at | DateTime | 创建时间 |

### 6.4 Task

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| session_id | UUID FK? | 关联会话 |
| user_id | UUID FK | 所属用户 |
| title | String | 任务标题 |
| description | Text | 任务描述 |
| status | Enum(pending, in_progress, completed, cancelled) | 状态 |
| priority | Enum(low, medium, high) | 优先级 |
| due_date | DateTime? | 截止时间 |
| parent_task_id | UUID FK? | 父任务 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 6.5 Document

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| user_id | UUID FK | 所属用户 |
| filename | String | 文件名 |
| file_path | String | 存储路径 |
| file_type | String | MIME 类型 |
| summary | Text? | AI 摘要 |
| metadata | JSON? | 元数据 |
| created_at | DateTime | 创建时间 |

### 6.6 CapabilityCall (审计日志)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| session_id | UUID FK | 所属会话 |
| message_id | UUID FK | 触发消息 |
| capability_name | String | 能力名 |
| input_data | JSON | 调用输入 |
| output_data | JSON? | 调用输出 |
| status | Enum(approved, denied, error, completed) | 状态 |
| created_at | DateTime | 创建时间 |

## 7. API 设计

### 7.1 REST API

| Method | Path | 说明 |
|---|---|---|
| GET | /api/v1/health | 健康检查 |
| POST | /api/v1/auth/token | 获取 Token |
| GET | /api/v1/sessions | 列出会话 |
| POST | /api/v1/sessions | 创建会话 |
| GET | /api/v1/sessions/{id} | 获取会话 |
| DELETE | /api/v1/sessions/{id} | 删除会话 |
| GET | /api/v1/sessions/{id}/messages | 获取消息历史 |
| POST | /api/v1/sessions/{id}/chat | 发送消息（返回 SSE 流） |
| GET | /api/v1/capabilities | 列出可用能力 |
| GET | /api/v1/tasks | 列出任务 |
| POST | /api/v1/tasks | 创建任务 |
| PATCH | /api/v1/tasks/{id} | 更新任务 |
| POST | /api/v1/documents/upload | 上传文档 |
| GET | /api/v1/documents | 列出文档 |
| GET | /api/v1/notifications | 获取通知 |

### 7.2 SSE 事件格式

```
event: text_delta
data: {"content": "我来帮你..."}

event: capability_call
data: {"name": "schedule_check", "input": {...}}

event: capability_result
data: {"name": "schedule_check", "output": {...}}

event: usage
data: {"input_tokens": 1200, "output_tokens": 350}

event: done
data: {}
```

## 8. 前端页面规划

| 页面 | 路由 | 说明 |
|---|---|---|
| Dashboard | / | 概览：今日日程、待办、最近会话、通知 |
| Assistant | /assistant | 对话工作区：Chat + 能力面板 + 上下文 |
| Sessions | /sessions | 会话历史列表 |
| Tasks | /tasks | 任务看板/列表 |
| Documents | /documents | 文档管理 |
| Settings | /settings | 配置：模型、权限、API Key |

## 9. Capability 接口设计

```python
class Capability(ABC):
    """能力基类，借鉴 Easy Agent Tool 接口"""

    name: str                    # 能力标识名
    description: str             # 模型可见说明
    input_schema: dict           # JSON Schema
    category: str                # 分类：schedule/email/document/...

    @abstractmethod
    async def call(self, input: dict, context: CapabilityContext) -> CapabilityResult:
        """执行能力"""
        ...

    def is_read_only(self) -> bool:
        """是否只读（影响权限判定）"""
        return True

    def is_enabled(self) -> bool:
        """是否可用"""
        return True

    def is_dangerous(self) -> bool:
        """是否需要严格授权（如发邮件）"""
        return False
```

## 10. 迭代路线图

### Iteration 0：骨架搭建 ✅ 已完成

- 项目结构、配置、依赖
- FastAPI 入口 + 健康检查
- SQLModel 基础模型
- Capability 基类 + Registry + 7 个示例能力
- 前端 Vite + React 骨架
- 本地启动说明
- AgenticLoop + Mock LLM
- 会话管理 + SSE 流式
- pytest 基础测试

### Iteration 1：核心对话循环（当前）

- AgenticLoop 实现（LLM 流式 → 能力调用 → 结果回填）
- SessionOrchestrator 实现
- SSE 流式输出
- 前端 Chat 面板 + 流式渲染
- 基础 SystemPrompt 构建

### Iteration 2：办公能力实现

- 日程/待办能力
- 文档上传 + 摘要能力
- 邮件草稿能力（mock）
- 会议纪要能力
- 知识库检索能力（简单向量搜索）

### Iteration 3：任务与通知

- 任务管理完整 CRUD
- 工作流编排能力
- 通知中心
- 权限引擎完善

### Iteration 4：生产化

- 上下文压缩
- 会话持久化完善
- 错误处理与重试
- 认证完善（OAuth 扩展点）
- 数据库迁移到 Postgres
- 前端打磨

## 11. 测试策略

| 类型 | 工具 | 覆盖目标 |
|---|---|---|
| 单元测试 | pytest | Capability、Service、Model 逻辑 |
| API 测试 | pytest + httpx | REST 端点、SSE 流 |
| 集成测试 | pytest | AgenticLoop + Mock LLM |
| 前端测试 | Vitest + Testing Library | 组件、Hook |
| E2E 测试 | Playwright（后期） | 核心用户场景 |

## 12. 安全边界

1. **能力执行授权**：写操作（发邮件、创建日程）需用户确认；读操作自动放行（权限模式决定）
2. **权限模式**：strict（所有能力需确认）→ moderate（读操作放行，写操作确认）→ trusted（按能力标记自动决策）
3. **数据隔离**：用户只能访问自己的会话、任务、文档
4. **API Key 防护**：不硬编码密钥，环境变量注入
5. **文件上传限制**：类型白名单 + 大小上限
6. **输入验证**：Pydantic 模型校验所有 API 输入
7. **审计日志**：CapabilityCall 记录所有能力调用
8. **Mock 边界**：所有外部集成（邮件、日历）用 stub，标记清晰 TODO，不引入真实凭证
