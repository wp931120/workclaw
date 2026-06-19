/** Dashboard — cockpit briefing style: status cards, quick actions, recent sessions. */

import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Task, Session, Capability } from '../types'
import './Dashboard.css'

export function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [capabilities, setCapabilities] = useState<Capability[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const [tasksData, sessionsData, capsData] = await Promise.all([
          api.listTasks(),
          api.listSessions(),
          api.listCapabilities(),
        ])
        setTasks(tasksData.tasks || [])
        setSessions(sessionsData || [])
        setCapabilities(capsData.capabilities || [])
      } catch (e) {
        console.error('Failed to load dashboard data:', e)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  if (loading) {
    return <div className="dashboard-loading">加载中...</div>
  }

  // Stats
  const pendingTasks = tasks.filter(t => t.status === 'pending')
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress')
  const completedTasks = tasks.filter(t => t.status === 'completed')
  const activeSessions = sessions.filter(s => s.status === 'active')

  const today = new Date()
  const greeting = today.getHours() < 12 ? '早上好' : today.getHours() < 18 ? '下午好' : '晚上好'

  return (
    <div className="dashboard">
      {/* Header — greeting */}
      <header className="dashboard-header">
        <div className="greeting">
          <h1>{greeting}</h1>
          <p>这是您的工作简报</p>
        </div>
        <div className="header-time">
          {today.toLocaleDateString('zh-CN', { weekday: 'long', month: 'short', day: 'numeric' })}
        </div>
      </header>

      {/* Status grid — cockpit style */}
      <section className="status-grid">
        <Link to="/tasks" className="status-card">
          <div className="status-card-icon pending">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="5" cy="10" r="1.5" fill="currentColor" />
              <circle cx="10" cy="10" r="1.5" fill="currentColor" />
              <circle cx="15" cy="10" r="1.5" fill="currentColor" />
              <path d="M2 6h16v1.5H2z" />
              <path d="M2 12.5h16V14H2z" />
            </svg>
          </div>
          <div className="status-card-content">
            <span className="status-value">{pendingTasks.length}</span>
            <span className="status-label">待办</span>
          </div>
          <div className="status-card-indicator" />
        </Link>

        <Link to="/tasks" className="status-card">
          <div className="status-card-icon progress">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M3 10l4-3 4 2 6-4v5l-6 4-4-2-4 3V10z" />
            </svg>
          </div>
          <div className="status-card-content">
            <span className="status-value">{inProgressTasks.length}</span>
            <span className="status-label">进行中</span>
          </div>
          <div className="status-card-indicator" />
        </Link>

        <Link to="/tasks" className="status-card">
          <div className="status-card-icon done">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M3 10l4 4 10-12" />
            </svg>
          </div>
          <div className="status-card-content">
            <span className="status-value">{completedTasks.length}</span>
            <span className="status-label">已完成</span>
          </div>
          <div className="status-card-indicator" />
        </Link>

        <Link to="/sessions" className="status-card">
          <div className="status-card-icon sessions">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M10 2a8 8 0 100 16 8 8 0 000-16z" />
              <path d="M10 6v4l2.5 1.5" />
            </svg>
          </div>
          <div className="status-card-content">
            <span className="status-value">{activeSessions.length}</span>
            <span className="status-label">活跃会话</span>
          </div>
          <div className="status-card-indicator" />
        </Link>
      </section>

      {/* Quick actions */}
      <section className="quick-actions">
        <Link to="/assistant" className="quick-action">
          <div className="quick-action-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M14 8c0 2.71-2.19 5-5 5a5 5 0 01-1.92-.38L3 15l.83-1.85A4.96 4.96 0 012 8c0-2.71 2.19-5 5-5s5 2.29 5 5z" />
            </svg>
          </div>
          <span>开始新对话</span>
        </Link>
        <Link to="/tasks" className="quick-action">
          <div className="quick-action-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="2" y="2" width="14" height="14" rx="2" />
              <path d="M5 9l2 2 4-4" />
            </svg>
          </div>
          <span>添加任务</span>
        </Link>
        <Link to="/sessions" className="quick-action">
          <div className="quick-action-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M2 9a7 7 0 1114 0 7 7 0 01-14 0z" />
              <path d="M9 5v4l2 1" />
            </svg>
          </div>
          <span>查看历史</span>
        </Link>
      </section>

      {/* Two-column: Recent sessions + Capabilities */}
      <div className="dashboard-columns">
        {/* Recent sessions */}
        <section className="dashboard-section recent-sessions">
          <header className="section-header">
            <h2>最近会话</h2>
            <Link to="/sessions" className="section-link">查看全部 →</Link>
          </header>
          <div className="session-list">
            {sessions.length === 0 ? (
              <div className="empty-card">
                <p>暂无会话记录</p>
                <Link to="/assistant" className="btn-ghost btn-sm">开始第一个会话</Link>
              </div>
            ) : (
              sessions.slice(0, 4).map(session => (
                <Link key={session.id} to={`/assistant?session=${session.id}`} className="session-item">
                  <div className="session-icon">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M12 6c0 1.66-1.34 3-3 3a3 3 0 01-1.64-.56L5 10l.78-1.76A2.98 2.98 0 013 6c0-1.66 1.34-3 3-3s3 1.34 3 3h2z" />
                    </svg>
                  </div>
                  <div className="session-info">
                    <span className="session-title">{session.title}</span>
                    <span className="session-date">
                      {new Date(session.updated_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <span className={`session-status ${session.status}`}>{session.status === 'active' ? '活跃' : '已归档'}</span>
                </Link>
              ))
            )}
          </div>
        </section>

        {/* Capabilities library */}
        <section className="dashboard-section capabilities">
          <header className="section-header">
            <h2>能力库</h2>
            <span className="section-count">{capabilities.length} 项</span>
          </header>
          <div className="capability-list">
            {capabilities.length === 0 ? (
              <div className="empty-card">
                <p>暂无可用能力</p>
              </div>
            ) : (
              capabilities.slice(0, 6).map(cap => (
                <div key={cap.name} className="capability-item">
                  <div className="capability-icon">
                    {cap.is_dangerous ? (
                      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M7 1v6M7 11v1M1 7h1M12 7h1M2.64 2.64l.7.7M10.66 10.66l.7.7M2.64 11.36l.7-.7M10.66 3.34l.7-.7" />
                      </svg>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M7 1l6 4v4l-6 4-6-4V5l6-4z" />
                      </svg>
                    )}
                  </div>
                  <div className="capability-info">
                    <span className="capability-name">{cap.name}</span>
                    <span className="capability-desc">{cap.description}</span>
                  </div>
                  {cap.is_dangerous && <span className="capability-badge">需确认</span>}
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Pending tasks preview */}
      {pendingTasks.length > 0 && (
        <section className="dashboard-section pending-tasks">
          <header className="section-header">
            <h2>待办事项</h2>
            <Link to="/tasks" className="section-link">查看全部 →</Link>
          </header>
          <div className="pending-task-list">
            {pendingTasks.slice(0, 3).map(task => (
              <div key={task.id} className="pending-task-item">
                <span className={`priority-dot priority-${task.priority}`} />
                <span className="task-title">{task.title}</span>
                {task.due_date && (
                  <span className="task-due">截止 {new Date(task.due_date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}</span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}