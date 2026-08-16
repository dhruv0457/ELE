import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  thoughts?: string[]
  toolsUsed?: string[]
  screenshots?: string[]
  timestamp: Date
  isStreaming?: boolean
}

interface Settings {
  theme: 'light' | 'dark' | 'system'
  language: string
  auto_update: boolean
  start_minimized: boolean
  telemetry: 'full' | 'errors' | 'none'
  voice: {
    wake_word_enabled: boolean
    wake_word_sensitivity: 'low' | 'medium' | 'high'
    stt_engine: 'auto' | 'whisper' | 'vosk'
    tts_voice: 'jarvis' | 'female' | 'system' | 'cloned'
    tts_engine: 'auto' | 'edge' | 'pyttsx3' | 'coqui'
    voice_speed: number
    volume: number
  }
  api_keys: Record<string, { key: string; configured: boolean }>
  permissions: Record<string, boolean>
}

interface AppState {
  currentView: 'chat' | 'dashboard' | 'plugins' | 'marketplace' | 'settings'
  setCurrentView: (view: AppState['currentView']) => void

  isSidebarCollapsed: boolean
  toggleSidebar: () => void

  isOverlayVisible: boolean
  setOverlayVisible: (visible: boolean) => void
  overlayStatus: 'idle' | 'listening' | 'thinking' | 'working' | 'speaking' | 'error'
  setOverlayStatus: (status: AppState['overlayStatus']) => void

  isVoiceEnabled: boolean
  toggleVoice: () => void

  messages: Message[]
  addMessage: (message: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  clearMessages: () => void

  settings: Settings
  updateSettings: (settings: Partial<Settings>) => void

  installedPlugins: string[]
  addPlugin: (id: string) => void
  removePlugin: (id: string) => void

  user: { id: string; email: string; tier: string } | null
  setUser: (user: AppState['user']) => void
}

const defaultSettings: Settings = {
  theme: 'system',
  language: 'en',
  auto_update: true,
  start_minimized: false,
  telemetry: 'errors',
  voice: {
    wake_word_enabled: true,
    wake_word_sensitivity: 'medium',
    stt_engine: 'auto',
    tts_voice: 'jarvis',
    tts_engine: 'auto',
    voice_speed: 1.0,
    volume: 1.0,
  },
  api_keys: {},
  permissions: {
    file_system: true,
    app_launch: true,
    browser: true,
    shell: true,
    microphone: true,
    notifications: true,
  },
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      currentView: 'chat',
      setCurrentView: (view) => set({ currentView: view }),

      isSidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),

      isOverlayVisible: false,
      setOverlayVisible: (visible) => set({ isOverlayVisible: visible }),
      overlayStatus: 'idle',
      setOverlayStatus: (status) => set({ overlayStatus: status }),

      isVoiceEnabled: true,
      toggleVoice: () => set((state) => ({ isVoiceEnabled: !state.isVoiceEnabled })),

      messages: [],
      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
      updateMessage: (id, updates) =>
        set((state) => ({
          messages: state.messages.map((m) => (m.id === id ? { ...m, ...updates } : m)),
        })),
      clearMessages: () => set({ messages: [] }),

      settings: defaultSettings,
      updateSettings: (newSettings) =>
        set((state) => ({ settings: { ...state.settings, ...newSettings } })),

      installedPlugins: [],
      addPlugin: (id) => set((state) => ({ installedPlugins: [...state.installedPlugins, id] })),
      removePlugin: (id) =>
        set((state) => ({ installedPlugins: state.installedPlugins.filter((p) => p !== id) })),

      user: null,
      setUser: (user) => set({ user }),
    }),
    {
      name: 'ele-web-store',
      partialize: (state) => ({
        settings: state.settings,
        installedPlugins: state.installedPlugins,
        isSidebarCollapsed: state.isSidebarCollapsed,
      }),
    }
  )
)