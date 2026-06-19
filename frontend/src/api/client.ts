/** API client for WorkClaw backend. */

import axios, { AxiosInstance } from 'axios'

const API_BASE = '/api/v1'

class ApiClient {
  private client: AxiosInstance
  private token: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  setToken(token: string) {
    this.token = token
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  // Auth
  async getToken(email?: string) {
    const res = await this.client.post('/auth/token', { email })
    return res.data
  }

  // Health
  async health() {
    const res = await this.client.get('/health')
    return res.data
  }

  // Sessions
  async createSession(data: { title?: string; model_profile?: string; permission_mode?: string }) {
    const res = await this.client.post('/sessions', data)
    return res.data
  }

  async listSessions() {
    const res = await this.client.get('/sessions')
    return res.data
  }

  async getSession(sessionId: string) {
    const res = await this.client.get(`/sessions/${sessionId}`)
    return res.data
  }

  async deleteSession(sessionId: string) {
    const res = await this.client.delete(`/sessions/${sessionId}`)
    return res.data
  }

  async getMessages(sessionId: string) {
    const res = await this.client.get(`/sessions/${sessionId}/messages`)
    return res.data
  }

  // Chat with SSE
  async *chat(sessionId: string, message: string) {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      },
      body: JSON.stringify({ message }),
    })

    const reader = response.body?.getReader()
    if (!reader) return

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          try {
            const event = JSON.parse(data)
            yield event
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  }

  // Capabilities
  async listCapabilities() {
    const res = await this.client.get('/capabilities')
    return res.data
  }

  // Tasks
  async listTasks(status?: string) {
    const params = status ? { status } : {}
    const res = await this.client.get('/tasks', { params })
    return res.data
  }

  async createTask(data: { title: string; description?: string; priority?: string }) {
    const res = await this.client.post('/tasks', data)
    return res.data
  }

  async updateTask(taskId: string, data: Partial<{ title: string; description: string; status: string; priority: string }>) {
    const res = await this.client.patch(`/tasks/${taskId}`, data)
    return res.data
  }

  async deleteTask(taskId: string) {
    const res = await this.client.delete(`/tasks/${taskId}`)
    return res.data
  }
}

export const api = new ApiClient()