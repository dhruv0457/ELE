/** Overlay Pop-up Component */
import React, { useEffect } from 'react'
import { Bot, Mic, Cpu, Hammer, Volume2, X, AlertCircle } from 'lucide-react'

type OverlayStatus = 'idle' | 'listening' | 'thinking' | 'working' | 'speaking' | 'error'

interface OverlayProps {
  status: OverlayStatus
}

const STATUS_CONFIG: Record<OverlayStatus, { icon: React.ReactNode; label: string; color: string; animate?: boolean }> = {
  idle: { icon: <Bot className="w-6 h-6" />, label: 'Hey ELE', color: 'text-gray-500 dark:text-gray-400' },
  listening: { icon: <Mic className="w-6 h-6 animate-pulse" />, label: 'Listening...', color: 'text-green-500', animate: true },
  thinking: { icon: <Cpu className="w-6 h-6 animate-spin" />, label: 'Thinking...', color: 'text-blue-500', animate: true },
  working: { icon: <Hammer className="w-6 h-6 animate-bounce" />, label: 'Working...', color: 'text-orange-500', animate: true },
  speaking: { icon: <Volume2 className="w-6 h-6 animate-pulse" />, label: 'Speaking...', color: 'text-purple-500', animate: true },
  error: { icon: <AlertCircle className="w-6 h-6" />, label: 'Error', color: 'text-red-500' }
}

export function Overlay({ status }: OverlayProps) {
  const config = STATUS_CONFIG[status]
  const [isPinned, setIsPinned] = React.useState(false)

  useEffect(() => {
    if (status === 'idle' && !isPinned) {
      const timer = setTimeout(() => {
        // Would hide via store
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [status, isPinned])

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] transition-all duration-300" style={{ transform: 'translateX(-50%)' }}>
      <div className="flex items-center gap-3 px-5 py-3 bg-white dark:bg-gray-800 rounded-full shadow-xl border border-gray-100 dark:border-gray-700 animate-slide-down">
        <config.icon className={config.color} />
        <span className="font-medium text-gray-900 dark:text-gray-100">{config.label}</span>
        <button onClick={() => setIsPinned(!isPinned)} className="ml-2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          {isPinned ? <X className="w-4 h-4 text-gray-500" /> : <X className="w-4 h-4 text-gray-400 opacity-50" />}
        </button>
      </div>
      <style jsx>{`
        @keyframes slide-down {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-slide-down { animation: slide-down 0.3s ease-out; }
      `}</style>
    </div>
  )
}