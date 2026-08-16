# Questions Log - All Q&A History

## Chunk 1: Project Goals & Scope (5 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 1 | Primary goal? | Personal/learning project | 2026-08-14 |
| 2 | Interfaces needed? | CLI first, then Web, Desktop, Telegram | 2026-08-14 |
| 3 | Target scale? | Single user, local machine | 2026-08-14 |
| 4 | CLI focus? | All features eventually (chat, voice, plugins, memory) | 2026-08-14 |
| 5 | LLM providers? | External APIs only: Gemini, Groq, NVIDIA, Claude, GPT | 2026-08-14 |

## Chunk 2: Architecture & Configuration (4 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 6 | Backend architecture? | Keep FastAPI + WebSocket (multi-interface ready) | 2026-08-14 |
| 7 | API key management? | BYOK: user keys first, platform keys fallback | 2026-08-14 |
| 8 | Config format? | TOML (Python standard) | 2026-08-14 |
| 9 | Voice priority? | Two-mode: Chat + Autonomous with Ellie avatar | 2026-08-14 |

## Chunk 3: Ellie Autonomous Mode Design (3 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 10 | Ellie avatar implementation? | Braille animation (Option B - Textual Canvas) | 2026-08-14 |
| 11 | Voice engines? | Hybrid: Online (Whisper+Edge-TTS) + Offline (Vosk+Coqui+pyttsx3) | 2026-08-14 |
| 12 | Continuous listening? | Always listening with VAD (Voice Activity Detection) | 2026-08-14 |

## Chunk 4: Voice Engine Details (3 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 13 | VAD Engine? | Silero VAD (ONNX) | 2026-08-14 |
| 14 | Offline TTS primary? | Both: Coqui primary, pyttsx3 fallback | 2026-08-14 |
| 15 | Vosk model size? | Medium (1.8 GB) | 2026-08-14 |

## Chunk 5: Audio & Integration (4 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 16 | Audio backend? | sounddevice (PortAudio, async-friendly) | 2026-08-14 |
| 17 | Streaming TTS? | Yes, chunked playback | 2026-08-14 |
| 18 | Coqui voice cloning? | Yes, set up now (30s freestyle) | 2026-08-14 |
| 19 | Wake word in Chat Mode? | Yes, Porcupine "Hey Ellie" | 2026-08-14 |

## Chunk 6: Terminal & Detection (4 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 20 | Terminal detection? | Yes, detect Kitty/iTerm2/WezTerm for image upgrade | 2026-08-14 |
| 21 | Ellie braille design? | Abstract geometric | 2026-08-14 |
| 22 | Online/offline check? | On-demand (before each voice request) | 2026-08-14 |
| 23 | Porcupine access key? | Don't know - need Picovoice Console setup | 2026-08-14 |

## Chunk 7: CLI UX Details (25 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 24 | Sidebar navigation? | Chat, Sessions, Tools, Plugins, Settings | 2026-08-14 |
| 25 | Message bubbles? | Rich with metadata (avatar, timestamp, tool badges, thought toggle, copy) | 2026-08-14 |
| 26 | Thought streaming? | Inline expandable (click to expand) | 2026-08-14 |
| 27 | Code display? | Full syntax highlighting with line numbers | 2026-08-14 |
| 28 | Session management? | Tabbed sessions (multiple concurrent) | 2026-08-14 |
| 29 | Execution detail? | Verbose (every command, output, timing, exit code) | 2026-08-14 |
| 30 | Conversation panel? | Bottom panel (40% height) | 2026-08-14 |
| 31 | Long progress? | All: spinner + elapsed + progress bar + live tail | 2026-08-14 |
| 32 | File tree features? | Full IDE-like (expand/collapse, search, git status, drag-drop) | 2026-08-14 |
| 33 | Code editor? | Textual TextArea (built-in) | 2026-08-14 |
| 34 | Shell colors? | Full ANSI support | 2026-08-14 |
| 35 | Browser automation? | Visible option (can watch browser work) | 2026-08-14 |
| 36 | Plugin browse? | Search + list | 2026-08-14 |
| 37 | Plugin templates? | Python skill, JSON manifest, WASM | 2026-08-14 |
| 38 | RAG file types? | Code + docs + config (*.py, *.js, *.ts, *.md, *.txt, *.json, *.yaml, *.toml) | 2026-08-14 |
| 39 | Project detection? | Manual + auto (git repos + marker files) | 2026-08-14 |
| 40 | Episodic memory? | All tool executions | 2026-08-14 |
| 41 | Config path (Windows)? | %USERPROFILE%\.ele-agent\ | 2026-08-14 |
| 42 | Secrets encryption? | Age (hardware-bound TPM/Windows Hello) | 2026-08-14 |
| 43 | Built-in themes? | All 10+ from Textual gallery | 2026-08-14 |
| 44 | Custom theme creation? | Interactive builder in CLI | 2026-08-14 |
| 45 | Wizard order? | Theme → API Keys → Voice → Tools → Plugins | 2026-08-14 |
| 46 | API key input? | All 5 providers in one screen | 2026-08-14 |

