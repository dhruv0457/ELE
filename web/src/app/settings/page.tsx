'use client'

import { useState } from 'react'
import { useStore } from '@/store/useStore'
import { Save, Key, Shield, Mic, Globe, Bell, Trash2, Download, RefreshCw, ToggleLeft, ToggleRight, Eye, EyeOff, Plug } from 'lucide-react'

const TABS = [
  { id: 'general', label: 'General', icon: Globe },
  { id: 'voice', label: 'Voice', icon: Mic },
  { id: 'api-keys', label: 'API Keys', icon: Key },
  { id: 'permissions', label: 'Permissions', icon: Shield },
  { id: 'plugins', label: 'Plugins', icon: Plug },
  { id: 'privacy', label: 'Privacy', icon: Shield },
] as const

export default function SettingsPage() {
  const { settings, updateSettings } = useStore()
  const [activeTab, setActiveTab] = useState<typeof TABS[number]['id']>('general')
  const [saving, setSaving] = useState(false)
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({})

  const handleSave = async () => {
    setSaving(true)
    await new Promise(r => setTimeout(r, 500))
    setSaving(false)
  }

  const toggleApiKey = (provider: string) => {
    setShowKeys(prev => ({ ...prev, [provider]: !prev[provider] }))
  }

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        <div className="flex gap-8">
          <div className="w-48 flex-shrink-0">
            <div className="card p-2">
              {TABS.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  <tab.icon className="w-5 h-5 flex-shrink-0" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1">
            {activeTab === 'general' && <GeneralSettings settings={settings} updateSettings={updateSettings} />}
            {activeTab === 'voice' && <VoiceSettings settings={settings} updateSettings={updateSettings} />}
            {activeTab === 'api-keys' && <ApiKeysSettings settings={settings} updateSettings={updateSettings} showKeys={showKeys} toggleApiKey={toggleApiKey} />}
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
          <select
            value={settings.theme}
            onChange={(e) => updateSettings({ theme: e.target.value as any })}
            className="input"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Language</label>
          <select
            value={settings.language}
            onChange={(e) => updateSettings({ language: e.target.value })}
            className="input"
          >
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
            <input
              type="checkbox"
              checked={settings.auto_update}
              onChange={(e) => updateSettings({ auto_update: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">Auto-update application</span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.start_minimized}
              onChange={(e) => updateSettings({ start_minimized: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">Start minimized to tray</span>
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Telemetry</label>
          <select
            value={settings.telemetry}
            onChange={(e) => updateSettings({ telemetry: e.target.value as any })}
            className="input"
          >
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
          <input
            type="checkbox"
            checked={voice.wake_word_enabled}
            onChange={(e) => updateSettings({ voice: { ...voice, wake_word_enabled: e.target.checked } })}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">Enable wake word ("Hey ELE")</span>
        </label>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Wake Word Sensitivity</label>
          <select
            value={voice.wake_word_sensitivity}
            onChange={(e) => updateSettings({ voice: { ...voice, wake_word_sensitivity: e.target.value as any } })}
            className="input"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Speech-to-Text Engine</label>
          <select
            value={voice.stt_engine}
            onChange={(e) => updateSettings({ voice: { ...voice, stt_engine: e.target.value as any } })}
            className="input"
          >
            <option value="auto">Auto (best available)</option>
            <option value="whisper">Whisper (high quality)</option>
            <option value="vosk">Vosk (offline)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Text-to-Speech Voice</label>
          <select
            value={voice.tts_voice}
            onChange={(e) => updateSettings({ voice: { ...voice, tts_voice: e.target.value as any } })}
            className="input"
          >
            <option value="jarvis">Jarvis (Male)</option>
            <option value="female">Aria (Female)</option>
            <option value="system">System Default</option>
            <option value="cloned">Cloned Voice</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">TTS Engine</label>
          <select
            value={voice.tts_engine}
            onChange={(e) => updateSettings({ voice: { ...voice, tts_engine: e.target.value as any } })}
            className="input"
          >
            <option value="auto">Auto</option>
            <option value="edge">Edge TTS (online)</option>
            <option value="pyttsx3">pyttsx3 (offline)</option>
            <option value="coqui">Coqui (cloning)</option>
          </select>
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Voice Speed: {voice.voice_speed}x</label>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={voice.voice_speed}
              onChange={(e) => updateSettings({ voice: { ...voice, voice_speed: parseFloat(e.target.value) } })}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Volume: {Math.round(voice.volume * 100)}%</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={voice.volume}
              onChange={(e) => updateSettings({ voice: { ...voice, volume: parseFloat(e.target.value) } })}
              className="w-full"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function ApiKeysSettings({ settings, updateSettings, showKeys, toggleApiKey }: any) {
  const providers = [
    { id: 'openai', name: 'OpenAI', prefix: 'sk-' },
    { id: 'gemini', name: 'Google Gemini', prefix: 'AI' },
    { id: 'openclaw', name: 'OpenClaw', prefix: 'oc_' },
    { id: 'anthropic', name: 'Anthropic', prefix: 'sk-ant-' },
    { id: 'nvidia', name: 'NVIDIA NIM', prefix: 'nvapi_' },
  ]

  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">API Keys</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Add your own API keys to use BYOK (Bring Your Own Key) mode. Platform keys are used when available.
      </p>

      <div className="space-y-4">
        {providers.map(provider => (
          <div key={provider.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400">
                <Key className="w-5 h-5" />
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">{provider.name}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {settings.api_keys[provider.id]?.configured ? 'Configured' : 'Not configured'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => toggleApiKey(provider.id)}
                className="btn-secondary text-sm"
              >
                {showKeys[provider.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
              <button className="btn-primary text-sm">Update</button>
            </div>
          </div>
        ))}
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
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Control what ELE Agent can access on your system. Changes require confirmation for risky actions.
      </p>

      <div className="space-y-4">
        {permissions.map(perm => (
          <label key={perm.key} className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <input
              type="checkbox"
              checked={settings.permissions[perm.key]}
              onChange={(e) => updateSettings({ permissions: { ...settings.permissions, [perm.key]: e.target.checked } })}
              className="mt-1 w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
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
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Manage plugin auto-updates and trusted sources
      </p>

      <div className="space-y-4">
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={true}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">Auto-update installed plugins</span>
        </label>
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={false}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">Allow unsigned plugins (not recommended)</span>
        </label>
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={true}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">Verify plugin signatures on install</span>
        </label>
      </div>
    </div>
  )
}

function PrivacySettings({ settings, updateSettings }: any) {
  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Privacy & Data</h2>

      <div className="space-y-4">
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Local Data Storage</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            All your conversations, memories, and settings are stored locally on your device.
            Nothing is sent to our servers unless you explicitly enable cloud sync.
          </p>
          <button className="btn-secondary text-sm">Manage Local Data</button>
        </div>

        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Cloud Sync (Optional)</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Sync your settings and memories across devices using Supabase. End-to-end encrypted.
          </p>
          <button className="btn-primary text-sm">Connect Supabase</button>
        </div>

        <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <h3 className="font-medium text-red-900 dark:text-red-100 mb-2">Delete All Data</h3>
          <p className="text-sm text-red-700 dark:text-red-300 mb-4">
            Permanently delete all conversations, memories, API keys, and settings. This cannot be undone.
          </p>
          <button className="btn text-red-600 border-red-300 hover:bg-red-50 dark:hover:bg-red-900/30 text-sm">Delete Everything</button>
        </div>
      </div>
    </div>
  )
}