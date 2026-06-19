# WorkClaw - AI Office Assistant

> 版本：0.1.0
> 状态：MVP 雏形 - 可本地运行

WorkClaw 是一个面向知识工作者的 AI 办公助手 Web 应用。它将大语言模型的能力封装为日常办公场景中的具体工具——日程管理、文档摘要、邮件草稿、会议纪要、知识库检索等——让用户通过对话式交互完成工作。

## 架构设计

WorkClaw 借鉴了 [Easy Agent](https://github.com/ConardLi/easy-agent) 的架构思想，但适配到 Web 办公助手场景：

- **分层架构**：交互层 → 编排层 → 核心循环 → 能力注册 → 权限引擎
- **能力注册机制**：类似 Easy Agent 的 Tool Registry，每个能力（Capability）有统一接口
- **会话编排**：SessionOrchestrator 管理多轮会话上下文
- **Agentic Loop**：模型推理 → 能力调用 → 结果回填 → 继续推理
- **权限模式**：strict / moderate / trusted 三级控制

## 技术栈

### Backend
- Python 3.11+
- FastAPI
- Pydantic v2
- SQLModel (SQLAlchemy)
- SQLite (可迁移 Postgres)
- SSE 流式输出

### Frontend
- React 18 + TypeScript
- Vite
- React Router
- Axios

## 项目结构

```
workclaw/
├── docs/
│   └── PROJECT_PLAN.md      # 项目规划文档
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API 路由 (REST + SSE)
│   │   ├── capabilities/    # 能力模块 (类 Tool 接口)
│   │   ├── core/            # 核心逻辑 (Orchestrator, AgenticLoop)
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 服务层 (LLM 通信)
│   │   └── config/          # 配置管理
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/             # API 客户端
│   │   ├── components/      # React 组件
│   │   ├── pages/           # 页面
│   │   ├── types/           # TypeScript 类型
│   │   └── styles/          # 样式
│   └── package.json
└── README.md
```

## 快速启动

### 1. 安装后端依赖

```bash
cd workclaw/backend
pip install -e ".[dev]"
```

### 2. 启动后端

```bash
cd workclaw/backend
uvicorn app.main:app --reload --port 8000
```

后端将在 http://localhost:8000 运行。

### 3. 安装前端依赖

```bash
cd workclaw/frontend
npm install
```

### 4. 启动前端

```bash
cd workclaw/frontend
npm run dev
```

前端将在 http://localhost:3000 运行。

### 5. 运行测试

```bash
# 后端测试
cd workclaw/backend
pytest -v

# 前端类型检查
cd workclaw/frontend
npx tsc --noEmit
```

### 6. 访问应用

打开浏览器访问 http://localhost:3000

## 能力模块

当前已实现的基础能力（使用 Mock 数据，TODO: 集成真实服务）：

| 能力 | 说明 | 状态 |
|------|------|------|
| schedule | 日程管理（查看、创建、修改日程） | Mock |
| todo | 待办管理（创建、列表、完成、删除） | Mock |
| doc_summary | 文档摘要（提取关键点） | Mock |
| email_draft | 邮件草稿生成 | Mock |
| meeting_notes | 会议纪要整理 | Mock |
| knowledge_search | 知识库检索 | Mock |
| file_parse | 文件解析 | Mock |

## API 端点

### 健康检查
```
GET /api/v1/health
```

### 认证（本地开发简化版）
```
POST /api/v1/auth/token
```

### 会话管理
```
GET    /api/v1/sessions           # 列出会话
POST   /api/v1/sessions           # 创建会话
GET    /api/v1/sessions/{id}      # ��取会话
DELETE /api/v1/sessions/{id}      # 删除会话
```

### 聊天（SSE 流式）
```
POST /api/v1/sessions/{id}/chat   # 发送消息，获取流式响应
```

### 能力
```
GET /api/v1/capabilities          # 列出所有可用能力
```

### 任务
```
GET    /api/v1/tasks              # 列出任务
POST   /api/v1/tasks              # 创建任务
PATCH  /api/v1/tasks/{id}         # 更新任务
DELETE /api/v1/tasks/{id}         # 删除任务
```

## 配置

后端配置通过环境变量设置（详见 `app/config/settings.py`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `WORKCLAW_DEBUG` | `true` | 调试模式 |
| `WORKCLAW_DATABASE_URL` | `sqlite+aiosqlite:///./data/workclaw.db` | 数据库连接 |
| `WORKCLAW_ANTHROPIC_API_KEY` | - | Anthropic API Key |
| `WORKCLAW_OPENAI_API_KEY` | - | OpenAI API Key |
| `WORKCLAW_DEFAULT_MODEL_PROFILE` | `anthropic` | 默认模型 |
| `WORKCLAW_DEFAULT_PERMISSION_MODE` | `moderate` | 默认权限模式 |

## 开发状态

当前为 **Iteration 0 - 骨架搭建** 阶段：

- [x] 项目结构
- [x] FastAPI 入口
- [x] 数据模型（User, Session, Message, Task, Document）
- [x] Capability 基类和注册表
- [x] 7 个示例能力
- [x] SessionOrchestrator
- [x] AgenticLoop（带 Mock LLM）
- [x] REST API + SSE 流
- [x] 前端 Vite + React 项目
- [x] Dashboard, Assistant, Tasks, Sessions 页面

## 下一步

### Iteration 1：核心对话循环
- 完善 AgenticLoop（真实 LLM 调用）
- 上下文压缩
- 会话持久化

### Iteration 2：办公能力实现
- 集成真实日历服务（Google/Outlook）
- 文档解析（PDF/DOCX）
- 邮件服务集成（SMTP/Graph API）

### Iteration 3：任务与通知
- 完整任务 CRUD
- 工作流编排
- 通知中心

### Iteration 4：生产化
- 认证完善（OAuth 扩展点）
- Postgres 迁移
- 前端 UI 打磨

## 许可证

MIT License