# WorkClaw

> 面向知识工作者的 AI 办公助手 Web 应用。  
> 目标不是替代 IDE 里的 Coding Agent，而是把「日程、待办、文档、邮件、会议、知识库」这些日常办公任务，统一到一个可扩展的 AI 工作台里。

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)](#技术栈)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB)](#技术栈)
[![Status](https://img.shields.io/badge/Status-MVP%20Prototype-orange)](#当前状态)

## 项目简介

WorkClaw 是一个前后端分离的 AI 办公助手项目，后端使用 Python + FastAPI，前端使用 React + TypeScript + Vite。

它借鉴了 Easy Agent / Claude Code 一类 Agent 系统的架构思想，但做了办公场景适配：

- Easy Agent 面向代码与终端，WorkClaw 面向办公与 Web。
- Easy Agent 的 Tool Registry 被抽象为 WorkClaw 的 Capability Registry。
- Easy Agent 的 QueryEngine / AgenticLoop 被转化为 SessionOrchestrator / AgenticLoop。
- Easy Agent 的权限模型被转化为更适合办公系统的 `strict` / `moderate` / `trusted` 模式。
- WorkClaw 不支持 CLI，不做 Shell 执行，不做代码修改，核心入口是浏览器。

当前版本是 MVP 雏形，重点是验证架构、交互形态和模块边界。第三方办公系统集成目前使用 mock / stub，不包含真实账号密钥。

## 核心能力

WorkClaw 当前已经包含以下办公助手能力雏形：

| 能力 | Capability ID | 当前状态 | 说明 |
|---|---|---|---|
| 日程管理 | `schedule` | Mock | 创建、查看、调整日程的能力雏形 |
| 待办管理 | `todo` | Mock | 创建、完成、整理待办事项 |
| 文档摘要 | `doc_summary` | Mock | 对文档内容生成结构化摘要 |
| 邮件草稿 | `email_draft` | Mock | 根据上下文生成邮件草稿 |
| 会议纪要 | `meeting_notes` | Mock | 整理会议记录，提取结论和行动项 |
| 知识库检索 | `knowledge_search` | Mock | 面向公司资料、项目文档的问答检索 |
| 文件解析 | `file_parse` | Mock | 文件上传与解析流程的预留能力 |

## 产品形态

WorkClaw 的前端被设计成一个 AI Office Cockpit：

- **Dashboard**：今日工作概览、快捷动作、最近会话、任务状态和能力入口。
- **Assistant**：对话式办公助手，支持发送消息、展示助手回复和能力调用上下文。
- **Tasks**：任务列表、状态标签、优先级和行动项管理。
- **Sessions**：历史会话列表和会话上下文入口。
- **Capability Panel**：办公能力库，让用户理解当前助手能做什么。

前端已经做了响应式布局：

- 桌面端：侧边导航 + 中央工作区 + 卡片化信息区。
- 移动端：纵向卡片、紧凑导航和适配手机宽度的内容布局。

## 架构图

```mermaid
flowchart TB
  User[用户 / 浏览器] --> Frontend[React + TypeScript Web App]

  Frontend --> API[FastAPI REST API]
  Frontend --> SSE[SSE / Stream 接口预留]

  API --> Auth[Mock Auth]
  API --> Orchestrator[SessionOrchestrator]
  API --> TaskService[Task Service]
  API --> CapabilityAPI[Capability API]

  Orchestrator --> Context[Context Builder]
  Orchestrator --> Loop[AgenticLoop]
  Loop --> ModelProvider[Model Provider / Mock LLM]
  Loop --> Registry[Capability Registry]
  Loop --> Permission[Permission Engine]

  Registry --> Schedule[Schedule Capability]
  Registry --> Todo[Todo Capability]
  Registry --> Doc[Document Summary]
  Registry --> Email[Email Draft]
  Registry --> Meeting[Meeting Notes]
  Registry --> Knowledge[Knowledge Search]
  Registry --> File[File Parse]

  TaskService --> Models[SQLModel / SQLite]
  Orchestrator --> Models
```

## 运行流程

```mermaid
sequenceDiagram
  participant U as User
  participant F as Frontend
  participant A as FastAPI
  participant O as SessionOrchestrator
  participant L as AgenticLoop
  participant R as CapabilityRegistry
  participant C as Capability

  U->>F: 输入办公请求
  F->>A: POST /api/v1/chat/sessions/{id}/chat
  A->>O: 载入会话与上下文
  O->>L: 执行 AgenticLoop
  L->>R: 查找可用能力
  R->>C: 调用对应办公能力
  C-->>L: 返回能力结果
  L-->>O: 生成助手回复
  O-->>A: 返回结构化响应 / 流式事件
  A-->>F: 展示回复、任务和能力结果
```

## 技术栈

### 后端

- Python 3.9+（建议 Python 3.11+）
- FastAPI
- Pydantic v2
- SQLModel / SQLAlchemy
- SQLite（可迁移到 PostgreSQL）
- sse-starlette（流式接口预留）
- pytest

### 前端

- React 18
- TypeScript
- Vite 4
- React Router
- Axios
- CSS Variables + 响应式 CSS

> 注意：当前项目锁定 Vite 4，是为了兼容当前本地运行环境。不要随意升级到 Vite 5 / Vite 8，否则在某些 Electron Node 环境下可能遇到 Rollup / Rolldown 原生 binding 签名问题。

## 项目结构

```text
workclaw/
├── README.md
├── .gitignore
├── docs/
│   └── PROJECT_PLAN.md
├── backend/
│   ├── pyproject.toml
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/
│   │   ├── capabilities/
│   │   ├── config/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   └── tests/
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── styles/
│       └── types/
└── scripts/
    └── keep-workclaw-tunnel.sh
```

## 快速开始

### 1. 克隆项目

```bash
git clone git@github.com:wp931120/workclaw.git
cd workclaw
```

### 2. 启动后端

```bash
cd backend
pip install -e ".[dev]"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8010
```

后端默认访问地址：

```text
http://localhost:8010
```

健康检查：

```text
http://localhost:8010/api/v1/health
```

API 文档：

```text
http://localhost:8010/docs
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3010
```

前端访问地址：

```text
http://localhost:3010
```

当前 `vite.config.ts` 中已经配置代理：

```text
/api -> http://localhost:8010
```

因此前端可以直接通过 `/api/v1/...` 访问后端。

## API 概览

### 健康检查

```http
GET /api/v1/health
```

### 认证

```http
POST /api/v1/auth/token
```

当前为本地开发 mock auth，后续可扩展 OAuth / SSO。

### Chat / Sessions

```http
POST   /api/v1/chat/sessions
GET    /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{session_id}
DELETE /api/v1/chat/sessions/{session_id}
GET    /api/v1/chat/sessions/{session_id}/messages
POST   /api/v1/chat/sessions/{session_id}/chat
```

### Capabilities

```http
GET /api/v1/capabilities
```

返回当前注册的办公能力列表。

### Tasks

```http
GET    /api/v1/tasks/tasks
POST   /api/v1/tasks/tasks
GET    /api/v1/tasks/tasks/{task_id}
PATCH  /api/v1/tasks/tasks/{task_id}
DELETE /api/v1/tasks/tasks/{task_id}
```

## 配置说明

后端配置通过环境变量读取，可参考：

```text
backend/.env.example
```

常用变量：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `WORKCLAW_DEBUG` | `true` | 调试模式 |
| `WORKCLAW_DATABASE_URL` | `sqlite+aiosqlite:///./data/workclaw.db` | 数据库连接 |
| `WORKCLAW_DEFAULT_MODEL_PROFILE` | `anthropic` | 默认模型 Profile |
| `WORKCLAW_DEFAULT_PERMISSION_MODE` | `moderate` | 默认权限模式 |
| `WORKCLAW_ANTHROPIC_API_KEY` | 空 | 预留 Anthropic API Key |
| `WORKCLAW_OPENAI_API_KEY` | 空 | 预留 OpenAI API Key |

当前 MVP 默认使用 mock / stub 能力，不需要真实第三方密钥。

## 开发验证

### 后端测试

```bash
cd backend
pytest -v
```

### 前端类型检查

```bash
cd frontend
npx tsc --noEmit
```

### 前端构建

```bash
cd frontend
npm run build
```

如果在 Electron Node 环境中遇到 Rollup / Rolldown native binding 报错，请使用系统 Node.js 或保持当前 Vite 4 版本。

## 设计原则

### 1. Web 优先，而不是 CLI 优先

WorkClaw 面向办公用户，入口是浏览器。它不提供 CLI，也不执行 Shell 命令。

### 2. Capability 是一等公民

每个办公能力都通过统一接口注册，后续可以像插件一样扩展。

### 3. 会话编排和能力调用分离

SessionOrchestrator 负责会话、上下文和流转；Capability 只负责具体办公动作。

### 4. Mock 先行，真实集成后置

MVP 阶段先验证产品体验和架构边界，日历、邮件、知识库、文档系统等真实集成在后续迭代中接入。

### 5. 默认安全

当前不会读取真实办公账号，不会发送真实邮件，不会访问真实第三方服务。所有外部集成都应显式配置密钥和权限。

## 当前状态

当前版本：`0.1.0`。

已完成：

- FastAPI 应用入口。
- CORS 与基础配置层。
- Mock Auth。
- Chat Session API。
- Capability Registry。
- 7 个办公能力 mock/stub。
- Task API。
- React + TypeScript 前端。
- Dashboard、Assistant、Tasks、Sessions 页面。
- 响应式前端布局初版。
- 本地开发与公网临时预览脚本。

仍待完善：

- 真实 LLM Provider 接入。
- 会话持久化完善。
- 数据库迁移管理。
- 文档上传与解析。
- 邮件、日历、知识库真实集成。
- 企业认证与权限模型。
- 更完整的端到端测试。

## 路线图

### Iteration 1：核心对话闭环

- 接入真实 LLM。
- 完善 AgenticLoop。
- 支持能力调用结果回填。
- 引入更完整的上下文管理。

### Iteration 2：办公能力落地

- 日程系统集成。
- 邮件草稿与发送确认流。
- 文档上传、解析与摘要。
- 会议纪要与行动项提取。

### Iteration 3：知识库与工作流

- 知识库检索。
- 任务拆解与状态跟踪。
- 通知中心。
- 多步骤办公工作流。

### Iteration 4：生产化

- OAuth / SSO。
- PostgreSQL。
- 部署配置。
- 权限审计。
- 前端体验打磨。

## 临时公网预览

开发阶段可以使用 `localtunnel` 或其他隧道工具临时暴露前端：

```bash
cd frontend
npx --yes localtunnel --port 3010 --subdomain workclaw-wp931120
```

也可以使用脚本做简单保活：

```bash
./scripts/keep-workclaw-tunnel.sh
```

注意：临时隧道不是生产部署方案，地址可能不稳定。长期预览建议使用 Cloudflare Tunnel、ngrok 固定域名或正式部署平台。

## 许可证

MIT License
