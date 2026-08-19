/**
 * ELE Agent — Slash Command Autocomplete Popup
 *
 * Shows as a glass panel above the input when user types "/".
 * Full keyboard navigation (↑↓ arrows, Enter/Tab to confirm, Esc to close).
 * Renders category labels, icons, syntax, and description for every command.
 */
import React from 'react'
import {
  Cpu,
  Palette,
  Minimize2,
  PlusCircle,
  Trash2,
  Mic,
  Eye,
  ArrowDownCircle,
  Key,
  Activity,
  HelpCircle,
  FolderTree,
  Download,
  History,
  Terminal,
  Zap,
  Settings,
} from 'lucide-react'

export interface CommandItem {
  command: string
  syntax: string
  description: string
  category: 'AI & Model' | 'Session' | 'View' | 'Vision & Voice' | 'System'
  icon: any
  accentColor: string
}

export const SLASH_COMMANDS: CommandItem[] = [
  // ── AI & Model ──────────────────────────────────────────────────
  {
    command: '/model',
    syntax: '/model <nvidia|gemini|groq|openai|deepseek|auto>',
    description: 'Switch active AI provider or enable auto-cascade mode',
    category: 'AI & Model',
    icon: Cpu,
    accentColor: '#58a6ff',
  },
  {
    command: '/key',
    syntax: '/key <provider> <api-key>',
    description: 'Permanently save an API key to ~/.ele-agent/.env',
    category: 'AI & Model',
    icon: Key,
    accentColor: '#58a6ff',
  },
  {
    command: '/keys',
    syntax: '/keys',
    description: 'Show status of all loaded API keys and providers',
    category: 'AI & Model',
    icon: Activity,
    accentColor: '#58a6ff',
  },
  {
    command: '/status',
    syntax: '/status',
    description: 'Check provider latency and streaming health',
    category: 'AI & Model',
    icon: Zap,
    accentColor: '#d29922',
  },

  // ── Session ──────────────────────────────────────────────────────
  {
    command: '/new',
    syntax: '/new [session-name]',
    description: 'Start a new blank conversation session',
    category: 'Session',
    icon: PlusCircle,
    accentColor: '#3fb950',
  },
  {
    command: '/clear',
    syntax: '/clear',
    description: 'Clear all messages in the current session',
    category: 'Session',
    icon: Trash2,
    accentColor: '#3fb950',
  },
  {
    command: '/export',
    syntax: '/export',
    description: 'Save session to JSON & Markdown at ~/.ele-agent/sessions/',
    category: 'Session',
    icon: Download,
    accentColor: '#3fb950',
  },
  {
    command: '/history',
    syntax: '/history',
    description: 'List all past sessions saved on disk',
    category: 'Session',
    icon: History,
    accentColor: '#3fb950',
  },

  // ── View ─────────────────────────────────────────────────────────
  {
    command: '/theme',
    syntax: '/theme <dark|monochrome|cyberpunk|matrix|minimal|light>',
    description: 'Switch visual theme instantly',
    category: 'View',
    icon: Palette,
    accentColor: '#d29922',
  },
  {
    command: '/compact',
    syntax: '/compact',
    description: 'Toggle dense developer compact layout mode',
    category: 'View',
    icon: Minimize2,
    accentColor: '#d29922',
  },
  {
    command: '/scroll',
    syntax: '/scroll <top|bottom>',
    description: 'Animate scroll to top or bottom of conversation',
    category: 'View',
    icon: ArrowDownCircle,
    accentColor: '#d29922',
  },

  // ── Vision & Voice ───────────────────────────────────────────────
  {
    command: '/voice',
    syntax: '/voice',
    description: 'Toggle JARVIS Live animated voice speaking orb',
    category: 'Vision & Voice',
    icon: Mic,
    accentColor: '#f778ba',
  },
  {
    command: '/screen',
    syntax: '/screen [instruction]',
    description: 'Capture & inspect active display with vision AI',
    category: 'Vision & Voice',
    icon: Eye,
    accentColor: '#f778ba',
  },

  // ── System ───────────────────────────────────────────────────────
  {
    command: '/tree',
    syntax: '/tree [path]',
    description: 'Scan and display project directory structure as tree',
    category: 'System',
    icon: FolderTree,
    accentColor: '#8b949e',
  },
  {
    command: '/help',
    syntax: '/help',
    description: 'Show all available commands and keyboard shortcuts',
    category: 'System',
    icon: HelpCircle,
    accentColor: '#8b949e',
  },
  {
    command: '/settings',
    syntax: '/settings',
    description: 'Open the ELE Agent settings panel',
    category: 'System',
    icon: Settings,
    accentColor: '#8b949e',
  },
]

const CATEGORY_ORDER: CommandItem['category'][] = [
  'AI & Model',
  'Session',
  'View',
  'Vision & Voice',
  'System',
]

