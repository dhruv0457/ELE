/** Plugin Manager Component */
import React, { useState } from 'react'
import { Plus, Trash2, Settings, ToggleLeft, ToggleRight, ExternalLink, RefreshCw, Loader2 } from 'lucide-react'
import { useStore } from '../store'

const MOCK_INSTALLED = [
  { id: 'python-assistant', name: 'Python Code Assistant', version: '2.1.0', description: 'Write, debug, refactor Python code with AI', author: 'ele-team', enabled: true, permissions: ['file:read', 'file:write', 'shell:run'], config: { default_model: 'gpt-4', auto_format: true } },
  { id: 'web-scraper', name: 'Web Scraper Pro', version: '1.5.3', description: 'Extract structured data from any website', author: 'datawizard', enabled: true, permissions: ['browser:navigate', 'file:write'], config: { timeout: 30000, user_agent: 'ELEBot/1.0' } },
  { id: 'git-helper', name: 'Git Workflow Helper', version: '1.2.0', description: 'Automate git operations with smart suggestions', author: 'devtools', enabled: false, permissions: ['shell:run', 'file:read'], config: { auto_commit: false } },
]

export function PluginManager() {
  const [plugins, setPlugins] = useState(MOCK_INSTALLED)
  const [showCreate, setShowCreate] = useState(false)
  const [editingConfig, setEditingConfig] = useState<string | null>(null)
  const [configValues, setConfigValues] = useState<Record<string, any>>({})

  const togglePlugin = (id: string) => {
    setPlugins(prev => prev.map(p => p.id === id ? { ...p, enabled: !p.enabled } : p))
  }

  const uninstallPlugin = (id: string) => {
    if (confirm('Uninstall this plugin?')) {
      setPlugins(prev => prev.filter(p => p.id !== id))
    }
  }

  const openConfig = (plugin: typeof MOCK_INSTALLED[0]) => {
    setEditingConfig(plugin.id)
    setConfigValues({ ...plugin.config })
  }

  const saveConfig = (id: string) => {
    setPlugins(prev => prev.map(p => p.id === id ? { ...p, config: configValues } : p))
    setEditingConfig(null)
  }

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Installed Plugins</h1>
          <button className="btn-primary flex items-center gap-2" onClick={() => setShowCreate(true)}><Plus className="w-4 h-4" /> Install Plugin</button>
        </div>

        {showCreate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowCreate(false)}>
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
              <h2 className="text-xl font-bold mb-4">Install New Plugin</h2>
              <input type="text" placeholder="Plugin URL or manifest path" className="input mb-4" />
              <div className="flex justify-end gap-2">
                <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button className="btn-primary">Install</button>
              </div>
            </div>
          </div>
        )}

        {editingConfig && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setEditingConfig(null)}>
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
              <h2 className="text-xl font-bold mb-4">Configure Plugin</h2>
              <div className="space-y-4 max-h-64 overflow-y-auto">
                {Object.entries(configValues).map(([key, value]) => (
                  <div key={key} className="flex items-center gap-3">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300 w-32">{key}</label>
                    <input type={typeof value === 'boolean' ? 'checkbox' : 'text'} defaultChecked={value} defaultValue={String(value)} onChange={(e) => setConfigValues(prev => ({ ...prev, [key]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))} className="input flex-1" />
                  </div>
                ))}
              </div>
              <div className="flex justify-end gap-2 mt-4">
                <button className="btn-secondary" onClick={() => setEditingConfig(null)}>Cancel</button>
                <button className="btn-primary" onClick={() => saveConfig(editingConfig!)}>Save</button>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {plugins.map(plugin => (
            <div key={plugin.id} className="card p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className="p-3 rounded-lg bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400"><Package className="w-6 h-6" /></div>
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100">{plugin.name}</h3>
                      <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400">v{plugin.version}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${plugin.enabled ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}`}>{plugin.enabled ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{plugin.description}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {plugin.permissions.map((p: string, i: number) => <span key={i} className="px-2 py-0.5 text-xs bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">{p}</span>)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => togglePlugin(plugin.id)} className={`p-2 rounded-lg transition-colors ${plugin.enabled ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'}`}><ToggleRight className="w-5 h-5" /></button>
                  <button onClick={() => openConfig(plugin)} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"><Settings className="w-5 h-5 text-gray-500 dark:text-gray-400" /></button>
                  <button onClick={() => uninstallPlugin(plugin.id)} className="p-2 rounded-lg hover:bg-red-100 text-red-500 dark:hover:bg-red-900/30 transition-colors"><Trash2 className="w-5 h-5" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {plugins.length === 0 && <div className="text-center py-12"><Package className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" /><h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No plugins installed</h3><p className="text-gray-500 dark:text-gray-400 mt-1">Visit the Marketplace to discover plugins</p></div>}
      </div>
    </div>
  )
}