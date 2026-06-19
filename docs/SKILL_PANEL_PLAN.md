# Skill Panel & Tool Call Visualization Plan

## 目标

1. **Skill 面板**：让用户可以启用/禁用 AI 能力（Skill）
2. **工具调用可视化**：在聊天中实时显示 skill 调用的卡片

## 非目标

- 不实现用户权限系统（暂时用 dev_user）
- 不实现复杂的 skill 配置（仅启用/禁用）
- 保留现有 `/api/v1/capabilities` 兼容性

---

## 1. 后端数据模型

### Skill 模型（复用 Capability 概念）

```python
# backend/app/models/skill.py
class Skill(SQLModel, table=True):
    id: UUID (primary key)
    name: str (unique, 对应 Capability.name)
    enabled: bool (default=True)
    read_only: bool (从 Capability 获取)
    user_scope: str (default="dev_user")
    created_at: datetime
    updated_at: datetime
```

### API 设计

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/skills` | 列出所有 skills（含 enabled 状态） |
| GET | `/api/v1/skills/{skill_id}` | 获取单个 skill |
| PATCH | `/api/v1/skills/{skill_id}` | 更新 skill（主要是 enabled） |
| POST | `/api/v1/skills/{skill_id}/toggle` | 快捷 toggle |

响应格式：
```json
{
  "skills": [
    {
      "id": "uuid",
      "name": "schedule",
      "title": "日程管理",
      "description": "...",
      "category": "schedule",
      "enabled": true,
      "read_only": false,
      "is_dangerous": false,
      "icon": "calendar"
    }
  ],
  "count": 7
}
```

### 与 Capability 集成

- 启动时：从 CapabilityRegistry 加载所有 capability
- 初始化 Skill 表：如果 skill 不存在，则创建（enabled=True）
- 查询时：Skill.enabled 控制是否传给 LLM
- AgenticLoop：只使用 enabled 的 capabilities

---

## 2. 前端设计

### 路由

- `/skills` - 新建 Skills 管理页面
- 导航栏添加 "Skills" 入口

### Skills 页面

- 展示所有 skills 按分类
- 每个 skill 显示：图标、标题、描述、启用开关
- 开关切换调用 PATCH API
- 响应式布局，移动端可用

### 工具调用卡片

在 AssistantPage 中：

```tsx
// 新增状态
const [toolCalls, setToolCalls] = useState<ToolCallEvent[]>([])

// SSE 事件处理
for await (const event of api.chat(...)) {
  if (event.type === 'capability_call') {
    // 添加 tool call 卡片（运行中）
    setToolCalls(prev => [...prev, { status: 'running', ...event.data }])
  } else if (event.type === 'capability_result') {
    // 更新卡片状态（成功/失败）
    setToolCalls(prev => prev.map(tc =>
      tc.name === event.data.name ? { ...tc, status: 'success', result: event.data.result } : tc
    ))
  }
}
```

卡片样式：
- 左侧：技能图标 + 名称
- 中间：输入摘要 / 结果摘要
- 右侧：状态指示器（运行中 spinner / 成功 ✓ / 失败 ✗）
- 位置：出现在对应 assistant 回复之前

---

## 3. SSE 事件设计

现有事件已支持：
- `capability_call` - 技能开始调用
- `capability_result` - 技能结果返回

扩展添加字段：
```json
{
  "type": "capability_call",
  "data": {
    "name": "schedule",
    "input": { "action": "list" },
    "call_id": "uuid",
    "timestamp": "ISO8601"
  }
}
{
  "type": "capability_result",
  "data": {
    "name": "schedule",
    "result": { "success": true, "content": "..." },
    "duration_ms": 123,
    "call_id": "uuid"
  }
}
```

---

## 4. 实现步骤

### Step 1: 后端 - Skill 模型和 API
1. 创建 `backend/app/models/skill.py`
2. 创建 `backend/app/api/v1/skills.py`
3. 修改 `capability` 相关代码支持 enabled 过滤
4. 注册 router 到 main.py

### Step 2: 前端 - Types 和 API Client
1. 更新 `frontend/src/types/index.ts` - 添加 Skill, ToolCallEvent 类型
2. 更新 `frontend/src/api/client.ts` - 添加 skills API 方法

### Step 3: 前端 - Skills 页面
1. 创建 `frontend/src/pages/SkillsPage.tsx`
2. 添加路由到 App.tsx
3. 更新 AppLayout 添加 Skills 导航项

### Step 4: 前端 - 工具调用可视化
1. 修改 AssistantPage 处理 capability_call/result 事件
2. 添加 ToolCallCard 组件
3. 样式调整

### Step 5: 验证和测试
1. 运行 pytest
2. 运行 tsc --noEmit
3. 运行 npm run build
4. API smoke test

### Step 6: README 更新
1. 添加 Skills 面板说明
2. 添加 API 文档
3. 链接本规划文档

---

## 5. 验证清单

- [ ] `GET /api/v1/skills` 返回所有 skills 含 enabled
- [ ] `PATCH /api/v1/skills/{id}` 修改 enabled
- [ ] 关闭 skill 后，LLM 不会收到该 skill 的 tool schema
- [ ] SSE 中有 capability_call 和 capability_result 事件
- [ ] 前端 Skills 页面可正常切换开关
- [ ] 聊天时 tool call 卡片显示在正确位置
- [ ] 移动端布局正常

---

## 6. 参考

- Easy Agent: ToolRegistry, AgenticLoop, ToolCard 组件
- WorkClaw 现有 Capability 概念：内部复用，增强用户可控性