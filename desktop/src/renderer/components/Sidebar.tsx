/** Sidebar Navigation */
import React from 'react'
import { MessageSquare, LayoutDashboard, Plug, ShoppingBag, Settings, Bot, X, ChevronRight } from 'lucide-react'
import { useStore } from '../store'

const NAV_ITEMS = [
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'plugins', label: 'Plugins', icon: Plug },
  { id: 'marketplace', label: 'Marketplace', icon: ShoppingBag },
  { id: 'settings', label: 'Settings', icon: Settings },
] as const

type NavId = typeof NAV_ITEMS[number]['id']

interface SidebarProps {
  currentView: NavId
  onViewChange: (view: NavId) => void
}

export function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const { isSidebarCollapsed, toggleSidebar } = useStore()

  return (
    <aside className={`sidebar transition-all duration-300 bg-white dark:bg-gray-800 border-r border-gray-100 dark:border-gray-700 flex flex-col ${isSidebarCollapsed ? 'w-16' : 'w-64'}`}>
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <Bot className="text-primary-600 dark:text-primary-400" size={28} />
          {!isSidebarCollapsed && <span className="text-xl font-bold text-gray-900 dark:text-gray-100">ELE Agent</span>}
        </div>
        <button onClick={toggleSidebar} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors" aria-label={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
          {isSidebarCollapsed ? <ChevronRight className="w-5 h-5" /> : <X className="w-5 h-5" />}
        </button>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => onViewChange(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${currentView === item.id ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'}`}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!isSidebarCollapsed && <span>{item.label}</span>}
          </button>
        ))}
      </nav>

      <div className="p-3 border-t border-gray-100 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">v1.0.0</div>
      </div>
    </aside>
  )
}