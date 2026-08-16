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

if (!isDev) {
  autoUpdater.setFeedURL({
    provider: 'github',
    owner: 'ele-agent',
    repo: 'ele-agent'
  })

  autoUpdater.checkForUpdatesAndNotify()

  autoUpdater.on('update-available', () => {
    mainWindow?.webContents.send('update:available')
  })

  autoUpdater.on('update-downloaded', () => {
    mainWindow?.webContents.send('update:downloaded')
  })
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
    if (!app.isQuitting) {
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
    { label: 'Quit', click: () => { app.isQuitting = true; app.quit() } }
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
  app.isQuitting = true
  if (pythonProcess) {
    pythonProcess.kill()
  }
})

ipcMain.handle('app:quit', () => {
  app.isQuitting = true
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