/**
 * ELE Agent — Complete Developer Chat Window
 * Design: Pure black terminal, colored icons, minimal typography, Apple terminal grid.
 *
 * Features:
 * ✦ Slash command autocomplete popup with arrow-key navigation
 * ✦ Automatic cascade failover (NVIDIA → Gemini → Groq → OpenAI)
 * ✦ Permanent disk-backed API keys (never asks again)
 * ✦ Auto-saves sessions to ~/.ele-agent/sessions/*.json + .md
 * ✦ Directory tree generator (/tree)
 * ✦ JARVIS Live voice + screen vision
 * ✦ Animated scroll, message fadeins, typing indicators
 */
import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import {
  Send,
  Mic,
  MicOff,
  Eye,
  Palette,
  Minimize2,
  Maximize2,
  ArrowDown,
  Radio,
  FolderTree,
  Download,
  Copy,
  Check,
  AlertTriangle,
  Loader2,
  Cpu,
  Zap,
} from 'lucide-react'
import { useStore, AppTheme } from '../store'
import {
  streamChat,
  captureScreen,
  Message,
  getStoredApiKey,
  setStoredApiKey,
  saveSessionToDisk,
  syncKeysFromDisk,
} from '../services/agentService'
import { JarvisLiveVisualizer } from './JarvisLiveVisualizer'
import { SlashCommandMenu, SLASH_COMMANDS, CommandItem } from './SlashCommandMenu'

