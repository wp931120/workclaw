/** Assistant/Chat page — premium chat UI with sidebar, messages, input, and capability panel. */

import { useState, useEffect, useRef } from 'react'
import { api } from '../api/client'
import type { Session, Capability, ToolCallState } from '../types'
import './AssistantPage.css'

export function AssistantPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string; toolCalls?: ToolCallState[] }>>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [capabilities, setCapabilities] = useState<Capability[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    loadSessions()
    loadCapabilities()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function loadSessions() {
    const data = await api.listSessions()
    setSessions(data)
    if (data.length > 0 && !currentSession) {
      selectSession(data[0])
    }
  }

  async function loadCapabilities() {
    const data = await api.listCapabilities()
    setCapabilities(data.capabilities || [])
  }

  async function createNewSession() {
    const session = await api.createSession({
      title: `新会话 ${sessions.length + 1}`,
    })
    setSessions([session, ...sessions])
    setCurrentSession(session)
    setMessages([])
    setSidebarOpen(false)
  }

  async function selectSession(session: Session) {
    setCurrentSession(session)
    const msgs = await api.getMessages(session.id)
    setMessages(msgs.map((m: { role: string; content: string }) => ({
      role: m.role as 'user' | 'assistant',
      content: m.content || '',
    })).filter((m: { content: string }) => m.content))
    setSidebarOpen(false)
  }

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    setMessages(prev => [...prev, { role: 'user', content: userMessage, toolCalls: [] }])

    try {
      let sessionId = currentSession?.id
      if (!sessionId) {
        const newSession = await api.createSession({ title: userMessage.slice(0, 20) })
        setSessions([newSession, ...sessions])
        setCurrentSession(newSession)
        sessionId = newSession.id
      }

      // sessionId is guaranteed to be defined now
      const finalSessionId = sessionId!

      setMessages(prev => [...prev, { role: 'assistant', content: '', toolCalls: [] }])
      let fullContent = ''
      let currentToolCalls: ToolCallState[] = []

      for await (const event of api.chat(finalSessionId, userMessage)) {
        if (event.type === 'text_delta') {
          fullContent += event.data.content
          setMessages(prev => {
            const updated = [...prev]
            // Find the last assistant message to update
            for (let i = updated.length - 1; i >= 0; i--) {
              if (updated[i].role === 'assistant') {
                updated[i] = { ...updated[i], content: fullContent }
                break
              }
            }
            return updated
          })
        } else if (event.type === 'capability_call') {
          // Add tool call card (running)
          const toolCall: ToolCallState = {
            id: event.data.call_id || `call_${Date.now()}`,
            name: event.data.name,
            title: event.data.title || event.data.name,
            input: event.data.input,
            status: 'running',
          }
          currentToolCalls.push(toolCall)
          setMessages(prev => {
            const updated = [...prev]
            for (let i = updated.length - 1; i >= 0; i--) {
              if (updated[i].role === 'assistant') {
                updated[i] = { ...updated[i], toolCalls: [...currentToolCalls] }
                break
              }
            }
            return updated
          })
        } else if (event.type === 'capability_result') {
          // Update tool call card status
          const result = event.data.result
          currentToolCalls = currentToolCalls.map(tc =>
            tc.name === event.data.name
              ? {
                  ...tc,
                  status: result.success ? 'success' : 'error',
                  result: result,
                  duration_ms: event.data.duration_ms,
                }
              : tc
          )
          // Append result content to message
          if (result.content) {
            fullContent += `\n\n${result.content}`
          }
          setMessages(prev => {
            const updated = [...prev]
            for (let i = updated.length - 1; i >= 0; i--) {
              if (updated[i].role === 'assistant') {
                updated[i] = { ...updated[i], content: fullContent, toolCalls: [...currentToolCalls] }
                break
              }
            }
            return updated
          })
        } else if (event.type === 'error') {
          console.error('Chat error:', event.data.message)
          fullContent += `\n\n[错误: ${event.data.message}]`
          setMessages(prev => {
            const updated = [...prev]
            for (let i = updated.length - 1; i >= 0; i--) {
              if (updated[i].role === 'assistant') {
                updated[i] = { ...updated[i], content: fullContent }
                break
              }
            }
            return updated
          })
        }
      }
    } catch (err) {
      console.error('Chat error:', err)
      setMessages(prev => [...prev, { role: 'assistant', content: '抱歉，发生错误，请重试。' }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(e as any)
    }
  }

  const groupedCapabilities = capabilities.reduce((acc, cap) => {
    const cat = cap.category || '其他'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(cap)
    return acc
  }, {} as Record<string, Capability[]>)

  return (
    <div className="assistant-page">
      {/* Mobile: sidebar toggle */}
      <button className="sidebar-toggle mobile-only" onClick={() => setSidebarOpen(!sidebarOpen)}>
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M3 5h14M3 10h14M3 15h14" />
        </svg>
      </button>

      {/* Sidebar — sessions */}
      <aside className={`chat-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>会话</h2>
          <button className="new-chat-btn" onClick={createNewSession}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M8 3v10M3 8h10" />
            </svg>
          </button>
        </div>
        <div className="session-list">
          {sessions.length === 0 ? (
            <div className="sidebar-empty">暂无会话</div>
          ) : (
            sessions.map(session => (
              <button
                key={session.id}
                className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
                onClick={() => selectSession(session)}
              >
                <span className="session-dot" />
                <span className="session-title">{session.title}</span>
              </button>
            ))
          )}
        </div>
        <button className="sidebar-close mobile-only" onClick={() => setSidebarOpen(false)}>
          关闭
        </button>
      </aside>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && <div className="sidebar-overlay mobile-only" onClick={() => setSidebarOpen(false)} />}

      {/* Main chat area */}
      <div className="chat-main">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="empty-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M38 24c0 7.18-5.82 13-13 13a13 13 0 01-5.08-.98L12 42l2.64-5.92A12.9 12.9 0 016 24c0-7.18 5.82-13 13-13s13 5.82 13 13h4z" />
                <circle cx="19" cy="22" r="1.5" fill="currentColor" />
                <circle cx="24" cy="22" r="1.5" fill="currentColor" />
                <circle cx="29" cy="22" r="1.5" fill="currentColor" />
              </svg>
            </div>
            <h2>WorkClaw 助手</h2>
            <p>我可以帮你管理日程、创建任务、摘要文档、整理会议纪要等。</p>
            <div className="empty-suggestions">
              <button onClick={() => setInput('帮我创建一个待办任务')}>帮我创建一个待办任务</button>
              <button onClick={() => setInput('今天的任务有哪些？')}>今天的任务有哪些？</button>
              <button onClick={() => setInput('总结一下上次会议的内容')}>总结一下上次会议的内容</button>
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? (
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <circle cx="9" cy="5" r="3" />
                      <path d="M3 16c0-3.31 2.69-6 6-6s6 2.69 6 6" />
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M14 9c0 2.21-1.79 4-4 4a4 4 0 01-1.34-.26l-2.44 1.96 1.08-2.16A4 4 0 015 9c0-2.21 1.79-4 4-4s4 1.79 4 4h1z" />
                    </svg>
                  )}
                </div>
                <div className="message-content">
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="tool-calls-container">
                      {msg.toolCalls.map(tc => (
                        <div key={tc.id} className={`tool-call-card ${tc.status}`}>
                          <div className="tool-call-icon">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                              <path d="M13 6l-3-3-4 4 3 3M3 10l3 3 4-4-3-3" />
                            </svg>
                          </div>
                          <div className="tool-call-info">
                            <div className="tool-call-name">{tc.title}</div>
                            <div className="tool-call-detail">
                              {JSON.stringify(tc.input).slice(0, 50)}
                              {JSON.stringify(tc.input).length > 50 ? '...' : ''}
                            </div>
                            {tc.result && (
                              <div className="tool-call-result">
                                {tc.result.content?.slice(0, 80)}
                                {tc.result.content && tc.result.content.length > 80 ? '...' : ''}
                                {tc.duration_ms && <span className="tool-duration"> ({tc.duration_ms}ms)</span>}
                              </div>
                            )}
                          </div>
                          <div className={`tool-call-status ${tc.status}`}>
                            {tc.status === 'running' ? (
                              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                                <circle cx="8" cy="8" r="6" strokeDasharray="20" strokeDashoffset="5" />
                              </svg>
                            ) : tc.status === 'success' ? (
                              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M4 8l3 3 5-5" />
                              </svg>
                            ) : (
                              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M5 5l6 6M11 5l-6 6" />
                              </svg>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="message-text">{msg.content || (msg.role === 'assistant' && loading && i === messages.length - 1 ? '思考中...' : '')}</div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}

        <form className="chat-input-wrapper" onSubmit={sendMessage}>
          <div className="chat-input-container">
            <textarea
              ref={inputRef}
              className="chat-input"
              placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              rows={1}
            />
            <button
              type="submit"
              className="send-btn"
              disabled={loading || !input.trim()}
            >
              {loading ? (
                <span className="loading-dots">
                  <span></span><span></span><span></span>
                </span>
              ) : (
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M2 9l14-7-7 14v-7H2z" />
                </svg>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Right panel — capabilities */}
      <aside className="capability-panel">
        <div className="panel-header">
          <h3>能力库</h3>
          <span className="panel-count">{capabilities.length} 项</span>
        </div>
        <div className="capability-categories">
          {Object.entries(groupedCapabilities).map(([category, caps]) => (
            <div key={category} className="capability-category">
              <div className="category-header">{category}</div>
              {caps.map(cap => (
                <div key={cap.name} className="capability-item" title={cap.description}>
                  <div className="cap-icon">
                    {cap.is_dangerous ? (
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M6 1v5M6 10v1M1 6h1M10 6h1M2.3 2.3l.6.6M9.1 9.1l.6.6M2.3 9.7l.6-.6M9.1 3.3l.6-.6" />
                      </svg>
                    ) : (
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M6 1l5 3v3l-5 4-5-4V4l5-3z" />
                      </svg>
                    )}
                  </div>
                  <span className="cap-name">{cap.name}</span>
                  {cap.is_dangerous && <span className="cap-badge">!</span>}
                </div>
              ))}
            </div>
          ))}
        </div>
      </aside>
    </div>
  )
}