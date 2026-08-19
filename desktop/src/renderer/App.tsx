/** Main App Component */
import React, { useEffect, useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { ChatWindow } from './components/ChatWindow'
import { Overlay } from './components/Overlay'
import { SettingsPanel } from './components/SettingsPanel'
import { Marketplace } from './components/Marketplace'
import { PluginManager } from './components/PluginManager'
import { useStore } from './store'

type View = 'chat' | 'dashboard' | 'plugins' | 'marketplace' | 'settings'

function Dashboard() {
  return (
    <div className="flex-1 p-6 overflow-auto">
      <h1 className="text-2xl font-bold text-gray-100 mb-6">System Dashboard</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total Messages', value: '1,234', icon: '⚡', color: 'bg-cyan-900/30 text-cyan-400 border border-cyan-500/30' },
          { label: 'Tasks Completed', value: '567', icon: '✓', color: 'bg-emerald-900/30 text-emerald-400 border border-emerald-500/30' },
          { label: 'Active Sessions', value: '12', icon: '📊', color: 'bg-purple-900/30 text-purple-400 border border-purple-500/30' },
          { label: 'Avg Latency', value: '< 1s', icon: '⚡', color: 'bg-orange-900/30 text-orange-400 border border-orange-500/30' },
        ].map((stat, i) => (
          <div key={i} className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-100 mt-1 font-mono">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-2xl ${stat.color} font-mono text-lg`}>{stat.icon}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function App() {
  const { currentView, setCurrentView, isOverlayVisible, overlayStatus, theme } = useStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)

    const handleShow = (status: string) => {
      useStore.getState().setOverlayStatus(status as any)
      useStore.getState().setOverlayVisible(true)
    }

    const handleHide = () => {
      useStore.getState().setOverlayVisible(false)
    }

    window.ele?.on('overlay:show', handleShow)
    window.ele?.on('overlay:hide', handleHide)

    return () => {
      window.ele?.off('overlay:show', handleShow)
      window.ele?.off('overlay:hide', handleHide)
    }
  }, [])

  if (!mounted) return <div className="loading text-white bg-gray-950 flex items-center justify-center h-screen">Loading ELE Agent...</div>

  return (
    <div className={`app h-screen w-screen flex overflow-hidden theme-${theme} bg-[var(--bg-primary)] text-[var(--text-primary)]`}>
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />

      <main className="flex-1 flex flex-col overflow-hidden bg-[var(--bg-primary)]">
        {currentView === 'chat' && <ChatWindow />}
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'plugins' && <PluginManager />}
        {currentView === 'marketplace' && <Marketplace />}
        {currentView === 'settings' && <SettingsPanel />}
      </main>

      {isOverlayVisible && <Overlay status={overlayStatus} />}
    </div>
  )
}