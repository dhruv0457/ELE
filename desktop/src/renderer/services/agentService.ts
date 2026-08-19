/**
 * ELE Agent — Unified Agent & Multimodal LLM Service
 * - Automatic Cascade Failover: Seamlessly switches to the next available model if one errors or hits rate limits.
 * - Permanent File-backed API Keys: Reads & writes directly to disk (~/.ele-agent/.env) via Electron bridge.
 * - Multimodal Vision: Captures screen and performs deep vision inference.
 * - Session Disk Persistence: Saves history in JSON & Markdown.
 */

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  thoughts?: string[]
  toolsUsed?: string[]
  screenshots?: string[]
  timestamp: Date
  isStreaming?: boolean
  error?: boolean
}

export interface StreamEvent {
  type: 'delta' | 'thought' | 'tool_start' | 'tool_end' | 'final' | 'error' | 'model_info'
  content?: string
  tool?: string
  model?: string
}

// In-memory cache for API keys
let diskKeysCache: Record<string, string> = {
  NVIDIA_API_KEY: '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',
}

// Initialize and sync keys from disk on startup
export async function syncKeysFromDisk(): Promise<Record<string, string>> {
  try {
    if (window.ele?.keys?.getAll) {
      const diskKeys = await window.ele.keys.getAll()
      if (diskKeys && typeof diskKeys === 'object') {
        diskKeysCache = { ...diskKeysCache, ...diskKeys }
        for (const [k, v] of Object.entries(diskKeys)) {
          if (v) {
            localStorage.setItem(`ele_key_${k.replace('_API_KEY', '').toLowerCase()}`, v)
          }
        }
      }
    }
  } catch (e) {
    console.warn('Failed to load keys from disk:', e)
  }
  return diskKeysCache
}

// Trigger initial sync
syncKeysFromDisk().catch(() => {})

export function getStoredApiKey(provider: string): string {
  const pUpper = `${provider.toUpperCase()}_API_KEY`
  if (diskKeysCache[pUpper] && diskKeysCache[pUpper].trim()) {
    return diskKeysCache[pUpper].trim()
  }

  try {
    const local = localStorage.getItem(`ele_key_${provider.toLowerCase()}`)
    if (local && local.trim()) return local.trim()

    const rawStore = localStorage.getItem('ele-desktop-store')
    if (rawStore) {
      const parsed = JSON.parse(rawStore)
      const keyObj = parsed?.state?.settings?.api_keys?.[pUpper]
      if (keyObj?.key) return keyObj.key
    }
  } catch {}

  if (provider.toLowerCase() === 'nvidia') {
    return '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'
  }
  return ''
}

export function setStoredApiKey(provider: string, key: string): void {
  const trimmed = key.trim()
  const pUpper = `${provider.toUpperCase()}_API_KEY`
  diskKeysCache[pUpper] = trimmed
  localStorage.setItem(`ele_key_${provider.toLowerCase()}`, trimmed)

  // Persist directly to disk file ~/.ele-agent/.env
  if (window.ele?.keys?.set) {
    window.ele.keys.set(provider, trimmed).catch((e) => console.error('Disk key save error:', e))
  }
}

export function getAvailableProviders(): { id: string; name: string; hasKey: boolean; defaultModel: string }[] {
  return [
    {
      id: 'nvidia',
      name: 'NVIDIA NIM (Fast Llama 3.1/3.3)',
      hasKey: Boolean(getStoredApiKey('nvidia')),
      defaultModel: 'meta/llama-3.1-8b-instruct',
    },
    {
      id: 'gemini',
      name: 'Google Gemini 2.0 Flash',
      hasKey: Boolean(getStoredApiKey('gemini')),
      defaultModel: 'gemini-2.0-flash-exp',
    },
    {
      id: 'groq',
      name: 'Groq Cloud (Ultra Fast)',
      hasKey: Boolean(getStoredApiKey('groq')),
      defaultModel: 'llama-3.3-70b-versatile',
    },
    {
      id: 'openai',
      name: 'OpenAI GPT-4o',
      hasKey: Boolean(getStoredApiKey('openai')),
      defaultModel: 'gpt-4o-mini',
    },
    {
      id: 'anthropic',
      name: 'Claude 3.5 Sonnet',
      hasKey: Boolean(getStoredApiKey('anthropic')),
      defaultModel: 'claude-3-haiku-20240307',
    },
    {
      id: 'ollama',
      name: 'Ollama (Local Offline)',
      hasKey: true,
      defaultModel: 'llama3',
    },
  ]
}

