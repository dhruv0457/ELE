/** Settings Panel Component */
import React, { useState } from 'react'
import { Save, Key, Shield, Mic, Globe, Bell, Trash2, Download, RefreshCw, ToggleLeft, ToggleRight, Plug } from 'lucide-react'
import { useStore } from '../store'

const TABS = [
  { id: 'general', label: 'General', icon: Globe },
  { id: 'voice', label: 'Voice', icon: Mic },
  { id: 'api-keys', label: 'API Keys', icon: Key },
  { id: 'permissions', label: 'Permissions', icon: Shield },
  { id: 'plugins', label: 'Plugins', icon: Plug },
  { id: 'privacy', label: 'Privacy', icon: Shield },
] as const

export function SettingsPanel() {
  const { settings, updateSettings } = useStore()
  const [activeTab, setActiveTab] = useState<TABS[number]['id']>('general')
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    await new Promise(r => setTimeout(r, 500))
    updateSettings(settings)
    setSaving(false)
  }

  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
          <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-2">
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        <div className="flex gap-6">
          <div className="w-48 flex-shrink-0">
            <div className="card p-2">
              {TABS.map(tab => (
                <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === tab.id ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'}`}>
                  <tab.icon className="w-5 h-5 flex-shrink-0" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1">
            {activeTab === 'general' && <GeneralSettings settings={settings} updateSettings={updateSettings} />}
            {activeTab === 'voice' && <VoiceSettings settings={settings} updateSettings={updateSettings} />}
            {activeTab === 'api-keys' && <ApiKeysSettings settings={settings} updateSettings={updateSettings} />}
            {activeTab === 'permissions' && <PermissionsSettings settings={settings} updateSettings={updateSettings} />}
            {activeTab === 'plugins' && <PluginsSettings settings={settings} updateSettings={updateSettings} />}
            {activeTab === 'privacy' && <PrivacySettings settings={settings} updateSettings={updateSettings} />}
          </div>
        </div>
      </div>
    </div>
  )
}

function GeneralSettings({ settings, updateSettings }: any) {
  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">General</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Theme</label>
          <select value={settings.theme} onChange={(e) => updateSettings({ theme: e.target.value as any })} className="input">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Language</label>
          <select value={settings.language} onChange={(e) => updateSettings({ language: e.target.value })} className="input">
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="ja">Japanese</option>
            <option value="zh">Chinese</option>
          </select>
        </div>
        <div className="grid sm:grid-cols-2 gap-4">
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={settings.auto_update} onChange={(e) => updateSettings({ auto_update: e.target.checked })} className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Auto-update application</span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={settings.start_minimized} onChange={(e) => updateSettings({ start_minimized: e.target.checked })} className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Start minimized to tray</span>
          </label>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Telemetry</label>
          <select value={settings.telemetry} onChange={(e) => updateSettings({ telemetry: e.target.value as any })} className="input">
            <option value="full">Full (help improve ELE)</option>
            <option value="errors">Errors only</option>
            <option value="none">None</option>
          </select>
        </div>
      </div>
    </div>
  )
}

function VoiceSettings({ settings, updateSettings }: any) {
  const voice = settings.voice
  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Voice</h2>
      <div className="space-y-4">
        <label className="flex items-center gap-3">
          <input type="checkbox" checked={voice.wake_word_enabled} onChange={(e) => updateSettings({ voice: { ...voice, wake_word_enabled: e.target.checked } })} className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
          <span className="text-sm text-gray-700 dark:text-gray-300">Enable wake word ("Hey ELE")</span>
        </label>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Wake Word Sensitivity</label>
          <select value={voice.wake_word_sensitivity} onChange={(e) => updateSettings({ voice: { ...voice, wake_word_sensitivity: e.target.value as any } })} className="input">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Speech-to-Text Engine</label>
          <select value={voice.stt_engine} onChange={(e) => updateSettings({ voice: { ...voice, stt_engine: e.target.value as any } })} className="input">
            <option value="auto">Auto (best available)</option>
            <option value="whisper">Whisper (high quality)</option>
            <option value="vosk">Vosk (offline)</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Text-to-Speech Voice</label>
          <select value={voice.tts_voice} onChange={(e) => updateSettings({ voice: { ...voice, tts_voice: e.target.value as any } })} className="input">
            <option value="jarvis">Jarvis (Male)</option>
            <option value="female">Aria (Female)</option>
            <option value="system">System Default</option>
            <option value="cloned">Cloned Voice</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">TTS Engine</label>
          <select value={voice.tts_engine} onChange={(e) => updateSettings({ voice: { ...voice, tts_engine: e.target.value as any } })} className="input">
            <option value="auto">Auto</option>
            <option value="edge">Edge TTS (online)</option>
            <option value="pyttsx3">pyttsx3 (offline)</option>
            <option value="coqui">Coqui (cloning)</option>
          </select>
        </div>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Voice Speed: {voice.voice_speed}x</label>
            <input type="range" min="0.5" max="2" step="0.1" value={voice.voice_speed} onChange={(e) => updateSettings({ voice: { ...voice, voice_speed: parseFloat(e.target.value) } })} className="w-full" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Volume: {Math.round(voice.volume * 100)}%</label>
            <input type="range" min="0" max="1" step="0.1" value={voice.volume} onChange={(e) => updateSettings({ voice: { ...voice, volume: parseFloat(e.target.value) } })} className="w-full" />
          </div>
        </div>
      </div>
    </div>
  )
}

