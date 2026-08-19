/** Electron Main Process */
import { app, BrowserWindow, ipcMain, Tray, Menu, nativeImage, shell, dialog, autoUpdater } from 'electron'
import { join } from 'path'
import { spawn, ChildProcess } from 'child_process'
import { writeFileSync, existsSync, mkdirSync } from 'fs'
import { homedir } from 'os'

const isDev = process.env.NODE_ENV === 'development'
const isMac = process.platform === 'darwin'
const isWin = process.platform === 'win32'

let mainWindow: BrowserWindow | null = null
let tray: Tray | null = null
let pythonProcess: ChildProcess | null = null
let pythonPort = 8000
let isQuitting = false

if (!isDev) {
  try {
    const { autoUpdater: updater } = require('electron-updater')
    updater?.checkForUpdatesAndNotify?.()
    updater?.on?.('update-available', () => {
      mainWindow?.webContents.send('update:available')
    })
    updater?.on?.('update-downloaded', () => {
      mainWindow?.webContents.send('update:downloaded')
    })
  } catch {
    // electron-updater optional
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    show: false,
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#1a1a2e',
      symbolColor: '#fff',
      height: 36
    },
    webPreferences: {
      preload: join(__dirname, '../preload/preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: !isDev
    },
    icon: join(__dirname, '../../build/icon.png')
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
    if (isDev) mainWindow?.webContents.openDevTools()
  })

  mainWindow.on('close', (e) => {
    if (!isQuitting) {
      e.preventDefault()
      mainWindow?.hide()
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function createTray() {
  const icon = nativeImage.createFromPath(join(__dirname, '../../build/tray-icon.png'))
  tray = new Tray(icon.resize({ width: 16, height: 16 }))

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show ELE Agent', click: () => mainWindow?.show() },
    { label: 'Voice Mode', click: () => mainWindow?.webContents.send('voice:toggle') },
    { type: 'separator' },
    { label: 'Quit', click: () => { isQuitting = true; app.quit() } }
  ])

  tray.setToolTip('ELE Agent')
  tray.setContextMenu(contextMenu)

  tray.on('double-click', () => {
    mainWindow?.show()
  })
}

async function startPythonBackend() {
  const pythonPath = isDev
    ? 'python'
    : join(process.resourcesPath, 'python', 'python.exe')

  const backendPath = isDev
    ? join(__dirname, '../../../backend/app/main.py')
    : join(process.resourcesPath, 'backend', 'app', 'main.py')

  pythonProcess = spawn(pythonPath, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(pythonPort)], {
    cwd: isDev ? join(__dirname, '../../../backend') : join(process.resourcesPath, 'backend'),
    env: { ...process.env, PYTHONPATH: isDev ? join(__dirname, '../../../backend') : join(process.resourcesPath, 'backend') }
  })

  pythonProcess.stdout?.on('data', (data) => {
    console.log(`Python: ${data}`)
  })

  pythonProcess.stderr?.on('data', (data) => {
    console.error(`Python Error: ${data}`)
  })

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`)
  })

  await new Promise<void>((resolve) => {
    const check = setInterval(async () => {
      try {
        const res = await fetch(`http://127.0.0.1:${pythonPort}/health`)
        if (res.ok) {
          clearInterval(check)
          resolve()
        }
      } catch {
      }
    }, 500)
  })
}

app.whenReady().then(async () => {
  await startPythonBackend()
  createWindow()
  createTray()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (!isMac) {
    app.quit()
  }
})

app.on('before-quit', () => {
  isQuitting = true
  if (pythonProcess) {
    pythonProcess.kill()
  }
})

ipcMain.handle('app:quit', () => {
  isQuitting = true
  app.quit()
})

ipcMain.handle('app:minimize', () => {
  mainWindow?.minimize()
})

ipcMain.handle('app:maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow?.unmaximize()
  } else {
    mainWindow?.maximize()
  }
})

