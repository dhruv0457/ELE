/**
 * ELE Agent — Minimal Developer Sidebar
 * Pure black, icon-first, sessions list with disk restore, session create.
 */
import React from 'react'
import {
  MessageSquare,
  Settings,
  Plus,
  Radio,
  ChevronLeft,
  ChevronRight,
  Terminal,
  Clock,
  Cpu,
} from 'lucide-react'
import { useStore } from '../store'

interface SidebarProps {
  currentView: string
  onViewChange: (view: any) => void
}

export function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const {
    isSidebarCollapsed,
    toggleSidebar,
    sessions,
    currentSessionId,
    createSession,
    switchSession,
    activeModel,
    activeProvider,
    toggleJarvisLive,
    isJarvisLiveOpen,
  } = useStore()

  const navItems = [
    { id: 'chat',     label: 'Chat',     icon: MessageSquare, accent: 'var(--cyan)' },
    { id: 'settings', label: 'Settings', icon: Settings,      accent: 'var(--muted)' },
  ] as const

  return (
    <aside
      className="flex flex-col border-r flex-shrink-0 transition-all duration-200"
      style={{
        width: isSidebarCollapsed ? 56 : 224,
        background: 'var(--surface)',
        borderColor: 'var(--border)',
      }}
    >
      {/* ── Logo / Brand ───────────────────────────────────────── */}
      <div
        className="flex items-center border-b flex-shrink-0"
        style={{
          height: 48,
          padding: isSidebarCollapsed ? '0 16px' : '0 16px',
          borderColor: 'var(--border)',
        }}
      >
        <div
          className="w-7 h-7 rounded flex items-center justify-center font-mono font-bold text-xs flex-shrink-0"
          style={{ background: 'rgba(88,166,255,0.12)', color: 'var(--cyan)' }}
        >
          ele
        </div>
        {!isSidebarCollapsed && (
          <div className="ml-2.5 flex-1 min-w-0">
            <div className="font-mono font-bold text-xs" style={{ color: 'var(--text-primary)' }}>
              ELE Agent
            </div>
            <div className="font-mono text-[10px]" style={{ color: 'var(--muted)' }}>
              v2.0 · developer
            </div>
          </div>
        )}
        <button
          type="button"
          onClick={toggleSidebar}
          className="p-1 rounded transition-colors ml-auto"
          style={{ color: 'var(--muted)' }}
        >
          {isSidebarCollapsed
            ? <ChevronRight className="w-3.5 h-3.5" />
            : <ChevronLeft className="w-3.5 h-3.5" />
          }
        </button>
      </div>

      {/* ── Nav items ──────────────────────────────────────────── */}
      <nav className="flex flex-col gap-0.5 p-2 flex-shrink-0">
        {navItems.map(({ id, label, icon: Icon, accent }) => {
          const isActive = currentView === id
          return (
            <button
              key={id}
              type="button"
              onClick={() => onViewChange(id)}
              className="flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-mono transition-all text-left"
              style={{
                background: isActive ? 'rgba(88,166,255,0.08)' : 'transparent',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                borderLeft: `2px solid ${isActive ? accent : 'transparent'}`,
              }}
              title={label}
            >
              <Icon className="w-3.5 h-3.5 flex-shrink-0" style={{ color: isActive ? accent : 'var(--muted)' }} />
              {!isSidebarCollapsed && <span>{label}</span>}
            </button>
          )
        })}

        {/* JARVIS Live toggle */}
        <button
          type="button"
          onClick={toggleJarvisLive}
          className="flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-mono transition-all"
          style={{
            background: isJarvisLiveOpen ? 'rgba(247,120,186,0.08)' : 'transparent',
            color: isJarvisLiveOpen ? 'var(--pink)' : 'var(--text-secondary)',
            borderLeft: `2px solid ${isJarvisLiveOpen ? 'var(--pink)' : 'transparent'}`,
          }}
          title="JARVIS Live Voice"
        >
          <Radio className="w-3.5 h-3.5 flex-shrink-0" style={{ color: isJarvisLiveOpen ? 'var(--pink)' : 'var(--muted)' }} />
          {!isSidebarCollapsed && <span>JARVIS Voice</span>}
        </button>
      </nav>

      {/* ── Divider ────────────────────────────────────────────── */}
      <div style={{ height: 1, background: 'var(--border)', margin: '4px 12px' }} />

      {/* ── Sessions list ──────────────────────────────────────── */}
      {!isSidebarCollapsed && (
        <div className="flex-1 overflow-y-auto">
          {/* Header */}
          <div
            className="flex items-center justify-between px-4 py-2 sticky top-0"
            style={{ background: 'var(--surface)' }}
          >
            <div
              className="text-[10px] uppercase tracking-widest font-mono font-semibold"
              style={{ color: 'var(--muted)' }}
            >
              Sessions
            </div>
            <button
              type="button"
              onClick={() => createSession()}
              className="p-1 rounded transition-colors"
              style={{ color: 'var(--muted)' }}
              title="New session"
            >
              <Plus className="w-3 h-3" />
            </button>
          </div>

          <div className="px-2 pb-2 space-y-0.5">
            {sessions.map((ses) => {
              const isActive = ses.id === currentSessionId
              return (
                <button
                  key={ses.id}
                  type="button"
                  onClick={() => { switchSession(ses.id); onViewChange('chat') }}
                  className={`session-item w-full text-left px-3 py-2 rounded-md flex items-start gap-2 text-xs font-mono transition-all ${isActive ? 'active' : ''}`}
                  style={{
                    color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  }}
                >
                  <MessageSquare className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: isActive ? 'var(--cyan)' : 'var(--muted)' }} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate">{ses.name}</div>
                    <div className="flex items-center gap-1 mt-0.5" style={{ color: 'var(--muted)', fontSize: 10 }}>
                      <Clock className="w-2.5 h-2.5" />
                      <span>{new Date(ses.createdAt).toLocaleDateString()}</span>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* ── Collapsed: only new session icon ───────────────────── */}
      {isSidebarCollapsed && (
        <div className="flex-1 flex flex-col items-center pt-2 gap-2">
          <button
            type="button"
            onClick={() => createSession()}
            className="p-2 rounded transition-colors"
            style={{ color: 'var(--muted)' }}
            title="New session"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* ── Footer: active model ───────────────────────────────── */}
      <div
        className="flex-shrink-0 border-t p-3"
        style={{ borderColor: 'var(--border)' }}
      >
        {!isSidebarCollapsed ? (
          <div
            className="flex items-center gap-2 font-mono text-[10px]"
            style={{ color: 'var(--muted)' }}
          >
            <Cpu className="w-3 h-3 flex-shrink-0" style={{ color: 'var(--cyan)' }} />
            <span className="truncate">
              <span style={{ color: 'var(--cyan)' }}>{activeProvider.toUpperCase()}</span>
              {' · '}
              <span>{activeModel.split('/').pop()}</span>
            </span>
          </div>
        ) : (
          <div className="flex justify-center">
            <Cpu className="w-3.5 h-3.5" style={{ color: 'var(--cyan)' }} />
          </div>
        )}
      </div>
    </aside>
  )
}