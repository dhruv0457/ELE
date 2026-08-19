/** Zustand Store for Desktop App */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type AppTheme = 'dark' | 'monochrome' | 'cyberpunk' | 'matrix' | 'minimal' | 'light'

interface SessionInfo {
  id: string
  name: string
  createdAt: number
}

interface Settings {
  theme: AppTheme
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

  theme: AppTheme
  setTheme: (theme: AppTheme) => void

  isCompact: boolean
  toggleCompact: () => void

  activeModel: string
  activeProvider: string
  setActiveModel: (model: string, provider?: string) => void

  isJarvisLiveOpen: boolean
  setJarvisLiveOpen: (open: boolean) => void
  toggleJarvisLive: () => void

  sessions: SessionInfo[]
  currentSessionId: string
  createSession: (name?: string) => string
  switchSession: (id: string) => void

  isSidebarCollapsed: boolean
  toggleSidebar: () => void

  isOverlayVisible: boolean
  setOverlayVisible: (visible: boolean) => void
  overlayStatus: 'idle' | 'listening' | 'thinking' | 'working' | 'speaking' | 'error'
  setOverlayStatus: (status: AppState['overlayStatus']) => void

  isVoiceEnabled: boolean
  toggleVoice: () => void

  settings: Settings
  updateSettings: (settings: Partial<Settings>) => void

  installedPlugins: string[]
  addPlugin: (id: string) => void
  removePlugin: (id: string) => void
}

const defaultSettings: Settings = {
  theme: 'dark',
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
  api_keys: {
    NVIDIA_API_KEY: { key: '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', configured: true },
  },
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
    (set, get) => ({
      currentView: 'chat',
      setCurrentView: (view) => set({ currentView: view }),

      theme: 'dark',
      setTheme: (theme) => set({ theme }),

      isCompact: false,
      toggleCompact: () => set((state) => ({ isCompact: !state.isCompact })),

      activeModel: 'meta/llama-3.1-8b-instruct',
      activeProvider: 'nvidia',
      setActiveModel: (model, provider) =>
        set((state) => ({
          activeModel: model,
          activeProvider: provider || state.activeProvider,
        })),

      isJarvisLiveOpen: false,
      setJarvisLiveOpen: (open) => set({ isJarvisLiveOpen: open }),
      toggleJarvisLive: () => set((state) => ({ isJarvisLiveOpen: !state.isJarvisLiveOpen })),

      sessions: [{ id: 'default', name: 'Main Session', createdAt: Date.now() }],
      currentSessionId: 'default',
      createSession: (name) => {
        const id = `ses_${Date.now().toString(36)}`
        const newSession = { id, name: name || `Session ${get().sessions.length + 1}`, createdAt: Date.now() }
        set((state) => ({
          sessions: [newSession, ...state.sessions],
          currentSessionId: id,
        }))
        return id
      },
      switchSession: (id) => set({ currentSessionId: id }),

      isSidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),

      isOverlayVisible: false,
      setOverlayVisible: (visible) => set({ isOverlayVisible: visible }),
      overlayStatus: 'idle',
      setOverlayStatus: (status) => set({ overlayStatus: status }),

      isVoiceEnabled: true,
      toggleVoice: () => set((state) => ({ isVoiceEnabled: !state.isVoiceEnabled })),

      settings: defaultSettings,
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
          theme: (newSettings.theme as AppTheme) || state.theme,
        })),

      installedPlugins: ['python-assistant'],
      addPlugin: (id) => set((state) => ({ installedPlugins: [...state.installedPlugins, id] })),
      removePlugin: (id) => set((state) => ({ installedPlugins: state.installedPlugins.filter((p) => p !== id) })),
    }),
    {
      name: 'ele-desktop-store',
      partialize: (state) => ({
        settings: state.settings,
        theme: state.theme,
        isCompact: state.isCompact,
        activeModel: state.activeModel,
        activeProvider: state.activeProvider,
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
        installedPlugins: state.installedPlugins,
        isSidebarCollapsed: state.isSidebarCollapsed,
      }),
    }
  )
)