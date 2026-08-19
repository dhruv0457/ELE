/**
 * JARVIS Live Visualizer & Voice Orb Component (Gemini Live & JARVIS Style)
 * Displays a pulsating holographic audio orb with real-time speech recognition,
 * animated speech waveforms, and interactive live voice conversations.
 */
import React, { useEffect, useState, useRef } from 'react'
import { Mic, MicOff, Volume2, VolumeX, Eye, X, Sparkles, Radio } from 'lucide-react'
import { streamChat, captureScreen } from '../services/agentService'

interface JarvisLiveProps {
  isOpen: boolean
  onClose: () => void
  onNewMessage?: (role: 'user' | 'assistant', text: string, screenshot?: string) => void
}

type LiveState = 'idle' | 'listening' | 'thinking' | 'speaking'

export function JarvisLiveVisualizer({ isOpen, onClose, onNewMessage }: JarvisLiveProps) {
  const [state, setState] = useState<LiveState>('idle')
  const [transcript, setTranscript] = useState<string>('')
  const [replyText, setReplyText] = useState<string>('')
  const [isMuted, setIsMuted] = useState<boolean>(false)
  const [isScreenAnalyzing, setIsScreenAnalyzing] = useState<boolean>(false)
  const [audioLevel, setAudioLevel] = useState<number>(20)

  const recognitionRef = useRef<any>(null)
  const synthRef = useRef<SpeechSynthesisUtterance | null>(null)
  const animFrameRef = useRef<number | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)

  // Start microphone and audio analyzer
  useEffect(() => {
    if (!isOpen) {
      stopAll()
      return
    }

    startMicrophone()
    startSpeechRecognition()

    return () => {
      stopAll()
    }
  }, [isOpen])

  // Audio frequency analyzer animation loop
  const startMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = stream

      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)()
      const analyser = audioCtx.createAnalyser()
      analyser.fftSize = 64
      const source = audioCtx.createMediaStreamSource(stream)
      source.connect(analyser)

      audioContextRef.current = audioCtx
      analyserRef.current = analyser

      const dataArray = new Uint8Array(analyser.frequencyBinCount)

      const updateLevel = () => {
        if (!analyserRef.current) return
        analyserRef.current.getByteFrequencyData(dataArray)
        let sum = 0
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i]
        }
        const avg = sum / dataArray.length
        setAudioLevel(Math.max(15, Math.min(100, avg * 1.6)))
        animFrameRef.current = requestAnimationFrame(updateLevel)
      }
      updateLevel()
    } catch (e) {
      console.warn('Microphone stream error:', e)
    }
  }

  const startSpeechRecognition = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      setTranscript('Speech recognition is not supported in this browser.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setState('listening')
    }

    recognition.onresult = (event: any) => {
      let currentText = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const item = event.results[i]
        currentText += item[0].transcript
        if (item.isFinal) {
          handleUserQuery(item[0].transcript)
        }
      }
      setTranscript(currentText)
    }

    recognition.onerror = (event: any) => {
      if (event.error !== 'no-speech') {
        console.warn('Speech recognition error:', event.error)
      }
    }

    recognition.onend = () => {
      // Auto restart if still open and not speaking
      if (isOpen && state !== 'speaking' && state !== 'thinking') {
        try {
          recognition.start()
        } catch {
          // ignore
        }
      }
    }

    try {
      recognition.start()
      recognitionRef.current = recognition
    } catch (err) {
      console.warn('Recognition start failed:', err)
    }
  }

  const stopAll = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch {}
      recognitionRef.current = null
    }
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current)
      animFrameRef.current = null
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop())
      mediaStreamRef.current = null
    }
    if (audioContextRef.current) {
      audioContextRef.current.close().catch(() => {})
      audioContextRef.current = null
    }
    setState('idle')
    setTranscript('')
    setReplyText('')
  }

  const handleUserQuery = async (query: string, screenshotB64?: string) => {
    const cleanQuery = query.trim()
    if (!cleanQuery && !screenshotB64) return

    setState('thinking')
    onNewMessage?.('user', cleanQuery || 'Look at my screen', screenshotB64)

    let prompt = cleanQuery
    if (screenshotB64) {
      prompt = cleanQuery
        ? `User says: "${cleanQuery}". Analyze what is visible on user's screen and answer concisely.`
        : 'Analyze what is currently open on my screen and tell me what you see, any errors, or how you can assist.'
    }

    // Check if user says "see my screen" / "what's on my screen"
    const lower = cleanQuery.toLowerCase()
    if (!screenshotB64 && (lower.includes('see my screen') || lower.includes("what's on my screen") || lower.includes('look at my screen'))) {
      await handleScreenCheck(cleanQuery)
      return
    }

    let fullAnswer = ''
    try {
      const messages: any[] = [{ role: 'user', content: prompt }]
      if (screenshotB64) {
        messages[0].imageBase64 = screenshotB64
      }

      for await (const event of streamChat(messages, 'auto', 'auto')) {
        if (event.type === 'delta' && event.content) {
          fullAnswer += event.content
          setReplyText(fullAnswer)
        } else if (event.type === 'error') {
          fullAnswer = event.content || 'Error getting AI response.'
          setReplyText(fullAnswer)
          break
        }
      }

      onNewMessage?.('assistant', fullAnswer)
      speakResponse(fullAnswer)
    } catch (e: any) {
      const err = `Sorry, I encountered an issue: ${e?.message || e}`
      setReplyText(err)
      speakResponse(err)
    }
  }

  const speakResponse = (text: string) => {
    if (isMuted || !window.speechSynthesis) {
      setState('listening')
      return
    }

    // Clean markdown formatting for speech
    const cleanText = text
      .replace(/```[\s\S]*?```/g, 'Here is the code.')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/[#*_~>]/g, '')
      .trim()

    setState('speaking')
    window.speechSynthesis.cancel()

    const utter = new SpeechSynthesisUtterance(cleanText.slice(0, 400))
    utter.rate = 1.05
    utter.pitch = 1.0

    // Try to pick a clear English voice
    const voices = window.speechSynthesis.getVoices()
    const preferredVoice =
      voices.find((v) => v.name.includes('Google') && v.lang.startsWith('en')) ||
      voices.find((v) => v.name.includes('Natural') || v.name.includes('David') || v.name.includes('Samantha')) ||
      voices[0]

    if (preferredVoice) {
      utter.voice = preferredVoice
    }

    utter.onend = () => {
      setState('listening')
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start()
        } catch {}
      }
    }

    utter.onerror = () => {
      setState('listening')
    }

    synthRef.current = utter
    window.speechSynthesis.speak(utter)
  }

  const handleScreenCheck = async (customPrompt?: string) => {
    setIsScreenAnalyzing(true)
    setState('thinking')
    try {
      const b64 = await captureScreen()
      setIsScreenAnalyzing(false)
      await handleUserQuery(customPrompt || 'Analyze my screen and help me with what I am doing.', b64)
    } catch (e: any) {
      setIsScreenAnalyzing(false)
      const msg = `Could not capture screen: ${e?.message || 'Permission denied'}`
      setReplyText(msg)
      speakResponse(msg)
    }
  }

  if (!isOpen) return null

  // Visualizer Wave Bars Configuration
  const barCount = 18
  const bars = Array.from({ length: barCount }, (_, i) => {
    const factor = Math.sin((i / (barCount - 1)) * Math.PI)
    const baseHeight = state === 'listening' ? audioLevel * factor : state === 'speaking' ? 35 * factor + 15 : 12
    return Math.max(8, Math.min(65, baseHeight))
  })

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-2xl animate-slide-down">
      <div className="relative rounded-3xl p-5 shadow-2xl backdrop-blur-xl border border-cyan-500/30 bg-gray-950/90 text-white overflow-hidden transition-all duration-300">
        {/* Glowing Background Radial Halo */}
        <div
          className={`absolute -inset-10 opacity-30 blur-2xl transition-all duration-700 pointer-events-none ${
            state === 'listening'
              ? 'bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-500'
              : state === 'speaking'
              ? 'bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500'
              : state === 'thinking'
              ? 'bg-gradient-to-r from-indigo-500 via-purple-600 to-cyan-400 animate-pulse'
              : 'bg-gradient-to-r from-blue-600 to-cyan-700'
          }`}
        />

        {/* Top Header Controls */}
        <div className="relative flex items-center justify-between pb-3 border-b border-gray-800/80">
          <div className="flex items-center gap-2.5">
            <span className="relative flex h-3 w-3">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  state === 'listening'
                    ? 'bg-emerald-400'
                    : state === 'speaking'
                    ? 'bg-purple-400'
                    : 'bg-cyan-400'
                }`}
              />
              <span
                className={`relative inline-flex rounded-full h-3 w-3 ${
                  state === 'listening'
                    ? 'bg-emerald-500'
                    : state === 'speaking'
                    ? 'bg-purple-500'
                    : 'bg-cyan-500'
                }`}
              />
            </span>
            <span className="font-semibold tracking-wide text-sm flex items-center gap-1.5 text-cyan-300">
              <Radio className="w-4 h-4 animate-pulse text-cyan-400" />
              JARVIS LIVE REVIEW
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800/80 text-gray-400 border border-gray-700 uppercase font-mono">
              {state}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleScreenCheck()}
              disabled={isScreenAnalyzing}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-xl bg-cyan-950/80 hover:bg-cyan-900/90 text-cyan-300 border border-cyan-500/40 transition-colors shadow-sm"
              title="See my screen and talk about it"
            >
              <Eye className="w-3.5 h-3.5 text-cyan-400" />
              {isScreenAnalyzing ? 'Scanning Screen...' : 'See Screen'}
            </button>

            <button
              onClick={() => setIsMuted(!isMuted)}
              className="p-1.5 rounded-xl bg-gray-800/60 hover:bg-gray-800 text-gray-300 transition-colors"
              title={isMuted ? 'Unmute voice' : 'Mute voice'}
            >
              {isMuted ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-xl bg-gray-800/60 hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
              title="Close JARVIS Live"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Dynamic Center Visualizer Orb & Soundwaves */}
        <div className="relative py-6 flex flex-col items-center justify-center">
          <div className="relative flex items-center justify-center h-24 w-full">
            {/* Center Animated Hologram Orb */}
            <div
              className={`absolute w-16 h-16 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 ${
                state === 'listening'
                  ? 'bg-gradient-to-tr from-emerald-500/80 to-cyan-500/80 shadow-emerald-500/50 scale-110'
                  : state === 'speaking'
                  ? 'bg-gradient-to-tr from-purple-500/80 to-cyan-500/80 shadow-purple-500/50 scale-125 animate-pulse'
                  : state === 'thinking'
                  ? 'bg-gradient-to-tr from-indigo-600/80 to-pink-500/80 shadow-pink-500/50 animate-spin'
                  : 'bg-gradient-to-tr from-cyan-600/60 to-blue-600/60 shadow-cyan-500/30'
              }`}
            >
              <Sparkles className="w-7 h-7 text-white animate-bounce" />
            </div>

            {/* Pulsing Audio Frequency Bars (Left and Right) */}
            <div className="w-full flex items-center justify-center gap-1.5 px-6 z-10 pointer-events-none">
              {bars.map((h, i) => (
                <div
                  key={i}
                  style={{ height: `${h}px` }}
                  className={`w-1.5 rounded-full transition-all duration-75 ${
                    state === 'speaking'
                      ? 'bg-gradient-to-t from-cyan-400 to-purple-500'
                      : state === 'listening'
                      ? 'bg-gradient-to-t from-emerald-400 to-cyan-400'
                      : 'bg-gray-700/60'
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Real-time Subtitles / Live Transcript */}
          <div className="w-full mt-3 text-center px-4 min-h-[48px] flex flex-col justify-center">
            {transcript ? (
              <p className="text-sm font-medium text-cyan-200 animate-fade-in line-clamp-2">
                <span className="text-gray-400 font-normal">You: </span>
                "{transcript}"
              </p>
            ) : replyText ? (
              <p className="text-sm font-medium text-emerald-300 animate-fade-in line-clamp-2">
                <span className="text-gray-400 font-normal">JARVIS: </span>
                {replyText}
              </p>
            ) : (
              <p className="text-xs text-gray-500 tracking-wide font-mono">
                {state === 'listening' ? '🎙 Listening to your voice... Speak anytime or say "See my screen"' : 'Ready for instruction'}
              </p>
            )}
          </div>
        </div>

        {/* Bottom Status & Quick Action Hint */}
        <div className="relative pt-2 border-t border-gray-800/60 flex items-center justify-between text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Mic className="w-3.5 h-3.5 text-emerald-400" />
            Gemini Live Audio Engine Active
          </span>
          <span className="font-mono text-[11px] text-gray-400">
            Commands: <code className="text-cyan-400">/screen</code> · <code className="text-cyan-400">/voice</code> · <code className="text-cyan-400">/model</code>
          </span>
        </div>
      </div>
    </div>
  )
}
