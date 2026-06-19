/** Tasks page — clean task list with status filters, priority badges, and quick actions. */

import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { Task } from '../types'
import './TasksPage.css'

type FilterType = 'all' | 'pending' | 'in_progress' | 'completed'

export function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [filter, setFilter] = useState<FilterType>('all')
  const [showForm, setShowForm] = useState(false)
  const [newTask, setNewTask] = useState({ title: '', description: '', priority: 'medium' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTasks()
  }, [])

  async function loadTasks() {
    setLoading(true)
    try {
      const data = await api.listTasks()
      setTasks(data.tasks || [])
    } catch (e) {
      console.error('Failed to load tasks:', e)
    } finally {
      setLoading(false)
    }
  }

  async function createTask(e: React.FormEvent) {
    e.preventDefault()
    if (!newTask.title.trim()) return

    try {
      const task = await api.createTask(newTask)
      setTasks([task, ...tasks])
      setNewTask({ title: '', description: '', priority: 'medium' })
      setShowForm(false)
    } catch (e) {
      console.error('Failed to create task:', e)
    }
  }

  async function toggleStatus(task: Task) {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed'
    try {
      const updated = await api.updateTask(task.id, { status: newStatus })
      setTasks(tasks.map(t => t.id === task.id ? updated : t))
    } catch (e) {
      console.error('Failed to update task:', e)
    }
  }

  async function deleteTask(taskId: string) {
    try {
      await api.deleteTask(taskId)
      setTasks(tasks.filter(t => t.id !== taskId))
    } catch (e) {
      console.error('Failed to delete task:', e)
    }
  }

  const filteredTasks = filter === 'all' ? tasks : tasks.filter(t => t.status === filter)

  const filterButtons: { key: FilterType; label: string; count: number }[] = [
    { key: 'all', label: '全部', count: tasks.length },
    { key: 'pending', label: '待办', count: tasks.filter(t => t.status === 'pending').length },
    { key: 'in_progress', label: '进行中', count: tasks.filter(t => t.status === 'in_progress').length },
    { key: 'completed', label: '已完成', count: tasks.filter(t => t.status === 'completed').length },
  ]

  return (
    <div className="tasks-page">
      <header className="page-header">
        <h1>任务管理</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M7 2v10M2 7h10" />
          </svg>
          {showForm ? '取消' : '新建任务'}
        </button>
      </header>

      {/* Filter tabs */}
      <div className="filter-tabs">
        {filterButtons.map(btn => (
          <button
            key={btn.key}
            className={`filter-tab ${filter === btn.key ? 'active' : ''}`}
            onClick={() => setFilter(btn.key)}
          >
            <span className="filter-label">{btn.label}</span>
            <span className="filter-count">{btn.count}</span>
          </button>
        ))}
      </div>

      {/* New task form */}
      {showForm && (
        <form className="task-form" onSubmit={createTask}>
          <input
            type="text"
            className="form-input"
            placeholder="任务标题"
            value={newTask.title}
            onChange={e => setNewTask({ ...newTask, title: e.target.value })}
            required
            autoFocus
          />
          <input
            type="text"
            className="form-input"
            placeholder="描述（可选）"
            value={newTask.description}
            onChange={e => setNewTask({ ...newTask, description: e.target.value })}
          />
          <div className="form-row">
            <select
              className="form-select"
              value={newTask.priority}
              onChange={e => setNewTask({ ...newTask, priority: e.target.value })}
            >
              <option value="low">低优先级</option>
              <option value="medium">中优先级</option>
              <option value="high">高优先级</option>
            </select>
            <button type="submit" className="btn-primary">创建</button>
          </div>
        </form>
      )}

      {/* Task list */}
      {loading ? (
        <div className="loading">加载中...</div>
      ) : filteredTasks.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="4" y="4" width="24" height="24" rx="4" />
              <path d="M10 16l3 3 7-7" />
            </svg>
          </div>
          <p>{filter === 'all' ? '暂无任务' : `暂无${filterButtons.find(b => b.key === filter)?.label}的任务`}</p>
          {filter === 'all' && (
            <button className="btn-ghost" onClick={() => setShowForm(true)}>创建第一个任务</button>
          )}
        </div>
      ) : (
        <div className="task-list">
          {filteredTasks.map(task => (
            <div key={task.id} className={`task-item ${task.status}`}>
              <label className="task-checkbox">
                <input
                  type="checkbox"
                  checked={task.status === 'completed'}
                  onChange={() => toggleStatus(task)}
                />
                <span className="checkmark">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M2 6l3 3 5-5" />
                  </svg>
                </span>
              </label>

              <div className="task-content">
                <span className="task-title">{task.title}</span>
                {task.description && <span className="task-desc">{task.description}</span>}
                <div className="task-meta">
                  <span className={`priority priority-${task.priority}`}>
                    {task.priority === 'high' ? '高' : task.priority === 'medium' ? '中' : '低'}
                  </span>
                  {task.due_date && (
                    <span className="due-date">
                      截止 {new Date(task.due_date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                    </span>
                  )}
                </div>
              </div>

              <button className="btn-delete" onClick={() => deleteTask(task.id)} title="删除">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M2 4h12M5.5 4V2.5a1 1 0 011-1h3a1 1 0 011 1V4M12 4v9a1 1 0 01-1 1H5a1 1 0 01-1-1V4" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}