interface SlashCommandMenuProps {
  filter: string
  selectedIndex: number
  onSelect: (cmd: CommandItem) => void
}

export function SlashCommandMenu({ filter, selectedIndex, onSelect }: SlashCommandMenuProps) {
  const query = filter.replace(/^\//, '').toLowerCase()

  const filtered = SLASH_COMMANDS.filter(
    (c) =>
      c.command.replace('/', '').startsWith(query) ||
      c.command.toLowerCase().includes(query) ||
      c.description.toLowerCase().includes(query) ||
      c.syntax.toLowerCase().includes(query)
  )

  if (filtered.length === 0) return null

  // Group by category in defined order
  const grouped: Record<string, CommandItem[]> = {}
  for (const c of CATEGORY_ORDER) grouped[c] = []
  for (const cmd of filtered) {
    grouped[cmd.category]?.push(cmd)
  }

  let globalIndex = 0

  return (
    <div className="absolute bottom-full left-0 mb-1.5 w-full max-w-2xl animate-slide-up z-50">
      {/* Glass panel */}
      <div
        className="rounded-xl overflow-hidden border"
        style={{
          background: 'rgba(13, 17, 23, 0.97)',
          borderColor: 'rgba(88, 166, 255, 0.25)',
          boxShadow: '0 -4px 40px rgba(88, 166, 255, 0.08), 0 0 0 1px rgba(33, 38, 45, 0.5)',
          backdropFilter: 'blur(20px)',
        }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-4 py-2 border-b"
          style={{ borderColor: 'rgba(33, 38, 45, 0.8)' }}
        >
          <div className="flex items-center gap-2">
            <Terminal className="w-3 h-3" style={{ color: '#58a6ff' }} />
            <span className="text-[10px] font-mono font-semibold tracking-widest uppercase" style={{ color: '#58a6ff' }}>
              Command Palette
            </span>
          </div>
          <div className="text-[10px] font-mono" style={{ color: '#484f58' }}>
            <span style={{ color: '#8b949e' }}>↑↓</span> navigate &nbsp;
            <span style={{ color: '#8b949e' }}>⏎</span> select &nbsp;
            <span style={{ color: '#8b949e' }}>Esc</span> close
          </div>
        </div>

        <div className="max-h-72 overflow-y-auto py-1.5">
          {CATEGORY_ORDER.map((cat) => {
            const items = grouped[cat]
            if (!items || items.length === 0) return null
            return (
              <div key={cat}>
                {/* Category label */}
                <div
                  className="px-4 py-1 text-[9px] uppercase tracking-widest font-mono font-semibold"
                  style={{ color: '#484f58' }}
                >
                  {cat}
                </div>

                {items.map((item) => {
                  const myIndex = globalIndex++
                  const Icon = item.icon
                  const isSelected = myIndex === selectedIndex

                  return (
                    <button
                      key={item.command}
                      type="button"
                      className="w-full text-left flex items-center gap-3 px-4 py-2 transition-colors"
                      style={{
                        background: isSelected ? 'rgba(88, 166, 255, 0.08)' : 'transparent',
                        borderLeft: isSelected ? `2px solid ${item.accentColor}` : '2px solid transparent',
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) {
                          const el = e.currentTarget
                          el.style.background = 'rgba(255,255,255,0.03)'
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) {
                          const el = e.currentTarget
                          el.style.background = 'transparent'
                        }
                      }}
                      onClick={() => onSelect(item)}
                    >
                      {/* Colored icon */}
                      <div
                        className="w-6 h-6 rounded flex items-center justify-center flex-shrink-0"
                        style={{ background: `${item.accentColor}16` }}
                      >
                        <Icon className="w-3.5 h-3.5" style={{ color: item.accentColor }} />
                      </div>

                      {/* Command + description */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-baseline gap-2">
                          <span
                            className="font-mono font-semibold text-xs"
                            style={{ color: item.accentColor }}
                          >
                            {item.command}
                          </span>
                          <span
                            className="font-mono text-[10px] truncate"
                            style={{ color: '#484f58' }}
                          >
                            {item.syntax.replace(item.command, '').trim()}
                          </span>
                        </div>
                        <div
                          className="text-[11px] truncate"
                          style={{ color: '#8b949e' }}
                        >
                          {item.description}
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            )
          })}
        </div>

        {/* Footer prompt */}
        <div
          className="px-4 py-1.5 border-t text-[10px] font-mono flex items-center gap-2"
          style={{ borderColor: 'rgba(33, 38, 45, 0.8)', color: '#484f58' }}
        >
          <span>Type to filter</span>
          <span style={{ color: 'rgba(88,166,255,0.4)' }}>|</span>
          <span style={{ color: '#3fb950' }}>{filtered.length}</span> commands available
        </div>
      </div>
    </div>
  )
}