function ApiKeysSettings({ settings, updateSettings }: any) {
  const [keyInputs, setKeyInputs] = React.useState<Record<string, string>>({})
  const [saved, setSaved] = React.useState<Record<string, boolean>>({})
  const [showKey, setShowKey] = React.useState<Record<string, boolean>>({})

  const providers = [
    { id: 'nvidia',    name: 'NVIDIA NIM',       hint: 'build.nvidia.com → Get API Key (Free)' },
    { id: 'groq',     name: 'Groq (Ultra Fast)', hint: 'console.groq.com/keys (Free)' },
    { id: 'gemini',   name: 'Google Gemini',     hint: 'aistudio.google.com (Free tier)' },
    { id: 'openai',   name: 'OpenAI',            hint: 'platform.openai.com' },
    { id: 'anthropic',name: 'Anthropic Claude',  hint: 'console.anthropic.com' },
  ]

  const getStoredKey = (id: string) => {
    return localStorage.getItem(`ele_key_${id}`) || ''
  }

  const handleSave = async (id: string) => {
    const key = keyInputs[id]?.trim()
    if (!key) return
    localStorage.setItem(`ele_key_${id}`, key)
    if ((window as any).ele?.keys?.set) {
      await (window as any).ele.keys.set(id, key)
    }
    setSaved(s => ({ ...s, [id]: true }))
    setKeyInputs(s => ({ ...s, [id]: '' }))
    setTimeout(() => setSaved(s => ({ ...s, [id]: false })), 2000)
  }

  const handleClear = (id: string) => {
    localStorage.removeItem(`ele_key_${id}`)
    if ((window as any).ele?.keys?.set) {
      (window as any).ele.keys.set(id, '')
    }
    setSaved(s => ({ ...s, [id]: false }))
  }

  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">API Keys</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Add your own API keys (BYOK mode). Keys are saved locally on your device only.
      </p>
      <div className="space-y-4">
        {providers.map(provider => {
          const existing = getStoredKey(provider.id)
          const configured = Boolean(existing)
          return (
            <div key={provider.id} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${configured ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' : 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400'}`}>
                    <Key className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{provider.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{provider.hint}</p>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${configured ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400'}`}>
                  {configured ? '✓ Configured' : 'Not set'}
                </span>
              </div>
              {configured && (
                <div className="flex items-center gap-2 text-xs text-gray-400 font-mono bg-gray-100 dark:bg-gray-900 px-3 py-1.5 rounded">
                  <span>{showKey[provider.id] ? existing : `${existing.slice(0, 8)}${'•'.repeat(12)}${existing.slice(-4)}`}</span>
                  <button onClick={() => setShowKey(s => ({ ...s, [provider.id]: !s[provider.id] }))} className="ml-auto text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                    {showKey[provider.id] ? '🙈' : '👁'}
                  </button>
                  <button onClick={() => handleClear(provider.id)} className="text-red-500 hover:text-red-700">✕</button>
                </div>
              )}
              <div className="flex gap-2">
                <input
                  type="password"
                  placeholder={configured ? 'Enter new key to replace...' : `Paste ${provider.id} API key...`}
                  value={keyInputs[provider.id] || ''}
                  onChange={e => setKeyInputs(s => ({ ...s, [provider.id]: e.target.value }))}
                  onKeyDown={e => e.key === 'Enter' && handleSave(provider.id)}
                  className="input flex-1 text-sm font-mono"
                />
                <button
                  onClick={() => handleSave(provider.id)}
                  disabled={!keyInputs[provider.id]?.trim()}
                  className="btn-primary text-sm px-4"
                >
                  {saved[provider.id] ? '✓ Saved' : 'Save'}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-1">🚀 NVIDIA NIM — All Models</h3>
        <p className="text-xs text-blue-700 dark:text-blue-300 mb-2">After setting your NVIDIA key, use <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">/model</code> to switch models in chat:</p>
        <div className="grid grid-cols-2 gap-1 text-xs font-mono text-blue-800 dark:text-blue-200">
          {[
            'meta/llama-3.1-8b-instruct',
            'meta/llama-3.1-70b-instruct',
            'meta/llama-3.3-70b-instruct',
            'meta/llama-3.2-11b-vision-instruct',
            'deepseek-ai/deepseek-r1',
            'deepseek-ai/deepseek-r1-distill-llama-70b',
            'mistralai/mistral-7b-instruct-v0.3',
            'mistralai/mixtral-8x22b-instruct-v0.1',
            'nvidia/nemotron-4-340b-instruct',
            'qwen/qwen2.5-72b-instruct',
            'microsoft/phi-3-mini-128k-instruct',
            'google/gemma-2-27b-it',
          ].map(m => (
            <code key={m} className="bg-blue-100 dark:bg-blue-900/50 px-1.5 py-0.5 rounded text-xs truncate">{m.split('/')[1]}</code>
          ))}
        </div>
        <p className="text-xs text-blue-600 dark:text-blue-400 mt-2">Use: <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">/model deepseek-ai/deepseek-r1</code> for full model IDs</p>
      </div>
    </div>
  )
}

function PermissionsSettings({ settings, updateSettings }: any) {
  const permissions = [
    { key: 'file_system', label: 'File System Access', desc: 'Read, write, and manage files' },
    { key: 'app_launch', label: 'App Launch', desc: 'Launch and control applications' },
    { key: 'browser', label: 'Browser Automation', desc: 'Control web browser (Playwright)' },
    { key: 'shell', label: 'Shell Commands', desc: 'Execute terminal commands' },
    { key: 'microphone', label: 'Microphone', desc: 'Access microphone for voice input' },
    { key: 'notifications', label: 'Notifications', desc: 'Show system notifications' },
  ]
  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Permissions</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400">Control what ELE Agent can access on your system.</p>
      <div className="space-y-4">
        {permissions.map(perm => (
          <label key={perm.key} className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <input type="checkbox" checked={settings.permissions[perm.key]} onChange={(e) => updateSettings({ permissions: { ...settings.permissions, [perm.key]: e.target.checked } })} className="mt-1 w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
            <div>
              <p className="font-medium text-gray-900 dark:text-gray-100">{perm.label}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{perm.desc}</p>
            </div>
          </label>
        ))}
      </div>
    </div>
  )
}

function PluginsSettings({ settings, updateSettings }: any) {
  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Plugins</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Manage plugin auto-updates and trusted sources</p>
      <div className="space-y-4">
        <label className="flex items-center gap-3"><input type="checkbox" checked={true} className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" /><span className="text-sm text-gray-700 dark:text-gray-300">Auto-update installed plugins</span></label>
        <label className="flex items-center gap-3"><input type="checkbox" checked={false} className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" /><span className="text-sm text-gray-700 dark:text-gray-300">Allow unsigned plugins (not recommended)</span></label>
        <label className="flex items-center gap-3"><input type="checkbox" checked={true} className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" /><span className="text-sm text-gray-700 dark:text-gray-300">Verify plugin signatures on install</span></label>
      </div>
    </div>
  )
}

function PrivacySettings({ settings, updateSettings }: any) {
  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Privacy &amp; Data</h2>
      <div className="space-y-4">
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Local Data Storage</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">All your conversations, memories, and settings are stored locally on your device.</p>
          <button className="btn-secondary text-sm">Manage Local Data</button>
        </div>
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Cloud Sync (Optional)</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Sync your settings and memories across devices using Supabase. End-to-end encrypted.</p>
          <button className="btn-primary text-sm">Connect Supabase</button>
        </div>
        <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <h3 className="font-medium text-red-900 dark:text-red-100 mb-2">Delete All Data</h3>
          <p className="text-sm text-red-700 dark:text-red-300 mb-4">Permanently delete all conversations, memories, API keys, and settings. This cannot be undone.</p>
          <button className="btn text-red-600 border-red-300 hover:bg-red-50 dark:hover:bg-red-900/30 text-sm">Delete Everything</button>
        </div>
      </div>
    </div>
  )
}