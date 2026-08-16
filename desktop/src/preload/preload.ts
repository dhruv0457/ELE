/** Preload Script - Secure IPC Bridge */
import { contextBridge, ipcRenderer } from 'electron'

interface AgentAPI {
  chat: (message: string, options?: any) => Promise<any>
  chatStream: (message: string, options?: any) => Promise<any>
}

interface VoiceAPI {
  transcribe: (audioData: ArrayBuffer) => Promise<{ text: string; engine: string }>
  synthesize: (text: string, voice?: string) => Promise<ArrayBuffer>
}

interface SettingsAPI {
  get: () => Promise<any>
  update: (settings: any) => Promise<any>
}

interface PluginsAPI {
  list: () => Promise<any[]>
  install: (source: string) => Promise<any>
}

interface SystemAPI {
  openExternal: (url: string) => Promise<void>
  showSaveDialog: (options: any) => Promise<any>
  showOpenDialog: (options: any) => Promise<any>
}

interface UpdaterAPI {
  check: () => Promise<any>
  install: () => Promise<void>
}

interface WindowAPI {
  minimize: () => void
  maximize: () => void
  close: () => void
  isMaximized: () => boolean
}

declare global {
  interface Window {
    ele: {
      agent: AgentAPI
      voice: VoiceAPI
      settings: SettingsAPI
      plugins: PluginsAPI
      system: SystemAPI
      updater: UpdaterAPI
      window: WindowAPI
      on: (channel: string, listener: (...args: any[]) => void) => void
      off: (channel: string, listener: (...args: any[]) => void) => void
    }
  }
}

contextBridge.exposeInMainWorld('ele', {
  agent: {
    chat: (message: string, options?: any) =>
      ipcRenderer.invoke('agent:chat', message, options),
    chatStream: (message: string, options?: any) =>
      ipcRenderer.invoke('agent:chat-stream', message, options)
  },
  voice: {
    transcribe: (audioData: ArrayBuffer) =>
      ipcRenderer.invoke('voice:transcribe', audioData),
    synthesize: (text: string, voice?: string) =>
      ipcRenderer.invoke('voice:synthesize', text, voice)
  },
  settings: {
    get: () => ipcRenderer.invoke('settings:get'),
    update: (settings: any) => ipcRenderer.invoke('settings:update', settings)
  },
  plugins: {
    list: () => ipcRenderer.invoke('plugins:list'),
    install: (source: string) => ipcRenderer.invoke('plugins:install', source)
  },
  system: {
    openExternal: (url: string) => ipcRenderer.invoke('shell:openExternal', url),
    showSaveDialog: (options: any) => ipcRenderer.invoke('dialog:showSaveDialog', options),
    showOpenDialog: (options: any) => ipcRenderer.invoke('dialog:showOpenDialog', options)
  },
  updater: {
    check: () => ipcRenderer.invoke('updater:check'),
    install: () => ipcRenderer.invoke('updater:install')
  },
  window: {
    minimize: () => ipcRenderer.invoke('app:minimize'),
    maximize: () => ipcRenderer.invoke('app:maximize'),
    close: () => ipcRenderer.invoke('app:quit'),
    isMaximized: () => ipcRenderer.invoke('app:isMaximized')
  },
  on: (channel: string, listener: (...args: any[]) => void) => {
    const validChannels = ['overlay:show', 'overlay:hide', 'update:available', 'update:downloaded']
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (_, ...args) => listener(...args))
    }
  },
  off: (channel: string, listener: (...args: any[]) => void) => {
    const validChannels = ['overlay:show', 'overlay:hide', 'update:available', 'update:downloaded']
    if (validChannels.includes(channel)) {
      ipcRenderer.removeListener(channel, listener)
    }
  }
})