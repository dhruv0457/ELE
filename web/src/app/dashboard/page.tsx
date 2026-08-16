'use client'

import { useStore } from '@/store/useStore'
import { Bot, Terminal, Mic, Plug, ShoppingBag, TrendingUp, Clock, CheckCircle, AlertCircle, Activity } from 'lucide-react'

const stats = [
  { label: 'Total Messages', value: '1,234', change: '+12%', icon: Bot, color: 'text-blue-500' },
  { label: 'Tasks Completed', value: '567', change: '+8%', icon: CheckCircle, color: 'text-green-500' },
  { label: 'Active Sessions', value: '23', change: '-2%', icon: Activity, color: 'text-purple-500' },
  { label: 'Avg Response Time', value: '1.2s', change: '-5%', icon: Clock, color: 'text-orange-500' },
]

const recentActivity = [
  { time: '2 min ago', action: 'Created React dashboard', type: 'code', status: 'success' },
  { time: '15 min ago', action: 'Scraped competitor pricing', type: 'web', status: 'success' },
  { time: '1 hour ago', action: 'Refactored auth module', type: 'code', status: 'success' },
  { time: '3 hours ago', action: 'Organized downloads folder', type: 'file', status: 'success' },
  { time: '5 hours ago', action: 'Failed: Deploy to Vercel', type: 'shell', status: 'error' },
]

const usageData = [
  { day: 'Mon', messages: 45, tokens: 12000 },
  { day: 'Tue', messages: 52, tokens: 15000 },
  { day: 'Wed', messages: 38, tokens: 11000 },
  { day: 'Thu', messages: 61, tokens: 18000 },
  { day: 'Fri', messages: 55, tokens: 16000 },
  { day: 'Sat', messages: 28, tokens: 8000 },
  { day: 'Sun', messages: 32, tokens: 9000 },
]

export default function DashboardPage() {
  const { settings } = useStore()

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Overview of your ELE Agent activity</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <Activity className="w-4 h-4 text-green-500 animate-pulse" />
          <span>Connected</span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, i) => (
          <div key={i} className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-xl bg-gray-100 dark:bg-gray-800 ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2">
              <TrendingUp className={`w-4 h-4 ${stat.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`} />
              <span className={`text-sm ${stat.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>{stat.change}</span>
              <span className="text-sm text-gray-500 dark:text-gray-400">vs last week</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Weekly Usage</h2>
          <div className="h-64 flex items-end justify-between gap-2">
            {usageData.map((day, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full bg-primary-500 dark:bg-primary-400 rounded-t transition-all hover:bg-primary-600" style={{ height: `${(day.messages / 61) * 100}%` }} />
                <span className="text-xs text-gray-500 dark:text-gray-400">{day.day}</span>
                <span className="text-xs font-medium text-gray-900 dark:text-gray-100">{day.messages}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">Messages per day</p>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Token Usage</h2>
          <div className="h-64 flex items-end justify-between gap-2">
            {usageData.map((day, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full bg-green-500 dark:bg-green-400 rounded-t transition-all hover:bg-green-600" style={{ height: `${(day.tokens / 18000) * 100}%` }} />
                <span className="text-xs text-gray-500 dark:text-gray-400">{day.day}</span>
                <span className="text-xs font-medium text-gray-900 dark:text-gray-100">{Math.round(day.tokens / 1000)}k</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">Tokens per day (thousands)</p>
        </div>
      </div>

      <div className="card">
        <div className="p-6 border-b border-gray-100 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Recent Activity</h2>
        </div>
        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {recentActivity.map((activity, i) => (
            <div key={i} className="p-4 flex items-center gap-4 hover:bg-gray-50 dark:hover:bg-gray-800/50">
              <div className={`p-2 rounded-lg ${activity.type === 'code' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' : activity.type === 'web' ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' : activity.type === 'file' ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' : 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400'}`}>
                {activity.type === 'code' && <Terminal className="w-5 h-5" />}
                {activity.type === 'web' && <Bot className="w-5 h-5" />}
                {activity.type === 'file' && <Bot className="w-5 h-5" />}
                {activity.type === 'shell' && <Terminal className="w-5 h-5" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 dark:text-gray-100 truncate">{activity.action}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{activity.time}</p>
              </div>
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${activity.status === 'success' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'}`}>
                {activity.status === 'success' ? (
                  <>
                    <CheckCircle className="w-3 h-3" />
                    Success
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3 h-3" />
                    Failed
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Quick Actions</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <QuickAction title="New Chat" description="Start a conversation with ELE" icon={Bot} href="/chat" primary />
            <QuickAction title="Browse Marketplace" description="Discover new plugins" icon={ShoppingBag} href="/marketplace" />
            <QuickAction title="Manage Plugins" description="Configure installed plugins" icon={Plug} href="/plugins" />
            <QuickAction title="Settings" description="Customize your experience" icon={Mic} href="/settings" />
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">System Status</h2>
          <div className="space-y-4">
            <StatusItem label="API Connection" status="online" />
            <StatusItem label="WebSocket" status="online" />
            <StatusItem label="Supabase Auth" status="online" />
            <StatusItem label="RAG Indexer" status="online" />
            <StatusItem label="Voice Engine" status={settings.voice.wake_word_enabled ? 'online' : 'offline'} />
            <StatusItem label="Plugin System" status="online" />
          </div>
        </div>
      </div>
    </div>
  )
}

function QuickAction({ title, description, icon: Icon, href, primary }: { title: string, description: string, icon: React.ComponentType<any>, href: string, primary?: boolean }) {
  return (
    <a href={href} className={`p-4 rounded-xl border transition-all hover:shadow-md ${primary ? 'bg-primary-50 border-primary-200 dark:bg-primary-900/30 dark:border-primary-800' : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700'}`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${primary ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">{title}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
        </div>
      </div>
    </a>
  )
}

function StatusItem({ label, status }: { label: string, status: 'online' | 'offline' }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-700 dark:text-gray-300">{label}</span>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
        <span className={`text-xs font-medium ${status === 'online' ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'}`}>
          {status === 'online' ? 'Online' : 'Offline'}
        </span>
      </div>
    </div>
  )
}