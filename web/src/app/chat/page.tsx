'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { useStore } from '@/store/useStore'
import { Send, Mic, MicOff, Bot, Loader2, Terminal, CheckCircle, AlertCircle, Copy, ChevronDown, ChevronUp, ChevronLeft, ChevronRight } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function ChatPage() {
  const {
    currentView,
    setCurrentView,
    isSidebarCollapsed,
    toggleSidebar,
    isOverlayVisible,
    overlayStatus,
    isVoiceEnabled,
    toggleVoice,
    messages,
    addMessage,
    updateMessage,
    clearMessages,
    settings,
  } = useStore()

  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showThoughts, setShowThoughts] = useState(true)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const thoughtsEndRef = useRef<HTMLDivElement>(null)
  const currentAssistantId = useRef<string | null>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const wsUrl = apiUrl.replace('http', 'ws') + '/api/v1/ws/chat'

    const websocket = new WebSocket(wsUrl)
    setWs(websocket)

    websocket.onopen = () => {
      console.log('WebSocket connected')
    }

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleWSMessage(data)
      } catch (e) {
        console.error('WS parse error', e)
      }
    }

    websocket.onerror = (error) => {
      console.error('WebSocket error', error)
    }

    return () => {
      websocket.close()
    }
  }, [])

  const handleWSMessage = (data: any) => {
    switch (data.type) {
      case 'thought':
        if (currentAssistantId.current) {
          updateMessage(currentAssistantId.current, {
            thoughts: [...(messages.find(m => m.id === currentAssistantId.current)?.thoughts || []), data.content]
          })
        }
        break
      case 'tool_start':
        if (currentAssistantId.current) {
          updateMessage(currentAssistantId.current, {
            toolsUsed: [...(messages.find(m => m.id === currentAssistantId.current)?.toolsUsed || []), data.tool]
          })
        }
        break
      case 'tool_result':
        break
      case 'screenshot':
        if (currentAssistantId.current) {
          updateMessage(currentAssistantId.current, {
            screenshots: [...(messages.find(m => m.id === currentAssistantId.current)?.screenshots || []), data.data]
          })
        }
        break
      case 'progress':
        break
      case 'final':
        if (currentAssistantId.current) {
          updateMessage(currentAssistantId.current, {
            content: data.content,
            isStreaming: false,
            thoughts: data.metadata?.thoughts,
            screenshots: data.metadata?.screenshots,
            toolsUsed: data.metadata?.tools_used,
          })
        }
        setIsLoading(false)
        currentAssistantId.current = null
        break
      case 'error':
        if (currentAssistantId.current) {
          updateMessage(currentAssistantId.current, {
            content: 'Error: ' + data.message,
            isStreaming: false,
          })
        }
        setIsLoading(false)
        currentAssistantId.current = null
        break
    }
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = {
      id: crypto.randomUUID(),
      role: 'user' as const,
      content: input,
      timestamp: new Date(),
    }

    addMessage(userMessage)
    setInput('')
    setIsLoading(true)

    const assistantId = crypto.randomUUID()
    currentAssistantId.current = assistantId

    const assistantMessage = {
      id: assistantId,
      role: 'assistant' as const,
      content: '',
      thoughts: [],
      toolsUsed: [],
      screenshots: [],
      timestamp: new Date(),
      isStreaming: true,
    }
    addMessage(assistantMessage)

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'message',
        content: input,
        tools: ['file', 'browser', 'shell'],
        model: 'auto',
      }))
    } else {
      setIsLoading(false)
      updateMessage(assistantId, {
        content: 'Connection lost. Please refresh.',
        isStreaming: false,
      })
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const STATUS_CONFIG = {
    idle: { icon: Bot, label: 'Ready', color: 'text-gray-500 dark:text-gray-400' },
    listening: { icon: Mic, label: 'Listening...', color: 'text-green-500 animate-pulse' },
    thinking: { icon: Loader2, label: 'Thinking...', color: 'text-blue-500 animate-spin' },
    working: { icon: Terminal, label: 'Working...', color: 'text-orange-500 animate-bounce' },
    speaking: { icon: Bot, label: 'Speaking...', color: 'text-purple-500 animate-pulse' },
    error: { icon: AlertCircle, label: 'Error', color: 'text-red-500' },
  }

  const statusConfig = STATUS_CONFIG[overlayStatus as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.idle
  const StatusIcon = statusConfig.icon

  return (
    <div className="flex h-screen w-full bg-gray-50 dark:bg-gray-900 overflow-hidden">
      <aside className={`fixed inset-y-0 left-0 z-40 transition-all duration-300 bg-white dark:bg-gray-800 border-r border-gray-100 dark:border-gray-700 ${isSidebarCollapsed ? 'w-16' : 'w-64'}`}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <Bot className="text-primary-600 dark:text-primary-400" size={28} />
            {!isSidebarCollapsed && <span className="text-xl font-bold text-gray-900 dark:text-gray-100">ELE Agent</span>}
          </div>
          <button onClick={toggleSidebar} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            {isSidebarCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {[
            { id: 'chat', label: 'Chat', icon: Bot },
            { id: 'dashboard', label: 'Dashboard', icon: Terminal },
            { id: 'plugins', label: 'Plugins', icon: Bot },
            { id: 'marketplace', label: 'Marketplace', icon: Bot },
            { id: 'settings', label: 'Settings', icon: Bot },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id as any)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                currentView === item.id
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!isSidebarCollapsed && <span>{item.label}</span>}
            </button>
          ))}
        </nav>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden ml-0 lg:ml-64">
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                showThoughts={showThoughts}
                onToggleThoughts={() => setShowThoughts(!showThoughts)}
                copyToClipboard={copyToClipboard}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-gray-100 dark:border-gray-800 p-4">
            <form onSubmit={handleSend} className="flex gap-3">
              <div className="flex-1 relative">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={isLoading ? 'Processing...' : 'Type a message or use voice...'}
                  disabled={isLoading}
                  className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none min-h-[52px] max-h-48"
                  rows={1}
                />
                <div className="absolute right-3 bottom-3 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={toggleVoice}
                    disabled={isLoading}
                    className={`p-2 rounded-lg transition-colors ${isVoiceEnabled ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'}`}
                  >
                    {isVoiceEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="btn-primary p-3 rounded-xl disabled:opacity-50"
                aria-label="Send message"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span>Shift+Enter for new line • Enter to send</span>
              <span className="flex items-center gap-2">
                <StatusIcon className={`w-4 h-4 ${statusConfig.color}`} />
                {statusConfig.label}
              </span>
            </div>
          </div>
        </div>

        {isOverlayVisible && (
          <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50">
            <div className="flex items-center gap-3 px-5 py-3 bg-white dark:bg-gray-800 rounded-full shadow-xl border border-gray-100 dark:border-gray-700 animate-slide-up">
              <StatusIcon className={`w-6 h-6 ${statusConfig.color}`} />
              <span className="font-medium text-gray-900 dark:text-gray-100">{statusConfig.label}</span>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

function MessageBubble({ message, showThoughts, onToggleThoughts, copyToClipboard }: any) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl bg-primary-600 px-4 py-3 text-white shadow-sm">
          <p className="whitespace-pre-wrap">{message.content}</p>
          <time className="block text-right text-xs opacity-70 mt-1">{message.timestamp.toLocaleTimeString()}</time>
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-3">
      <Bot className="w-8 h-8 text-primary-600 dark:text-primary-400 mt-1 flex-shrink-0" />
      <div className="flex-1 max-w-[85%]">
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 p-4 shadow-sm">
          <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
            {message.content}
          </div>

          {message.isStreaming && (
            <div className="flex items-center gap-2 mt-3 text-sm text-gray-500 dark:text-gray-400">
              <Loader2 className="w-4 h-4 animate-spin text-primary-500" />
              <span>Generating response...</span>
            </div>
          )}

          {(message.thoughts && message.thoughts.length > 0) && (
            <details className="mt-4" open={showThoughts}>
              <summary className="flex items-center gap-2 text-sm font-medium text-gray-500 dark:text-gray-400 cursor-pointer">
                <ChevronDown className="w-4 h-4" />
                <span>Thought Process ({message.thoughts.length})</span>
              </summary>
              <div className="mt-2 space-y-1 pl-6 border-l-2 border-gray-200 dark:border-gray-700">
                {message.thoughts.map((thought: string, i: number) => (
                  <div key={i} className="text-sm text-gray-600 dark:text-gray-300 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                    {thought}
                  </div>
                ))}
              </div>
            </details>
          )}

          {(message.toolsUsed && message.toolsUsed.length > 0) && (
            <div className="mt-4 flex flex-wrap gap-2">
              {message.toolsUsed.map((tool: string, i: number) => (
                <span key={i} className="px-2 py-1 text-xs bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 rounded-full">
                  {tool}
                </span>
              ))}
            </div>
          )}

          {(message.screenshots && message.screenshots.length > 0) && (
            <div className="mt-4 grid grid-cols-2 gap-2">
              {message.screenshots.map((screenshot: string, i: number) => (
                <img
                  key={i}
                  src={`data:image/png;base64,${screenshot}`}
                  alt={`Screenshot ${i + 1}`}
                  className="rounded-lg border border-gray-200 dark:border-gray-700 max-h-40 object-cover"
                />
              ))}
            </div>
          )}

          <div className="flex items-center justify-end gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
            <button
              onClick={() => copyToClipboard(message.content)}
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Copy response"
            >
              <Copy className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </button>
            <time className="text-xs text-gray-500 dark:text-gray-400">{message.timestamp.toLocaleTimeString()}</time>
          </div>
        </div>
      </div>
    </div>
  )
}