## Chunk 8: CLI Polish & Backend (24 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 47 | Status bar? | Connection, Model, Credits, Battery, Voice, Time | 2026-08-14 |
| 48 | Command palette? | All actions (Space+h): sessions, themes, plugins, tools, settings | 2026-08-14 |
| 49 | Notifications? | Sidebar badge on relevant nav item | 2026-08-14 |
| 50 | Mouse support? | Full: click messages, sidebar, buttons, scroll | 2026-08-14 |
| 51 | Ellie click area? | Full avatar + label | 2026-08-14 |
| 52 | Ellie anim FPS? | 60 FPS | 2026-08-14 |
| 53 | Command highlight? | Yes, full shell syntax | 2026-08-14 |
| 54 | Git integration? | Full: status icons, branch, diff on hover | 2026-08-14 |
| 55 | Shell history? | Both: arrow keys + searchable panel | 2026-08-14 |
| 56 | Browser screenshots? | Both: auto + on demand | 2026-08-14 |
| 57 | Plugin updates? | On startup | 2026-08-14 |
| 58 | Plugin trust? | Unrestricted | 2026-08-14 |
| 59 | FAISS rebuild? | On session start | 2026-08-14 |
| 60 | Embedding model? | Local: BGE-small | 2026-08-14 |
| 61 | Metadata DB? | SQLite | 2026-08-14 |
| 62 | Age KDF? | Hardware-bound (TPM/Windows Hello) | 2026-08-14 |
| 63 | Config validation? | Schema-based (pydantic) | 2026-08-14 |
| 64 | Theme preview? | Preview pane | 2026-08-14 |
| 65 | Voice test in wizard? | Yes, record + playback test | 2026-08-14 |
| 66 | Tool permissions? | All enabled by default | 2026-08-14 |
| 67 | Crash reports? | Local only (~/.ele-agent/logs/crashes/) | 2026-08-14 |
| 68 | Log levels? | Structured JSON + file rotation + per-module | 2026-08-14 |

## Chunk 9: Backend Architecture (24 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 69 | WS auth? | JWT in cookie (HttpOnly) | 2026-08-14 |
| 70 | Rate limiting? | Per-IP (before auth) | 2026-08-14 |
| 71 | Session storage? | SQLite (persistent) | 2026-08-14 |
| 72 | LangGraph checkpointer? | SqliteSaver | 2026-08-14 |
| 73 | Parallel LLMs? | Auto: use all available keys | 2026-08-14 |
| 74 | Tool calling format? | Unified abstraction (adapter per provider) | 2026-08-14 |
| 75 | Merge strategy? | Heuristic: longest/best | 2026-08-14 |
| 76 | File sandbox? | Home directory (~), full access | 2026-08-14 |
| 77 | Shell safety? | Confirm all, no list | 2026-08-14 |
| 78 | Browser library? | Both (configurable: Playwright/Selenium) | 2026-08-14 |
| 79 | RAG chunking? | Fixed size (512 tokens) | 2026-08-14 |
| 80 | Hybrid search? | Yes (FAISS + BM25) | 2026-08-14 |
| 81 | Short-term buffer? | Dynamic: fit in token budget | 2026-08-14 |
| 82 | Episodic TTL? | Forever (manual cleanup) | 2026-08-14 |
| 83 | WASM sandbox? | No sandbox (trusted only) | 2026-08-14 |
| 84 | Marketplace? | Cloud (current plan) | 2026-08-14 |
| 85 | Telegram mode? | Webhook (production) | 2026-08-14 |
| 86 | Telegram users? | Single user (owner only) | 2026-08-14 |
| 87 | Desktop updater? | electron-updater + GitHub Releases | 2026-08-14 |
| 88 | System tray? | Full menu (sessions, plugins, etc.) | 2026-08-14 |
| 89 | Web realtime? | Both (WS for chat, SSE for notifications) | 2026-08-14 |
| 90 | Web auth? | Skip for now (no auth initially) | 2026-08-14 |
| 91 | Startup time? | < 2 seconds (lazy-load) | 2026-08-14 |
| 92 | Auto backend? | Yes, spawn uvicorn subprocess | 2026-08-14 |

