/** Sessions page — list and manage chat sessions. */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { Session } from '../types'
import './SessionsPage.css'

export function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadSessions()
  }, [])

  async function loadSessions() {
    setLoading(true)
    try {
      const data = await api.listSessions()
      setSessions(data || [])
    } catch (e) {
      console.error('Failed to load sessions:', e)
    } finally {
      setLoading(false)
    }
  }

  async function createSession() {
    try {
      const session = await api.createSession({
        title: `会话 ${sessions.length + 1}`,
      })
      setSessions([session, ...sessions])
      navigate(`/assistant?session=${session.id}`)
    } catch (e) {
      console.error('Failed to create session:', e)
    }
  }

  async function deleteSession(sessionId: string) {
    try {
      await api.deleteSession(sessionId)
      setSessions(sessions.filter(s => s.id !== sessionId))
      setConfirmDelete(null)
    } catch (e) {
      console.error('Failed to delete session:', e)
    }
  }

  function formatDate(dateStr: string) {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return `今天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
    } else if (diffDays === 1) {
      return '昨天'
    } else if (diffDays < 7) {
      return `${diffDays} 天前`
    } else {
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    }
  }

  return (
    <div className="sessions-page">
      <header className="page-header">
        <h1>会话历史</h1>
        <button className="btn-primary" onClick={createSession}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M7 2v10M2 7h10" />
          </svg>
          新建会话
        </button>
      </header>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : sessions.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M26 16c0 5.52-4.48 10-10 10S6 21.52 6 16 10.48 6 16 6s10 4.48 10 10z" />
              <path d="M16 11v5l3 1.5" />
            </svg>
          </div>
          <p>暂无会话记录</p>
          <button className="btn-ghost" onClick={createSession}>开始第一个会话</button>
        </div>
      ) : (
        <div className="session-grid">
          {sessions.map(session => (
            <div key={session.id} className="session-card">
              <div className="session-header">
                <h3 className="session-title">{session.title}</h3>
                <span className={`status-badge ${session.status}`}>
                  {session.status === 'active' ? '活跃' : '已归档'}
                </span>
              </div>

              <div className="session-meta">
                <div className="meta-item">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M6 1v5M8 9H4" transform="rotate(45 6 6)" />
                  </svg>
                  <span>{session.model_profile}</span>
                </div>
                <div className="meta-item">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <rect x="2" y="2" width="8" height="8" rx="1" />
                    <path d="M4 5h4M4 7h2" />
                  </svg>
                  <span>{session.permission_mode === 'trusted' ? '信任' : session.permission_mode === 'moderate' ? '中等' : '严格'}</span>
                </div>
                <div className="meta-item">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <circle cx="6" cy="6" r="4" />
                    <path d="M6 3v3l2 1" />
                  </svg>
                  <span>{formatDate(session.updated_at)}</span>
                </div>
              </div>

              <div className="session-actions">
                <button
                  className="btn-open"
                  onClick={() => navigate(`/assistant?session=${session.id}`)}
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M3 11l8-8M6 3h5v5" />
                  </svg>
                  打开
                </button>

                {confirmDelete === session.id ? (
                  <div className="confirm-delete">
                    <span>确认?</span>
                    <button className="btn-confirm" onClick={() => deleteSession(session.id)}>是</button>
                    <button className="btn-cancel" onClick={() => setConfirmDelete(null)}>否</button>
                  </div>
                ) : (
                  <button
                    className="btn-delete"
                    onClick={() => setConfirmDelete(session.id)}
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M2 4h10M4.5 4V2.5a.5.5 0 01.5-.5h4a.5.5 0 01.5.5V4M11 4v7.5a.5.5 0 01-.5.5H3.5a.5.5 0 01-.5-.5V4" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}