/** Plugin Marketplace Component */
import React, { useState } from 'react'
import { Search, Filter, Star, Download, Package, ExternalLink, ChevronRight, CheckCircle } from 'lucide-react'
import { useStore } from '../store'

const CATEGORIES = ['All', 'Coding', 'Productivity', 'Automation', 'Fun', 'System']

const MOCK_PLUGINS = [
  { id: 'python-assistant', name: 'Python Code Assistant', description: 'Write, debug, refactor Python code with AI. Supports FastAPI, Django, Flask.', version: '2.1.0', author: 'ele-team', rating: 4.9, installs: 12400, category: 'Coding', permissions: ['file:read', 'file:write', 'shell:run'], icon: '🐍', installed: true },
  { id: 'web-scraper', name: 'Web Scraper Pro', description: 'Extract structured data from any website. Export to CSV, JSON, or Markdown.', version: '1.5.3', author: 'datawizard', rating: 4.7, installs: 8200, category: 'Automation', permissions: ['browser:navigate', 'file:write'], icon: '🌐', installed: false },
  { id: 'git-helper', name: 'Git Workflow Helper', description: 'Automate git operations: commit, branch, merge, rebase with smart suggestions.', version: '1.2.0', author: 'devtools', rating: 4.8, installs: 5600, category: 'Coding', permissions: ['shell:run', 'file:read'], icon: '📝', installed: false },
  { id: 'email-automation', name: 'Email Automation', description: 'Send, organize, and automate email workflows. Templates, scheduling, tracking.', version: '1.0.5', author: 'productivity-labs', rating: 4.5, installs: 3400, category: 'Productivity', permissions: ['email:send', 'email:read', 'calendar:write'], icon: '📧', installed: false },
  { id: 'system-monitor', name: 'System Monitor', description: 'Real-time system metrics: CPU, RAM, disk, network. Alerts and logging.', version: '2.0.1', author: 'sysadmin-tools', rating: 4.6, installs: 4100, category: 'System', permissions: ['shell:run', 'notifications'], icon: '📊', installed: false },
  { id: 'docker-manager', name: 'Docker Container Manager', description: 'Manage containers, images, volumes, networks. Compose support included.', version: '1.3.0', author: 'devops-pro', rating: 4.4, installs: 2800, category: 'System', permissions: ['shell:run', 'file:read'], icon: '🐳', installed: false },
]

export function Marketplace() {
  const { installedPlugins, addPlugin, removePlugin } = useStore()
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')
  const [view, setView] = useState<'grid' | 'list'>('grid')

  const filteredPlugins = MOCK_PLUGINS.filter(plugin => {
    const matchesSearch = plugin.name.toLowerCase().includes(search.toLowerCase()) || plugin.description.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = category === 'All' || plugin.category === category
    return matchesSearch && matchesCategory
  })

  const handleInstall = (pluginId: string) => { addPlugin(pluginId) }
  const handleUninstall = (pluginId: string) => { if (confirm('Uninstall this plugin?')) removePlugin(pluginId) }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Plugin Marketplace</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Discover and install plugins to extend ELE Agent</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setView('grid')} className={`p-2 rounded-lg ${view === 'grid' ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'}`}><Package className="w-5 h-5" /></button>
            <button onClick={() => setView('list')} className={`p-2 rounded-lg ${view === 'list' ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'}`}><Package className="w-5 h-5" /></button>
          </div>
        </div>

        <div className="card p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1"><Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" /><input type="text" placeholder="Search plugins..." value={search} onChange={(e) => setSearch(e.target.value)} className="input pl-10" /></div>
            <div className="flex items-center gap-2"><Filter className="w-5 h-5 text-gray-400" /><select value={category} onChange={(e) => setCategory(e.target.value)} className="input py-2 pr-8">{CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}</select></div>
          </div>
        </div>

        {view === 'grid' ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">{filteredPlugins.map(plugin => <PluginCardGrid key={plugin.id} plugin={plugin} onInstall={handleInstall} onUninstall={handleUninstall} />)}</div>
        ) : (
          <div className="space-y-4">{filteredPlugins.map(plugin => <PluginCardList key={plugin.id} plugin={plugin} onInstall={handleInstall} onUninstall={handleUninstall} />)}</div>
        )}

        {filteredPlugins.length === 0 && <div className="text-center py-12"><Package className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" /><h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No plugins found</h3><p className="text-gray-500 dark:text-gray-400 mt-1">Try adjusting your search or filter</p></div>}
      </div>
    </div>
  )
}

function PluginCardGrid({ plugin, onInstall, onUninstall }: any) {
  const isInstalled = plugin.installed
  return (
    <div className="card p-6 hover:shadow-lg transition-shadow flex flex-col">
      <div className="flex items-start justify-between mb-4"><span className="text-4xl">{plugin.icon}</span><span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400">v{plugin.version}</span></div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{plugin.name}</h3>
      <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 flex-1">{plugin.description}</p>
      <div className="flex items-center gap-4 mb-4 text-sm"><div className="flex items-center gap-1 text-gray-500 dark:text-gray-400"><Star className="w-4 h-4 fill-current text-yellow-500" /><span>{plugin.rating}</span></div><div className="flex items-center gap-1 text-gray-500 dark:text-gray-400"><Download className="w-4 h-4" /><span>{plugin.installs.toLocaleString()}</span></div><span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-400">{plugin.category}</span></div>
      <div className="flex flex-wrap gap-1 mb-4">{plugin.permissions.map((p: string, i: number) => <span key={i} className="px-2 py-0.5 text-xs bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">{p}</span>)}</div>
      <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-700"><span className="text-sm text-gray-500 dark:text-gray-400">by {plugin.author}</span><button onClick={() => isInstalled ? onUninstall(plugin.id) : onInstall(plugin.id)} className={`btn text-sm ${isInstalled ? 'btn-secondary' : 'btn-primary'}`}>{isInstalled ? <> <CheckCircle className="w-4 h-4 mr-2" /> Installed </> : 'Install'}</button></div>
    </div>
  )
}

function PluginCardList({ plugin, onInstall, onUninstall }: any) {
  const isInstalled = plugin.installed
  return (
    <div className="card p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-4">
        <span className="text-3xl">{plugin.icon}</span>
        <div className="flex-1 min-w-0"><div className="flex items-center gap-3"><h3 className="font-semibold text-gray-900 dark:text-gray-100">{plugin.name}</h3><span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400">v{plugin.version}</span><span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-400 text-xs">{plugin.category}</span></div><p className="text-gray-600 dark:text-gray-300 text-sm mt-1">{plugin.description}</p><div className="flex items-center gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400"><div className="flex items-center gap-1"><Star className="w-4 h-4 fill-current text-yellow-500" /><span>{plugin.rating}</span></div><div className="flex items-center gap-1"><Download className="w-4 h-4" /><span>{plugin.installs.toLocaleString()}</span></div><span className="text-gray-400">by {plugin.author}</span></div></div>
        <div className="flex flex-wrap gap-1">{plugin.permissions.map((p: string, i: number) => <span key={i} className="px-2 py-0.5 text-xs bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">{p}</span>)}</div>
        <button onClick={() => isInstalled ? onUninstall(plugin.id) : onInstall(plugin.id)} className={`btn text-sm ${isInstalled ? 'btn-secondary' : 'btn-primary'}`}>{isInstalled ? <> <CheckCircle className="w-4 h-4 mr-2" /> Installed </> : 'Install'}</button>
      </div>
    </div>
  )
}