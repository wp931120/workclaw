/** Skills management page - toggle user skills/capabilities. */

import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { Skill } from '../types'
import './SkillsPage.css'

export function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState<string | null>(null)

  useEffect(() => {
    loadSkills()
  }, [])

  async function loadSkills() {
    setLoading(true)
    try {
      const data = await api.listSkills()
      setSkills(data.skills || [])
    } catch (err) {
      console.error('Failed to load skills:', err)
    } finally {
      setLoading(false)
    }
  }

  async function toggleSkill(skill: Skill) {
    if (updating) return

    setUpdating(skill.id)
    try {
      const updated = await api.toggleSkill(skill.id)
      setSkills(prev => prev.map(s =>
        s.id === skill.id ? { ...s, enabled: updated.enabled } : s
      ))
    } catch (err) {
      console.error('Failed to toggle skill:', err)
    } finally {
      setUpdating(null)
    }
  }

  const groupedSkills = skills.reduce((acc, skill) => {
    const cat = skill.category || '其他'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(skill)
    return acc
  }, {} as Record<string, Skill[]>)

  function getSkillIcon(icon?: string) {
    switch (icon) {
      case 'calendar':
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="3" y="4" width="14" height="13" rx="2" />
            <path d="M3 8h14M7 2v4M13 2v4" />
          </svg>
        )
      case 'check':
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="3" y="3" width="14" height="14" rx="2" />
            <path d="M7 10l2 2 4-4" />
          </svg>
        )
      case 'file-text':
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M4 4h8l4 4v10a1 1 0 01-1 1H4a1 1 0 01-1-1V5a1 1 0 011-1z" />
            <path d="M12 4v4h4M10 10h4M10 13h4" />
          </svg>
        )
      case 'mail':
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="3" y="5" width="14" height="10" rx="2" />
            <path d="M3 7l7 4 7-4" />
          </svg>
        )
      case 'users':
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="7" cy="6" r="3" />
            <path d="M1 17v-1a4 4 0 014-4h4a4 4 0 014 4v1" />
            <circle cx="15" cy="6" r="2" />
            <path d="M16 14v-1a3 3 0 00-2-2.8" />
          </svg>
        )
      case 'search':
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="9" cy="9" r="6" />
            <path d="M15 15l-3-3" />
          </svg>
        )
      case 'file':
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M4 4h8l4 4v10a1 1 0 01-1 1H4a1 1 0 01-1-1V5a1 1 0 011-1z" />
            <path d="M12 4v4h4" />
          </svg>
        )
      default:
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M10 2l8 4v5l-8 5-8-5V6l8-4z" />
          </svg>
        )
    }
  }

  return (
    <div className="skills-page">
      <div className="skills-header">
        <h1>技能管理</h1>
        <p className="skills-subtitle">开启或关闭 AI 助手可以使用的技能</p>
      </div>

      {loading ? (
        <div className="skills-loading">
          <div className="loading-spinner" />
          <span>加载中...</span>
        </div>
      ) : (
        <div className="skills-content">
          {Object.entries(groupedSkills).map(([category, categorySkills]) => (
            <div key={category} className="skill-category">
              <div className="category-header">
                <span className="category-name">{category}</span>
                <span className="category-count">{categorySkills.length} 项</span>
              </div>
              <div className="skill-list">
                {categorySkills.map(skill => (
                  <div key={skill.id} className={`skill-card ${skill.enabled ? 'enabled' : 'disabled'}`}>
                    <div className="skill-icon">
                      {getSkillIcon(skill.icon)}
                    </div>
                    <div className="skill-info">
                      <div className="skill-title">{skill.title}</div>
                      <div className="skill-description">{skill.description}</div>
                      {skill.is_dangerous && (
                        <span className="skill-badge">危险操作</span>
                      )}
                    </div>
                    <button
                      className={`skill-toggle ${skill.enabled ? 'on' : 'off'} ${updating === skill.id ? 'updating' : ''}`}
                      onClick={() => toggleSkill(skill)}
                      disabled={!!updating || skill.read_only}
                    >
                      <span className="toggle-track">
                        <span className="toggle-thumb" />
                      </span>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}