/* ─── Helper: render markdown-lite inline ─────────────────────────── */
function renderMarkdown(text: string) {
  if (!text) return ''
  // Bold **text**
  let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  // Italic *text*
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')
  // Inline code `text`
  html = html.replace(/`([^`\n]+)`/g, '<code class="inline-code">$1</code>')
  return html
}

/* ─── Message types ───────────────────────────────────────────────── */
export function ChatWindow() {
  const {
    theme,
    setTheme,
    isCompact,
    toggleCompact,
    activeModel,
    activeProvider,
    setActiveModel,
    isJarvisLiveOpen,
    setJarvisLiveOpen,
    toggleJarvisLive,
    createSession,
    currentSessionId,
    sessions,
  } = useStore()

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'ELE Agent online. Developer AI assistant.\n\n' +
        '  /model       switch AI provider\n' +
        '  /tree        scan project directory\n' +
        '  /screen      vision · see your screen\n' +
        '  /voice       JARVIS live voice mode\n' +
        '  /help        all commands\n\n' +
        'Press Enter to send. Shift+Enter for newline. Type / for commands.',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showScrollBottom, setShowScrollBottom] = useState(false)
  const [slashQuery, setSlashQuery] = useState<string | null>(null)
  const [slashIndex, setSlashIndex] = useState(0)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [keysInitialized, setKeysInitialized] = useState(false)
  const [currentModel, setCurrentModel] = useState('')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  /* ── Sync API keys from disk on startup ─────────────────────────── */
  useEffect(() => {
    syncKeysFromDisk().then(() => {
      setKeysInitialized(true)
      setCurrentModel(`${activeProvider.toUpperCase()} · ${activeModel.split('/').pop()}`)
    })
  }, [])

  /* ── Load session from disk ─────────────────────────────────────── */
  useEffect(() => {
    const load = async () => {
      try {
        if (window.ele?.sessions?.load) {
          const saved = await window.ele.sessions.load(currentSessionId)
          if (saved && Array.isArray(saved.messages) && saved.messages.length > 0) {
            setMessages(
              saved.messages.map((m: any) => ({
                ...m,
                timestamp: new Date(m.timestamp || Date.now()),
              }))
            )
          }
        }
      } catch {}
    }
    load()
  }, [currentSessionId])

  /* ── Auto-save session to disk ──────────────────────────────────── */
  useEffect(() => {
    if (messages.length > 1 && !isLoading) {
      const ses = sessions.find((s) => s.id === currentSessionId)
      saveSessionToDisk({
        id: currentSessionId,
        name: ses?.name || 'Session',
        createdAt: ses?.createdAt || Date.now(),
        messages,
      })
    }
  }, [messages, isLoading])

  /* ── Scroll helpers ─────────────────────────────────────────────── */
  const scrollToBottom = useCallback((smooth = true) => {
    messagesEndRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' })
  }, [])

  useEffect(() => {
    if (!showScrollBottom) scrollToBottom()
  }, [messages])

  const handleScroll = () => {
    if (!messagesContainerRef.current) return
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current
    setShowScrollBottom(scrollHeight - scrollTop - clientHeight > 200)
  }

  /* ── Input / Slash command handler ─────────────────────────────── */
  const filteredCommands = useMemo(() => {
    if (!slashQuery) return SLASH_COMMANDS
    const q = slashQuery.replace(/^\//, '').toLowerCase()
    return SLASH_COMMANDS.filter(
      (c) =>
        c.command.replace('/', '').startsWith(q) ||
        c.command.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q)
    )
  }, [slashQuery])

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value
    setInput(val)
    // Auto-resize textarea
    const ta = textareaRef.current
    if (ta) {
      ta.style.height = 'auto'
      ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`
    }
    setSlashQuery(val.startsWith('/') ? val : null)
    setSlashIndex(0)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Slash command navigation
    if (slashQuery !== null && filteredCommands.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSlashIndex((p) => (p + 1) % filteredCommands.length)
        return
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSlashIndex((p) => (p - 1 + filteredCommands.length) % filteredCommands.length)
        return
      }
      if (e.key === 'Tab' || (e.key === 'Enter' && !e.shiftKey && filteredCommands[slashIndex])) {
        e.preventDefault()
        executeSlashCommand(filteredCommands[slashIndex])
        return
      }
      if (e.key === 'Escape') {
        setSlashQuery(null)
        return
      }
    }

    // Send on Enter
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const executeSlashCommand = (cmd: CommandItem) => {
    setSlashQuery(null)
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'

    switch (cmd.command) {
      case '/compact': toggleCompact(); badge('Compact mode toggled.'); return
      case '/clear':   setMessages([]); badge('Messages cleared.'); return
      case '/new':     createSession(); setMessages([]); badge('New session started.'); return
      case '/voice':   toggleJarvisLive(); return
      case '/screen':  handleCaptureScreen(); return
      case '/tree':    handleDirTree(); return
      case '/export':  handleExport(); return
      case '/history': handleHistory(); return
      default:
        setInput(`${cmd.command} `)
        setTimeout(() => textareaRef.current?.focus(), 50)
    }
  }

  /* ─── System badge helper ────────────────────────────────────────── */
  const badge = (text: string) => {
    setMessages((p) => [...p, {
      id: crypto.randomUUID(),
      role: 'system',
      content: text,
      timestamp: new Date(),
    }])
  }

  /* ─── Directory tree ─────────────────────────────────────────────── */
  const handleDirTree = async (path?: string) => {
    badge('Scanning directory structure...')
    try {
      if (window.ele?.system?.generateDirectoryTree) {
        const res = await window.ele.system.generateDirectoryTree(path)
        if (res?.tree) {
          const fmt = (node: any, depth = 0): string => {
            const indent = '  '.repeat(depth)
            const icon = node.type === 'directory' ? '▸' : '·'
            let out = `${indent}${icon} ${node.name}\n`
            if (node.children) {
              for (const c of node.children) out += fmt(c, depth + 1)
            }
            return out
          }
          setMessages((p) => [...p, {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: `Directory tree: ${res.root}\n\n\`\`\`text\n${fmt(res.tree).slice(0, 4000)}\`\`\``,
            timestamp: new Date(),
          }])
          return
        }
      }
    } catch (e: any) {
      badge(`Directory scan failed: ${e?.message}`)
    }
  }

  /* ─── Export session ─────────────────────────────────────────────── */
  const handleExport = async () => {
    const ses = sessions.find((s) => s.id === currentSessionId)
    const data = { id: currentSessionId, name: ses?.name || 'Session', createdAt: ses?.createdAt || Date.now(), messages }
    if (window.ele?.sessions?.save) {
      const res = await window.ele.sessions.save(data)
      if (res.success) {
        badge(`✓ Saved session\n  JSON: ${res.jsonPath}\n  MD:   ${res.mdPath}`)
        return
      }
    }
    // Fallback: download JSON
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `${currentSessionId}.json` })
    a.click()
    badge('Downloaded session JSON to downloads folder.')
  }

  /* ─── History listing ─────────────────────────────────────────────── */
  const handleHistory = async () => {
    if (window.ele?.sessions?.list) {
      const list = await window.ele.sessions.list()
      if (list.length > 0) {
        const lines = list.map((s: any) =>
          `  ${new Date(s.createdAt).toLocaleDateString()} · ${s.name.padEnd(24)} ${s.messageCount} msgs`
        ).join('\n')
        badge(`Session history (~/.ele-agent/sessions):\n\n${lines}`)
        return
      }
    }
    badge(`No saved sessions found. Chat and type /export to save.`)
  }

  /* ─── Screen capture ─────────────────────────────────────────────── */
  const handleCaptureScreen = async (instruction?: string) => {
    setIsLoading(true)
    try {
      const b64 = await captureScreen()
      await handleSend(instruction || 'Analyze my screen and tell me what you observe.', b64)
    } catch (e: any) {
      badge(`Screen capture: ${e?.message || 'Cancelled or denied'}`)
      setIsLoading(false)
    }
  }

  /* ─── Main send / command dispatcher ────────────────────────────── */
  const handleSend = async (customText?: string, screenshot?: string) => {
    const rawText = (customText !== undefined ? customText : input).trim()
    if ((!rawText && !screenshot) || isLoading) return

    setSlashQuery(null)
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'

    /* ── Inline slash command dispatcher ── */
    if (rawText.startsWith('/') && !screenshot) {
      const parts = rawText.split(/\s+/)
      const cmd = parts[0].toLowerCase()
      const arg = parts.slice(1).join(' ').trim()

      switch (cmd) {
        case '/clear':
          setMessages([]); badge('Messages cleared.'); return
        case '/new': case '/session':
          createSession(arg || undefined)
          setMessages([])
          badge(`New session${arg ? ` "${arg}"` : ''} started.`)
          return
        case '/compact':
          toggleCompact(); badge('Compact mode toggled.'); return
        case '/voice':
          toggleJarvisLive(); return
        case '/screen':
          handleCaptureScreen(arg || undefined); return
        case '/tree': case '/dir':
          handleDirTree(arg || undefined); return
        case '/export':
          handleExport(); return
        case '/history':
          handleHistory(); return
        case '/theme': {
          const validThemes: AppTheme[] = ['dark', 'monochrome', 'cyberpunk', 'matrix', 'minimal', 'light']
          if (validThemes.includes(arg as AppTheme)) {
            setTheme(arg as AppTheme)
            badge(`Theme: ${arg.toUpperCase()}`)
          } else {
            badge(`Unknown theme. Valid: ${validThemes.join(', ')}`)
          }
          return
        }
        case '/model': {
          if (!arg || arg === 'list') {
            badge(`Active: ${activeProvider.toUpperCase()} · ${activeModel}\n\nOptions: /model nvidia  /model gemini  /model groq  /model openai  /model auto`)
          } else {
            const m = arg.toLowerCase()
            const modelMap: Record<string, [string, string]> = {
              nvidia: ['meta/llama-3.1-8b-instruct', 'nvidia'],
              'llama-3.3': ['meta/llama-3.3-70b-instruct', 'nvidia'],
              deepseek: ['deepseek-ai/deepseek-r1', 'nvidia'],
              gemini: ['gemini-2.0-flash-exp', 'gemini'],
              groq: ['llama-3.3-70b-versatile', 'groq'],
              openai: ['gpt-4o-mini', 'openai'],
              auto: ['meta/llama-3.1-8b-instruct', 'nvidia'],
            }
            const [model, provider] = modelMap[m] || [arg, 'auto']
            setActiveModel(model, provider)
            setCurrentModel(`${provider.toUpperCase()} · ${model.split('/').pop()}`)
            badge(`Switched to: ${provider.toUpperCase()} · ${model}`)
          }
          return
        }
        case '/scroll':
          if (arg === 'top') {
            messagesContainerRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
          } else {
            scrollToBottom()
          }
          return
        case '/keys': {
          const prov = ['nvidia', 'gemini', 'groq', 'openai', 'anthropic']
          const lines = prov.map((p) => {
            const k = getStoredApiKey(p)
            return `  ${k ? '✓' : '✗'} ${p.padEnd(12)} ${k ? `${k.slice(0, 6)}...${k.slice(-4)}` : 'not configured'}`
          }).join('\n')
          badge(`API keys (~/.ele-agent/.env):\n\n${lines}\n\nUse /key <provider> <key> to save permanently.`)
          return
        }
        case '/key': {
          if (parts.length >= 3) {
            setStoredApiKey(parts[1], parts.slice(2).join(' '))
            badge(`✓ Saved ${parts[1].toUpperCase()}_API_KEY to ~/.ele-agent/.env`)
          } else {
            badge('Usage: /key <provider> <api-key>\n  e.g. /key nvidia nvapi-...')
          }
          return
        }
        case '/status': {
          const nvidia = getStoredApiKey('nvidia') ? 'configured' : 'missing'
          const gemini = getStoredApiKey('gemini') ? 'configured' : 'missing'
          badge(`System Status:\n  Active: ${activeProvider.toUpperCase()} · ${activeModel}\n  NVIDIA: ${nvidia}\n  Gemini: ${gemini}\n  Failover: enabled (auto-cascade)`)
          return
        }
        case '/settings':
          badge('Settings panel — coming soon.\n\nFor now use /key <provider> <key> to configure API access.')
          return
        case '/help':
          badge(
            'ELE Agent — Command Reference:\n\n' +
            '  /model <name>      switch AI provider\n' +
            '  /key <p> <key>     save API key to disk\n' +
            '  /keys              show all API key status\n' +
            '  /theme <name>      dark|monochrome|cyberpunk|matrix|minimal|light\n' +
            '  /compact           toggle compact layout\n' +
            '  /new [name]        new conversation session\n' +
            '  /clear             clear messages\n' +
            '  /export            save session JSON + Markdown to disk\n' +
            '  /history           list saved sessions\n' +
            '  /screen [prompt]   capture screen + AI vision\n' +
            '  /voice             toggle JARVIS live voice\n' +
            '  /tree [path]       show directory structure\n' +
            '  /scroll top|bottom scroll viewport\n' +
            '  /status            show provider status\n' +
            '  /help              this message'
          )
          return
        default:
          // Fall through: treat as regular message to AI
      }
    }

    /* ── User message ── */
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: rawText || 'Analyze my screen.',
      screenshots: screenshot ? [screenshot] : undefined,
      timestamp: new Date(),
    }
    setMessages((p) => [...p, userMsg])
    setIsLoading(true)

    const asstId = crypto.randomUUID()
    setMessages((p) => [...p, { id: asstId, role: 'assistant', content: '', isStreaming: true, timestamp: new Date() }])

    try {
      const history = messages
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content, imageBase64: m.screenshots?.[0] }))
      history.push({ role: 'user', content: rawText, imageBase64: screenshot })

      let full = ''
      for await (const event of streamChat(history, activeProvider, activeModel)) {
        if (event.type === 'delta' && event.content) {
          full += event.content
          setMessages((p) => p.map((m) => m.id === asstId ? { ...m, content: full } : m))
        } else if (event.type === 'model_info' && event.model) {
          setCurrentModel(event.model)
          if (event.model.includes('Failover')) badge(`⚡ ${event.model}`)
        } else if (event.type === 'final') {
          full = event.content || full
          setMessages((p) => p.map((m) => m.id === asstId ? { ...m, content: full, isStreaming: false } : m))
        } else if (event.type === 'error') {
          setMessages((p) => p.map((m) => m.id === asstId ? { ...m, content: event.content || 'Error.', isStreaming: false, error: true } : m))
        }
      }
    } catch (e: any) {
      setMessages((p) => p.map((m) => m.id === asstId ? { ...m, content: `Error: ${e?.message || e}`, isStreaming: false, error: true } : m))
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  /* ─────────────────────────────────────────────────────────────────
     RENDER
  ───────────────────────────────────────────────────────────────── */
  return (
    <div
      className={`flex-1 flex flex-col h-full overflow-hidden theme-${theme} terminal-grid-bg`}
      style={{ background: 'var(--black)', color: 'var(--text-primary)' }}
    >
      {/* JARVIS Live Orb (floating, top-center) */}
      <JarvisLiveVisualizer
        isOpen={isJarvisLiveOpen}
        onClose={() => setJarvisLiveOpen(false)}
        onNewMessage={(role, text, screenshot) => {
          setMessages((p) => [...p, {
            id: crypto.randomUUID(),
            role,
            content: text,
            screenshots: screenshot ? [screenshot] : undefined,
            timestamp: new Date(),
          }])
        }}
      />

      {/* ── Status bar (top) ──────────────────────────────────────── */}
      <div
        className="flex items-center justify-between px-5 py-2 border-b text-xs font-mono select-none flex-shrink-0"
        style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
      >
        {/* Left: model badge */}
        <div className="flex items-center gap-3">
          {/* Status dot */}
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{
              background: keysInitialized && getStoredApiKey(activeProvider) ? 'var(--green)' : 'var(--yellow)',
              boxShadow: `0 0 6px ${keysInitialized && getStoredApiKey(activeProvider) ? 'var(--green)' : 'var(--yellow)'}`,
            }}
          />
          <span style={{ color: 'var(--text-secondary)' }}>
            <span style={{ color: 'var(--cyan)' }}>{activeProvider.toUpperCase()}</span>
            <span style={{ color: 'var(--muted)' }}> · </span>
            <span>{activeModel.split('/').pop()}</span>
          </span>
          <span style={{ color: 'var(--muted)' }}>|</span>
          <span style={{ color: 'var(--green)', fontSize: '10px' }}>auto-failover</span>
        </div>

        {/* Right: action buttons */}
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={toggleJarvisLive}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono transition-all"
            style={{
              background: isJarvisLiveOpen ? 'rgba(247,120,186,0.12)' : 'transparent',
              color: isJarvisLiveOpen ? 'var(--pink)' : 'var(--text-secondary)',
              border: `1px solid ${isJarvisLiveOpen ? 'rgba(247,120,186,0.4)' : 'var(--border)'}`,
            }}
          >
            <Radio className="w-3 h-3" />
            <span>JARVIS</span>
          </button>

          <button
            type="button"
            onClick={() => handleCaptureScreen()}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono transition-all"
            style={{
              background: 'transparent',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border)',
            }}
            title="/screen"
          >
            <Eye className="w-3 h-3" style={{ color: 'var(--cyan)' }} />
            <span>Screen</span>
          </button>

          <button
            type="button"
            onClick={() => handleDirTree()}
            className="p-1.5 rounded-md transition-colors"
            style={{ background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
            title="/tree"
          >
            <FolderTree className="w-3.5 h-3.5" style={{ color: 'var(--green)' }} />
          </button>

          <button
            type="button"
            onClick={() => handleExport()}
            className="p-1.5 rounded-md transition-colors"
            style={{ background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
            title="/export"
          >
            <Download className="w-3.5 h-3.5" style={{ color: 'var(--yellow)' }} />
          </button>

          <button
            type="button"
            onClick={toggleCompact}
            className="p-1.5 rounded-md transition-colors"
            style={{ background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
            title="/compact"
          >
            {isCompact
              ? <Maximize2 className="w-3.5 h-3.5" style={{ color: 'var(--cyan)' }} />
              : <Minimize2 className="w-3.5 h-3.5" style={{ color: 'var(--cyan)' }} />
            }
          </button>

          <button
            type="button"
            onClick={() => {
              const themes: AppTheme[] = ['dark', 'monochrome', 'cyberpunk', 'matrix', 'minimal', 'light']
              setTheme(themes[(themes.indexOf(theme) + 1) % themes.length])
            }}
            className="p-1.5 rounded-md transition-colors"
            style={{ background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
            title="cycle theme"
          >
            <Palette className="w-3.5 h-3.5" style={{ color: 'var(--yellow)' }} />
          </button>
        </div>
      </div>

      {/* ── Messages area ─────────────────────────────────────────── */}
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
        style={{
          padding: isCompact ? '12px 20px' : '24px 28px',
        }}
      >
        <div style={{ maxWidth: 760, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: isCompact ? 12 : 20 }}>
          {messages.map((msg, i) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              isCompact={isCompact}
              copiedId={copiedId}
              onCopy={copyToClipboard}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* ── Jump to bottom ────────────────────────────────────────── */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom()}
          className="btn-jump absolute bottom-24 right-6 z-30 p-2 rounded-full text-white text-xs font-mono"
          style={{ background: 'var(--cyan)', boxShadow: '0 0 12px rgba(88,166,255,0.4)' }}
        >
          <ArrowDown className="w-4 h-4" />
        </button>
      )}

      {/* ── Input area ────────────────────────────────────────────── */}
      <div
        className="border-t flex-shrink-0"
        style={{ background: 'var(--surface)', borderColor: 'var(--border)', padding: '12px 20px 16px' }}
      >
        <div style={{ maxWidth: 760, margin: '0 auto', position: 'relative' }}>
          {/* Slash command popup — anchored above input */}
          {slashQuery !== null && (
            <SlashCommandMenu
              filter={slashQuery}
              selectedIndex={slashIndex}
              onSelect={executeSlashCommand}
            />
          )}

          <form
            onSubmit={(e) => { e.preventDefault(); handleSend() }}
            className="flex gap-2 items-end"
          >
            {/* Terminal prompt input */}
            <div
              className="terminal-input flex-1 flex items-start rounded-lg border overflow-hidden"
              style={{ background: 'var(--panel)', borderColor: 'var(--border)' }}
            >
              {/* Prompt symbol */}
              <span
                className="px-3 pt-3 text-sm font-mono font-bold select-none"
                style={{ color: 'var(--green)' }}
              >
                ❯
              </span>

              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder={
                  isLoading
                    ? 'Generating...'
                    : 'Ask anything or type / for commands  [Enter to send]'
                }
                disabled={isLoading}
                rows={1}
                className="flex-1 bg-transparent py-2.5 pr-3 font-mono text-sm resize-none focus:outline-none"
                style={{
                  color: 'var(--text-primary)',
                  '::placeholder': { color: 'var(--muted)' },
                  minHeight: 44,
                  maxHeight: 160,
                } as any}
              />

              {/* Quick icons inside input */}
              <div className="flex items-center gap-1 px-2 py-2">
                <button
                  type="button"
                  onClick={() => handleCaptureScreen()}
                  disabled={isLoading}
                  className="p-1 rounded transition-colors"
                  style={{ color: 'var(--muted)' }}
                  title="Screen vision"
                >
                  <Eye className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={toggleJarvisLive}
                  className="p-1 rounded transition-colors"
                  style={{ color: isJarvisLiveOpen ? 'var(--pink)' : 'var(--muted)' }}
                  title="JARVIS voice"
                >
                  {isJarvisLiveOpen ? <Mic className="w-3.5 h-3.5" /> : <MicOff className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            {/* Send button */}
            <button
              type="submit"
              disabled={(!input.trim()) || isLoading}
              className="px-4 py-2.5 rounded-lg font-mono text-xs font-semibold flex items-center justify-center flex-shrink-0 transition-all"
              style={{
                background: isLoading || !input.trim() ? 'var(--panel)' : 'var(--cyan)',
                color: isLoading || !input.trim() ? 'var(--muted)' : 'var(--black)',
                border: `1px solid ${isLoading || !input.trim() ? 'var(--border)' : 'transparent'}`,
                minWidth: 48,
                height: 44,
              }}
            >
              {isLoading
                ? <LoadingDots />
                : <Send className="w-4 h-4" />
              }
            </button>
          </form>

          {/* Status line */}
          <div
            className="flex items-center justify-between mt-2 text-[10px] font-mono"
            style={{ color: 'var(--muted)' }}
          >
            <span>/ commands &nbsp;·&nbsp; Enter send &nbsp;·&nbsp; Shift+Enter newline</span>
            <span style={{ color: isLoading ? 'var(--yellow)' : 'var(--muted)' }}>
              {isLoading ? '● streaming' : `${messages.length - 1} messages`}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ─── Loading dots ───────────────────────────────────────────────── */
function LoadingDots() {
  return (
    <span className="flex items-center gap-1">
      <span className="loading-dot" />
      <span className="loading-dot" />
      <span className="loading-dot" />
    </span>
  )
}

/* ─── Message Bubble ─────────────────────────────────────────────── */
function MessageBubble({
  message,
  isCompact,
  copiedId,
  onCopy,
}: {
  message: Message
  isCompact: boolean
  copiedId: string | null
  onCopy: (id: string, text: string) => void
}) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  /* System badge */
  if (isSystem) {
    return (
      <div
        className="animate-msg-in flex justify-center text-center"
      >
        <div
          className="px-4 py-1.5 rounded-full text-[11px] font-mono"
          style={{
            background: 'rgba(88,166,255,0.06)',
            border: '1px solid rgba(88,166,255,0.12)',
            color: 'var(--text-secondary)',
            whiteSpace: 'pre-wrap',
            textAlign: 'left',
            maxWidth: 520,
          }}
        >
          {message.content}
        </div>
      </div>
    )
  }

  /* User message */
  if (isUser) {
    return (
      <div className="animate-msg-in flex justify-end">
        <div
          style={{
            maxWidth: '80%',
            background: 'var(--panel)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: isCompact ? '8px 14px' : '12px 16px',
          }}
        >
          {message.screenshots?.[0] && (
            <img
              src={`data:image/jpeg;base64,${message.screenshots[0]}`}
              alt="screen"
              className="rounded mb-2 max-h-48 object-cover"
              style={{ border: '1px solid var(--border)' }}
            />
          )}
          <div className="flex items-start gap-2">
            <span
              className="font-mono font-bold text-sm select-none flex-shrink-0"
              style={{ color: 'var(--green)' }}
            >
              ❯
            </span>
            <p
              className="font-mono text-sm whitespace-pre-wrap leading-relaxed"
              style={{ color: 'var(--text-primary)' }}
            >
              {message.content}
            </p>
          </div>
          <time
            className="block text-right mt-1 font-mono"
            style={{ color: 'var(--muted)', fontSize: 10 }}
          >
            {new Date(message.timestamp).toLocaleTimeString()}
          </time>
        </div>
      </div>
    )
  }

  /* Assistant message */
  return (
    <div className="animate-msg-in flex gap-3">
      {/* ELE badge */}
      <div
        className="w-7 h-7 rounded flex items-center justify-center flex-shrink-0 mt-0.5 font-mono text-[10px] font-bold"
        style={{
          background: 'var(--panel)',
          border: '1px solid var(--border)',
          color: 'var(--cyan)',
        }}
      >
        ele
      </div>

      <div className="flex-1 min-w-0">
        <div
          style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: isCompact ? '10px 14px' : '14px 18px',
          }}
        >
          {/* Content */}
          {message.content ? (
            <MessageContent content={message.content} />
          ) : message.isStreaming ? (
            <span
              className="font-mono text-sm"
              style={{ color: 'var(--muted)' }}
            >
              <span className="animate-stream-pulse">Thinking</span>
              <span className="cursor-blink" />
            </span>
          ) : null}

          {/* Streaming indicator */}
          {message.isStreaming && message.content && (
            <span className="cursor-blink" />
          )}

          {/* Error indicator */}
          {message.error && (
            <div
              className="mt-2 flex items-start gap-2 text-xs font-mono rounded p-2"
              style={{ background: 'rgba(210,153,34,0.08)', border: '1px solid rgba(210,153,34,0.2)', color: 'var(--yellow)' }}
            >
              <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
              <span>Auto-failover attempted. Check /keys or /status for provider details.</span>
            </div>
          )}

          {/* Footer */}
          {!message.isStreaming && (
            <div
              className="flex items-center justify-between mt-3 pt-2 font-mono"
              style={{ borderTop: '1px solid var(--border)', color: 'var(--muted)' }}
            >
              <span style={{ fontSize: 10 }}>ele · auto-saved</span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => onCopy(message.id, message.content)}
                  className="flex items-center gap-1 p-1 rounded transition-colors text-[10px]"
                  style={{ color: copiedId === message.id ? 'var(--green)' : 'var(--muted)' }}
                >
                  {copiedId === message.id
                    ? <><Check className="w-3 h-3" /><span>Copied</span></>
                    : <Copy className="w-3 h-3" />
                  }
                </button>
                <time style={{ fontSize: 10 }}>{new Date(message.timestamp).toLocaleTimeString()}</time>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─── Message content renderer (code blocks, text) ──────────────── */
function MessageContent({ content }: { content: string }) {
  const parts: React.ReactNode[] = []
  const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = codeBlockRegex.exec(content)) !== null) {
    const before = content.slice(lastIndex, match.index)
    if (before) parts.push(<InlineText key={lastIndex} text={before} />)

    parts.push(
      <div
        key={match.index}
        style={{ position: 'relative', margin: '8px 0' }}
      >
        {match[1] && (
          <div
            className="px-3 py-1 font-mono text-[10px]"
            style={{ background: 'rgba(88,166,255,0.08)', borderBottom: '1px solid var(--border)', color: 'var(--cyan)', borderRadius: '6px 6px 0 0' }}
          >
            {match[1]}
          </div>
        )}
        <pre
          style={{
            margin: 0,
            background: 'rgba(0,0,0,0.4)',
            border: '1px solid var(--border)',
            borderRadius: match[1] ? '0 0 6px 6px' : 6,
            padding: '12px 14px',
            overflowX: 'auto',
            fontSize: 12,
            lineHeight: 1.7,
            color: 'var(--text-primary)',
          }}
        >
          <code>{match[2].trim()}</code>
        </pre>
      </div>
    )

    lastIndex = match.index + match[0].length
  }

  const remainder = content.slice(lastIndex)
  if (remainder) parts.push(<InlineText key={lastIndex} text={remainder} />)

  return <>{parts}</>
}

function InlineText({ text }: { text: string }) {
  return (
    <p
      className="text-sm leading-relaxed whitespace-pre-wrap font-sans"
      style={{ color: 'var(--text-primary)' }}
      dangerouslySetInnerHTML={{ __html: renderMarkdown(text) }}
    />
  )
}