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
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Dashboard</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total Messages', value: '1,234', icon: '🤖', color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' },
          { label: 'Tasks Completed', value: '567', icon: '✅', color: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' },
          { label: 'Active Sessions', value: '23', icon: '📊', color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400' },
          { label: 'Avg Response', value: '1.2s', icon: '⚡', color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400' },
        ].map((stat, i) => (
          <div key={i} className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-xl ${stat.color}`}>{stat.icon}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function App() {
  const { currentView, setCurrentView, isOverlayVisible, overlayStatus } = useStore()
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

  if (!mounted) return <div className="loading">Loading...</div>

  return (
    <div className="app h-screen w-screen flex bg-gray-50 dark:bg-gray-900">
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />

      <main className="flex-1 flex flex-col overflow-hidden">
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