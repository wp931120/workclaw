/** App layout — dark sidebar on desktop, bottom nav on mobile. */

import { Outlet, NavLink } from 'react-router-dom'
import './AppLayout.css'

const navItems = [
  { to: '/', end: true, label: '概览', icon: 'grid' },
  { to: '/assistant', end: false, label: '助手', icon: 'chat' },
  { to: '/tasks', end: false, label: '任务', icon: 'check' },
  { to: '/sessions', end: false, label: '会话', icon: 'history' },
] as const

function NavIcon({ name }: { name: string }) {
  switch (name) {
    case 'grid':
      return (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="2" width="6.5" height="6.5" rx="1.5" />
          <rect x="11.5" y="2" width="6.5" height="6.5" rx="1.5" />
          <rect x="2" y="11.5" width="6.5" height="6.5" rx="1.5" />
          <rect x="11.5" y="11.5" width="6.5" height="6.5" rx="1.5" />
        </svg>
      )
    case 'chat':
      return (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 10c0 3.866-3.134 7-7 7a7.46 7.46 0 01-2.74-.52L4 17l1.18-2.65A6.96 6.96 0 013 10c0-3.866 3.134-7 7-7s7 3.134 7 7z" />
          <circle cx="7.5" cy="10" r="0.75" fill="currentColor" />
          <circle cx="10" cy="10" r="0.75" fill="currentColor" />
          <circle cx="12.5" cy="10" r="0.75" fill="currentColor" />
        </svg>
      )
    case 'check':
      return (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="3" width="16" height="14" rx="2" />
          <path d="M6 7.5l2 2 4-4" />
          <path d="M12 11.5h2" />
        </svg>
      )
    case 'history':
      return (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 10a7 7 0 1114 0 7 7 0 01-14 0z" />
          <path d="M10 6v4.5l3 1.5" />
        </svg>
      )
    default:
      return null
  }
}

export function AppLayout() {
  return (
    <div className="app-layout">
      {/* Desktop sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M3 6l6-3v6l-6 3V6z" fill="var(--accent)" opacity="0.9" />
              <path d="M11 3l6 3v6l-6-3V3z" fill="var(--accent)" opacity="0.6" />
              <path d="M3 12l6 3v6l-6-3v-6z" fill="var(--accent)" opacity="0.4" />
              <path d="M11 12l6 3v6l-6-3v-6z" fill="var(--accent)" opacity="0.7" />
            </svg>
          </div>
          <span className="brand-name">WorkClaw</span>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <NavIcon name={item.icon} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-status">
            <span className="status-dot" />
            <span>在线</span>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <main className="main-content">
        <Outlet />
      </main>

      {/* Mobile bottom nav */}
      <nav className="bottom-nav">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `bottom-nav-item ${isActive ? 'active' : ''}`}
          >
            <NavIcon name={item.icon} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
