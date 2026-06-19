/** TypeScript types matching backend models. */

export interface User {
  id: string
  email: string
  name: string
  role: 'user' | 'admin'
}

export interface Session {
  id: string
  user_id: string
  title: string
  model_profile: string
  permission_mode: 'strict' | 'moderate' | 'trusted'
  status: 'active' | 'archived'
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  session_id: string
  role: 'system' | 'user' | 'assistant' | 'tool'
  content: string
  tool_calls?: ToolCall[]
  tool_call_id?: string
  model_usage?: Record<string, unknown>
  created_at: string
}

export interface ToolCall {
  id: string
  name: string
  input: Record<string, unknown>
}

export interface Task {
  id: string
  user_id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high'
  due_date?: string
  created_at: string
  updated_at: string
}

export interface Capability {
  name: string
  description: string
  input_schema: Record<string, unknown>
  category: string
  is_read_only: boolean
  is_dangerous: boolean
}

export interface Skill {
  id: string
  name: string
  title: string
  description: string
  category: string
  enabled: boolean
  read_only: boolean
  is_dangerous: boolean
  icon?: string
}

// SSE Event types
export type SSEEvent =
  | { type: 'text_delta'; data: { content: string } }
  | { type: 'capability_call'; data: CapabilityCallEvent }
  | { type: 'capability_result'; data: CapabilityResultEvent }
  | { type: 'usage'; data: Record<string, unknown> }
  | { type: 'done'; data: { message_id: string } }
  | { type: 'error'; data: { message: string } }

export interface CapabilityCallEvent {
  name: string
  title?: string
  input: Record<string, unknown>
  call_id?: string
  timestamp?: string
}

export interface CapabilityResultEvent {
  name: string
  result: {
    success: boolean
    content?: string
    error?: string
    data?: Record<string, unknown>
  }
  duration_ms?: number
  call_id?: string
}

// Tool call card state for UI
export interface ToolCallState {
  id: string
  name: string
  title: string
  input: Record<string, unknown>
  result?: {
    success: boolean
    content?: string
    error?: string
  }
  status: 'running' | 'success' | 'error'
  duration_ms?: number
}