ipcMain.handle('app:isMaximized', () => {
  return mainWindow?.isMaximized() ?? false
})

ipcMain.handle('shell:openExternal', async (_, url: string) => {
  await shell.openExternal(url)
})

ipcMain.handle('dialog:showSaveDialog', async (_, options: any) => {
  const result = await dialog.showSaveDialog(mainWindow!, options)
  return result
})

ipcMain.handle('dialog:showOpenDialog', async (_, options: any) => {
  const result = await dialog.showOpenDialog(mainWindow!, options)
  return result
})

ipcMain.handle('updater:check', async () => {
  return autoUpdater.checkForUpdates()
})

ipcMain.handle('updater:install', async () => {
  autoUpdater.quitAndInstall()
})

ipcMain.handle('screen:capture', async () => {
  try {
    const { desktopCapturer } = require('electron')
    const sources = await desktopCapturer.getSources({
      types: ['screen'],
      thumbnailSize: { width: 1920, height: 1080 }
    })
    if (sources && sources.length > 0) {
      return sources[0].thumbnail.toJPEG(80).toString('base64')
    }
  } catch (err) {
    console.error('desktopCapturer error:', err)
  }
  return null
})

// ── Persistent API Keys Bridge (Stored in ~/.ele-agent/.env) ────────────────
function getEleAgentDir(): string {
  const dir = join(homedir(), '.ele-agent')
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true })
  }
  return dir
}

function loadAllDiskKeys(): Record<string, string> {
  const keys: Record<string, string> = {}
  const envFiles = [
    join(getEleAgentDir(), '.env'),
    join(__dirname, '../../../.env'),
    join(process.cwd(), '.env'),
  ]

  for (const f of envFiles) {
    if (existsSync(f)) {
      try {
        const { readFileSync } = require('fs')
        const content = readFileSync(f, 'utf-8')
        for (const line of content.split('\n')) {
          const trimmed = line.trim()
          if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
            const [k, ...rest] = trimmed.split('=')
            const v = rest.join('=').trim().replace(/^["']|["']$/g, '')
            if (k.trim() && v) {
              keys[k.trim()] = v
            }
          }
        }
      } catch (err) {
        console.error(`Error reading ${f}:`, err)
      }
    }
  }

  // Also check process.env
  for (const k of ['NVIDIA_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY', 'ANTHROPIC_API_KEY', 'GROQ_API_KEY']) {
    if (process.env[k]) {
      keys[k] = process.env[k]!
    }
  }

  return keys
}

function saveKeyToDisk(keyName: string, keyValue: string): void {
  const envPath = join(getEleAgentDir(), '.env')
  let existingLines: string[] = []
  if (existsSync(envPath)) {
    try {
      const { readFileSync } = require('fs')
      existingLines = readFileSync(envPath, 'utf-8').split('\n')
    } catch {}
  }

  let found = false
  const updatedLines = existingLines.map((line) => {
    const trimmed = line.trim()
    if (trimmed.startsWith(`${keyName}=`)) {
      found = true
      return `${keyName}=${keyValue}`
    }
    return line
  })

  if (!found) {
    updatedLines.push(`${keyName}=${keyValue}`)
  }

  try {
    writeFileSync(envPath, updatedLines.join('\n').trim() + '\n', 'utf-8')
  } catch (err) {
    console.error('Failed to write to .env:', err)
  }
}

ipcMain.handle('keys:getAll', async () => {
  return loadAllDiskKeys()
})

ipcMain.handle('keys:set', async (_, { provider, key }: { provider: string; key: string }) => {
  const envKey = `${provider.toUpperCase()}_API_KEY`
  saveKeyToDisk(envKey, key)
  process.env[envKey] = key
  return { success: true, key: envKey }
})

// ── Persistent Sessions History in JSON & Markdown ───────────────────────────
function getSessionsDir(): string {
  const dir = join(getEleAgentDir(), 'sessions')
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true })
  }
  return dir
}