## Chunk 10: Config & Voice Details (24 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 93 | Config hot reload? | Yes, watch config file | 2026-08-14 |
| 94 | Ellie idle anim? | Subtle pulse | 2026-08-14 |
| 95 | Token cost display? | Yes, real-time counter | 2026-08-14 |
| 96 | Hidden files? | Toggle (Ctrl+h) | 2026-08-14 |
| 97 | Editor auto-save? | Yes, instant on focus loss | 2026-08-14 |
| 98 | Shell pager? | Built-in pager in TUI | 2026-08-14 |
| 99 | Browser stealth? | Yes, playwright-stealth | 2026-08-14 |
| 100 | RAG re-index? | On session start only | 2026-08-14 |
| 101 | Session export? | Markdown (human readable) | 2026-08-14 |
| 102 | Dep resolution? | pip (standard) | 2026-08-14 |
| 103 | Plugin versioning? | Semver (^1.0.0) | 2026-08-14 |
| 104 | Telegram commands? | Custom: user defines | 2026-08-14 |
| 105 | Desktop window state? | Yes (position, size, maximized) | 2026-08-14 |
| 106 | Desktop frameless? | Yes, custom titlebar | 2026-08-14 |
| 107 | Web PWA? | Yes, manifest + service worker | 2026-08-14 |
| 108 | Web offline? | Yes, cache static assets | 2026-08-14 |
| 109 | Test framework? | pytest (backend), vitest (web) | 2026-08-14 |
| 110 | CI trigger? | Push + PR | 2026-08-14 |
| 111 | Release versioning? | Semver (1.0.0) | 2026-08-14 |
| 112 | Doc generation? | Yes (pdoc/sphinx) | 2026-08-14 |
| 113 | Multi-language? | English only (v1) | 2026-08-14 |
| 114 | Accessibility? | Full WCAG AA | 2026-08-14 |
| 115 | Voice interrupt? | Stop TTS, start STT immediately | 2026-08-14 |
| 116 | Autonomous multi-task? | Parallel tool chains | 2026-08-14 |

## Chunk 11: Tools, RAG, Memory, Plugins, Telegram (11 questions)

| # | Question | Answer | Date |
|---|----------|--------|------|
| 117 | Diff view? | Both (side-by-side + unified toggle) | 2026-08-14 |
| 118 | Terminal emulator? | Yes (pty + xterm.js in TUI) | 2026-08-14 |
| 119 | RAG cross-ref? | Yes, parse imports/links | 2026-08-14 |
| 120 | Episodic dedup? | Yes, embed + cluster similar | 2026-08-14 |
| 121 | Plugin signing? | No, trust registry | 2026-08-14 |
| 122 | Telegram files? | Yes, send/receive files | 2026-08-14 |

---

## Summary Statistics

- **Total Questions**: 122
- **Chunks**: 11
- **Avg per chunk**: ~11 questions
- **Coverage**: Project goals, architecture, CLI UX, voice, backend, tools, memory, plugins, telemetry

---

## Key Decisions Requiring Action

| Item | Action Required | Status |
|------|-----------------|--------|
| Porcupine Access Key | Sign up at console.picovoice.ai, create "Hey Ellie" keyword | ⏳ Pending |
| Coqui Voice Sample | Record 30s freestyle, save to ~/.ele-agent/voice/cloned/my_voice.wav | ⏳ Pending |
| Vosk Model Download | Download 1.8 GB model to ~/.ele-agent/voice/vosk-model/ | ⏳ Pending |
| Silero VAD ONNX | Export model: `torch.onnx.export(model, ..., 'silero_vad.onnx')` | ⏳ Pending |

---

## Files Created in temporary_docs/

1. PROJECT_OVERVIEW.md - Master specification
2. ARCHITECTURE_DECISIONS.md - Tradeoffs & rationale
3. CLI_DESIGN.md - TUI layouts, components, animations
4. CONFIG_SPEC.md - TOML schema + Pydantic models
5. API_KEY_MANAGEMENT.md - BYOK flow + encryption
6. PLUGIN_SYSTEM.md - CLI commands + SDK
7. VOICE_INTEGRATION.md - Hybrid voice architecture
8. ELLIE_AUTONOMOUS_MODE.md - Ellie design + two-mode
9. HYBRID_VOICE_ARCHITECTURE.md - Online/offline engines
10. MEMORY_RAG_DESIGN.md - 4-layer memory + RAG
11. PHASE_PLAN.md - 5-phase implementation plan
12. QUESTIONS_LOG.md - This file