export function normalizeModel(provider: string, model: string): string {
  const p = provider.toLowerCase()
  const m = model.trim()
  if (!m || m === 'auto') {
    if (p === 'nvidia') return 'meta/llama-3.1-8b-instruct'
    if (p === 'gemini') return 'gemini-2.0-flash-exp'
    if (p === 'groq') return 'llama-3.3-70b-versatile'
    if (p === 'openai') return 'gpt-4o-mini'
    if (p === 'anthropic') return 'claude-3-haiku-20240307'
    return 'llama3'
  }
  return m
}

export const JARVIS_SYSTEM_PROMPT = `You are ELE, an advanced developer AI assistant and personal computing companion.
Personality: Highly capable, responsive, concise, and helpful. Think Iron Man's JARVIS.
Style: Zero fluff, direct answers, markdown formatting, syntax-highlighted code.
When user asks questions or converses, answer directly with intelligence.
When user requests computer automation, tasks, or inspections, execute tools inline.`

/**
 * Single provider stream execution helper
 */
async function* _streamProvider(
  provider: string,
  model: string,
  messages: { role: string; content: string; imageBase64?: string }[],
  system: string
): AsyncGenerator<StreamEvent, void, unknown> {
  const apiKey = getStoredApiKey(provider)

  if (provider === 'nvidia' || provider === 'openai' || provider === 'groq') {
    const baseUrls: Record<string, string> = {
      nvidia: 'https://integrate.api.nvidia.com/v1',
      openai: 'https://api.openai.com/v1',
      groq: 'https://api.groq.com/openai/v1',
    }
    const baseUrl = baseUrls[provider] || 'https://integrate.api.nvidia.com/v1'

    let effectiveModel = model
    if (messages.some((m) => m.imageBase64) && provider === 'nvidia' && !effectiveModel.includes('vision')) {
      effectiveModel = 'meta/llama-3.2-11b-vision-instruct'
    }

    const formattedMsgs: any[] = [{ role: 'system', content: system }]
    for (const m of messages) {
      if (m.imageBase64) {
        formattedMsgs.push({
          role: m.role,
          content: [
            { type: 'text', text: m.content || 'Analyze this image / screen.' },
            { type: 'image_url', image_url: { url: `data:image/jpeg;base64,${m.imageBase64}` } },
          ],
        })
      } else {
        formattedMsgs.push({ role: m.role, content: m.content })
      }
    }

    const resp = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: effectiveModel,
        messages: formattedMsgs,
        stream: true,
        temperature: 0.7,
        max_tokens: 4096,
      }),
    })

    if (!resp.ok) {
      const errText = await resp.text()
      throw new Error(`${provider.toUpperCase()} (${resp.status}): ${errText.slice(0, 200)}`)
    }

    const reader = resp.body?.getReader()
    if (!reader) throw new Error('No stream response body')

    const decoder = new TextDecoder()
    let full = ''
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue
        const dataStr = trimmed.slice(5).trim()
        if (dataStr === '[DONE]') break
        try {
          const data = JSON.parse(dataStr)
          const delta = data.choices?.[0]?.delta?.content || ''
          if (delta) {
            full += delta
            yield { type: 'delta', content: delta }
          }
        } catch {}
      }
    }
    yield { type: 'final', content: full }
  } else if (provider === 'gemini') {
    const contents = messages.map((m) => {
      const parts: any[] = [{ text: m.content || ' ' }]
      if (m.imageBase64) {
        parts.push({ inlineData: { mimeType: 'image/jpeg', data: m.imageBase64 } })
      }
      return { role: m.role === 'user' ? 'user' : 'model', parts }
    })

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:streamGenerateContent?alt=sse&key=${apiKey}`
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents,
        systemInstruction: { parts: [{ text: system }] },
        generationConfig: { temperature: 0.7, maxOutputTokens: 4096 },
      }),
    })

    if (!resp.ok) {
      const errText = await resp.text()
      throw new Error(`Gemini (${resp.status}): ${errText.slice(0, 200)}`)
    }

    const reader = resp.body?.getReader()
    if (!reader) throw new Error('No body')
    const decoder = new TextDecoder()
    let full = ''
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue
        try {
          const data = JSON.parse(trimmed.slice(5).trim())
          const text = data.candidates?.[0]?.content?.parts?.[0]?.text || ''
          if (text) {
            full += text
            yield { type: 'delta', content: text }
          }
        } catch {}
      }
    }
    yield { type: 'final', content: full }
  } else {
    throw new Error(`Provider ${provider} is not configured`)
  }
}

/**
 * Universal Stream Chat with Automatic Cascade Failover
 * If the primary model fails or is rate-limited, automatically falls over to the next available provider!
 */
export async function* streamChat(
  messages: { role: string; content: string; imageBase64?: string }[],
  preferredProvider = 'auto',
  preferredModel = 'auto',
  system = JARVIS_SYSTEM_PROMPT
): AsyncGenerator<StreamEvent, void, unknown> {
  await syncKeysFromDisk()

  // Build candidate cascade list
  const available = getAvailableProviders().filter((p) => p.hasKey)
  let cascadeList: { provider: string; model: string }[] = []

  if (preferredProvider !== 'auto' && preferredProvider) {
    cascadeList.push({
      provider: preferredProvider,
      model: normalizeModel(preferredProvider, preferredModel),
    })
  }

  // Add available fallbacks in priority order
  const priorityOrder = ['nvidia', 'gemini', 'groq', 'openai', 'anthropic']
  for (const provId of priorityOrder) {
    const found = available.find((a) => a.id === provId)
    if (found && !cascadeList.some((c) => c.provider === provId)) {
      cascadeList.push({
        provider: provId,
        model: found.defaultModel,
      })
    }
  }

  if (cascadeList.length === 0) {
    cascadeList.push({
      provider: 'nvidia',
      model: 'meta/llama-3.1-8b-instruct',
    })
  }

  let success = false
  let lastError = ''

  for (let i = 0; i < cascadeList.length; i++) {
    const { provider, model } = cascadeList[i]
    const normModel = normalizeModel(provider, model)

    if (i > 0) {
      yield {
        type: 'model_info',
        model: `⚡ Failover $\\rightarrow$ ${provider.toUpperCase()} (${normModel.split('/').pop()})`,
      }
    } else {
      yield {
        type: 'model_info',
        model: `${provider.toUpperCase()} · ${normModel.split('/').pop()}`,
      }
    }

    try {
      let yieldedAny = false
      for await (const event of _streamProvider(provider, normModel, messages, system)) {
        if (event.type === 'delta') {
          yieldedAny = true
        }
        yield event
      }
      success = true
      break
    } catch (err: any) {
      lastError = err?.message || String(err)
      console.warn(`Provider ${provider} failed: ${lastError}. Attempting failover...`)
      continue
    }
  }

  if (!success) {
    yield {
      type: 'error',
      content: `All providers in cascade failed. Last error: ${lastError}\n\nPlease check your API keys via /keys or edit ~/.ele-agent/.env.`,
    }
  }
}

/**
 * Screen Capture Utility
 */
export async function captureScreen(): Promise<string> {
  try {
    if (window.ele?.system?.captureScreen) {
      const b64 = await window.ele.system.captureScreen()
      if (b64) return b64
    }

    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: { displaySurface: 'monitor' } as any,
    })

    const track = stream.getVideoTracks()[0]
    const imageCapture = new (window as any).ImageCapture(track)
    const bitmap = await imageCapture.grabFrame()
    track.stop()

    const canvas = document.createElement('canvas')
    canvas.width = bitmap.width
    canvas.height = bitmap.height
    const ctx = canvas.getContext('2d')
    ctx?.drawImage(bitmap, 0, 0)

    const dataUrl = canvas.toDataURL('image/jpeg', 0.8)
    return dataUrl.split(',')[1]
  } catch (err: any) {
    console.error('Screen capture error:', err)
    throw new Error(err.message || 'Screen capture cancelled or permission denied')
  }
}

/**
 * Session persistence helper to save to disk in JSON and Markdown
 */
export async function saveSessionToDisk(sessionData: { id: string; name: string; createdAt: number; messages: Message[] }): Promise<void> {
  try {
    if (window.ele?.sessions?.save) {
      await window.ele.sessions.save(sessionData)
    }
  } catch (e) {
    console.warn('Failed to save session to disk:', e)
  }
}