ipcMain.handle('sessions:save', async (_, sessionData: any) => {
  try {
    const sessionsDir = getSessionsDir()
    const id = sessionData.id || `ses_${Date.now()}`
    const jsonPath = join(sessionsDir, `${id}.json`)
    const mdPath = join(sessionsDir, `${id}.md`)

    // Save JSON
    writeFileSync(jsonPath, JSON.stringify(sessionData, null, 2), 'utf-8')

    // Generate readable Markdown
    let md = `# Session: ${sessionData.name || 'Conversation'}\n`
    md += `**Date:** ${new Date(sessionData.createdAt || Date.now()).toLocaleString()}\n`
    md += `**ID:** \`${id}\`\n\n---\n\n`

    if (Array.isArray(sessionData.messages)) {
      for (const msg of sessionData.messages) {
        const role = msg.role === 'user' ? '👤 **User**' : msg.role === 'system' ? '⚙ **System**' : '🤖 **ELE (Assistant)**'
        md += `### ${role}\n*${new Date(msg.timestamp || Date.now()).toLocaleTimeString()}*\n\n${msg.content}\n\n`
      }
    }

    writeFileSync(mdPath, md, 'utf-8')
    return { success: true, jsonPath, mdPath }
  } catch (err: any) {
    console.error('Session save error:', err)
    return { success: false, error: err.message }
  }
})

ipcMain.handle('sessions:list', async () => {
  try {
    const sessionsDir = getSessionsDir()
    const { readdirSync, readFileSync } = require('fs')
    const files = readdirSync(sessionsDir).filter((f: string) => f.endsWith('.json'))
    const list: any[] = []

    for (const f of files) {
      try {
        const raw = readFileSync(join(sessionsDir, f), 'utf-8')
        const data = JSON.parse(raw)
        list.push({
          id: data.id || f.replace('.json', ''),
          name: data.name || 'Session',
          createdAt: data.createdAt || Date.now(),
          messageCount: data.messages?.length || 0,
          preview: data.messages?.[data.messages.length - 1]?.content?.slice(0, 80) || '',
        })
      } catch {}
    }
    return list.sort((a, b) => b.createdAt - a.createdAt)
  } catch (err: any) {
    return []
  }
})

ipcMain.handle('sessions:load', async (_, id: string) => {
  try {
    const sessionsDir = getSessionsDir()
    const jsonPath = join(sessionsDir, `${id}.json`)
    if (existsSync(jsonPath)) {
      const { readFileSync } = require('fs')
      return JSON.parse(readFileSync(jsonPath, 'utf-8'))
    }
    return null
  } catch (err: any) {
    console.error('Session load error:', err)
    return null
  }
})

// ── Directory Tree Scanner ───────────────────────────────────────────────────
function scanDirectory(dir: string, depth = 0, maxDepth = 3): any {
  if (depth > maxDepth) return null
  const { readdirSync, statSync } = require('fs')
  const base = require('path').basename(dir)
  const ignored = new Set(['node_modules', '.git', '.venv', '__pycache__', '.next', 'dist', 'out', 'build', '.ele-agent'])

  if (ignored.has(base)) return null

  try {
    const stat = statSync(dir)
    if (!stat.isDirectory()) {
      return { name: base, type: 'file', size: stat.size }
    }

    const children: any[] = []
    const files = readdirSync(dir)
    for (const file of files) {
      if (ignored.has(file)) continue
      const fullPath = join(dir, file)
      try {
        const item = scanDirectory(fullPath, depth + 1, maxDepth)
        if (item) children.push(item)
      } catch {}
    }

    return { name: base, type: 'directory', children }
  } catch {
    return null
  }
}

ipcMain.handle('system:generateDirectoryTree', async (_, targetPath?: string) => {
  const root = targetPath || process.cwd()
  const tree = scanDirectory(root, 0, 3)
  return { root, tree }
})