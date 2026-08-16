/** Chat Window Component */
import React, { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Mic, MicOff, Bot, Loader2, Terminal, CheckCircle, AlertCircle, Copy, ChevronDown, ChevronUp } from 'lucide-react'
import { useStore } from '../store'

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

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showThoughts, setShowThoughts] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { isVoiceEnabled, setVoiceEnabled } = useStore()

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await window.ele.agent.chat(input, { tools: ['file', 'browser', 'shell'] })
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        thoughts: response.thoughts,
        toolsUsed: response.tools_used,
        screenshots: response.screenshots,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Failed to get response. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
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
    error: { icon: AlertCircle, label: 'Error', color: 'text-red-500' }
  }

  return (
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
              <button type="button" onClick={() => setVoiceEnabled(!isVoiceEnabled)} disabled={isLoading} className={`p-2 rounded-lg transition-colors ${isVoiceEnabled ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'}`}>
                {isVoiceEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
              </button>
            </div>
          </div>
          <button type="submit" disabled={!input.trim() || isLoading} className="btn-primary p-3 rounded-xl disabled:opacity-50" aria-label="Send message">
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
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
          <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">{message.content}</div>

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
                <span key={i} className="px-2 py-1 text-xs bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 rounded-full">{tool}</span>
              ))}
            </div>
          )}

          {(message.screenshots && message.screenshots.length > 0) && (
            <div className="mt-4 grid grid-cols-2 gap-2">
              {message.screenshots.map((screenshot: string, i: number) => (
                <img key={i} src={`data:image/png;base64,${screenshot}`} alt={`Screenshot ${i + 1}`} className="rounded-lg border border-gray-200 dark:border-gray-700 max-h-40 object-cover" />
              ))}
            </div>
          )}

          <div className="flex items-center justify-end gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
            <button onClick={() => copyToClipboard(message.content)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors" aria-label="Copy response">
              <Copy className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </button>
            <time className="text-xs text-gray-500 dark:text-gray-400">{message.timestamp.toLocaleTimeString()}</time>
          </div>
        </div>
      </div>
    </div>
  )
}