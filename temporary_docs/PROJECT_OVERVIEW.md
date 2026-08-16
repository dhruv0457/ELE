# ELE Agent - Project Overview & Decisions

## Project Goals
- **Primary**: Personal/learning project
- **Target**: Single user on local machine
- **Approach**: CLI-first (Textual TUI), then expand to Web/Desktop/Telegram
- **Scope**: Full-featured AI desktop assistant with tools, voice, plugins, memory

## User Requirements Summary

### Interfaces Priority
1. **CLI/TUI (Textual)** - Primary focus, build first
2. **Web (Next.js)** - Secondary
3. **Desktop (Electron+React)** - Tertiary
4. **Telegram Bot** - Later

### LLM Providers (External APIs Only)
- Google Gemini
- Groq
- NVIDIA (NIM)
- Anthropic Claude
- OpenAI GPT
- **No local LLMs** (Ollama, llama.cpp) - user explicitly wants external APIs

### Tools Required (All)
- File operations (read/write/list/glob/delete)
- Shell commands
- Browser automation (Playwright)
- App launching
- Email/Calendar (future)

### API Key Management (BYOK Pattern)
- **Backend/Platform keys**: Stored in `.env` (platform API keys for credits)
- **User keys**: Users bring their own keys via UI/CLI settings
- **Priority**: User keys first → Platform keys as fallback
- **Storage**: Secure (OS keyring for desktop, encrypted config for CLI)

### Configuration
- **Format**: TOML (Python standard, good tooling)
- Single config file for settings
- Environment variables for secrets
- **First-run wizard**: Full (all settings: theme, voice, tools, plugins, API keys)
- **Wizard order**: Theme → API Keys → Voice → Tools → Plugins
- **API key input**: All 5 providers in one screen
- **Config path (Windows)**: %USERPROFILE%\.ele-agent\
- **Secrets encryption**: Age with hardware-bound key (TPM/Windows Hello)
- **Config validation**: Schema-based (pydantic)
- **Hot reload**: Yes, watch config file for instant theme/setting changes
- **Startup time**: < 2 seconds (lazy-load heavy components)
- **Auto backend**: Yes, spawn uvicorn subprocess on CLI start

### UI/UX Requirements - CLI Specific
- **Best-in-class terminal animations**
- **Rich TUI with smooth transitions**
- **Thought streaming, tool execution visualization**
- **Overlay-style status indicators**
- **Keyboard-driven with mouse support** (Full: click messages, sidebar, buttons, scroll)
- **Keyboard shortcuts**: Vim-style (Space leader key)
- **Status bar**: Connection, Model, Credits, Battery, Voice, Time
- **Command palette**: All actions (Space+h) - sessions, themes, plugins, tools, settings
- **Notifications**: Sidebar badge on relevant nav item
- **Themes**: All 10+ from Textual gallery + custom theme builder (live preview pane)
- **Custom themes**: Interactive builder in CLI
- **Multi-language**: English only (v1), i18n ready structure
- **Accessibility**: Full WCAG AA (live regions, focus management)

### Voice Integration Vision (Unique)
**Two-Mode CLI Interface:**

**Mode 1: Chat Interface (Default)**
- Standard textual chat with thought streaming
- Text input at bottom
- Sidebar with sessions, plugins, settings
- **Voice button (mic icon)** for push-to-talk
- **Wake word**: "Hey Ellie" (Porcupine) for hands-free

**Mode 2: Autonomous Agent Mode (Triggered by Voice Button)**
- **Full-screen takeover**: Terminal becomes autonomous coding/automation view
- **Agent runs commands by itself** - visible execution stream
- **"Ellie" miniature avatar** at top-center of screen
- **Animations**: Ellie speaks, gestures, shows thinking state (60 FPS)
- **Voice output**: Ellie talks through TTS (streaming chunks)
- **Voice input**: Continuous listening (Silero VAD)
- **Text sync**: Everything spoken also shown as text in side panel
- **Click Ellie miniature** (full avatar + label area) → Stop autonomous mode → Return to chat interface
- **Use cases**: "Go to this link, open this, see what's different", coding tasks, research
- **Idle animation**: Subtle pulse
- **Token cost**: Real-time counter in status
- **Interrupt**: Stop TTS, start STT immediately (natural conversation)
- **Multi-task**: Parallel tool chains for independent tasks

---

## Technical Decisions Made

| Decision | Choice | Date |
|----------|--------|------|
| Backend architecture | Keep FastAPI + WebSocket | 2026-08-14 |
| Config format | TOML | 2026-08-14 |
| CLI themes | Built-in (All 10+ from Textual gallery) | 2026-08-14 |
| Voice integration | Two-mode: Chat + Autonomous Agent with Ellie avatar | 2026-08-14 |
| Ellie avatar | Braille animation (Textual Canvas) - Abstract geometric | 2026-08-14 |
| Voice engines | Hybrid: Online (Whisper+Edge-TTS) + Offline (Vosk+Coqui+pyttsx3) | 2026-08-14 |
| Listening mode | Always listening with VAD (Voice Activity Detection) | 2026-08-14 |
| VAD Engine | Silero VAD (ONNX) | 2026-08-14 |
| Offline TTS Primary | Coqui TTS (with pyttsx3 fallback) | 2026-08-14 |
| Offline STT Model | Vosk Medium (1.8 GB) | 2026-08-14 |
| Audio Backend | sounddevice (PortAudio, async-friendly) | 2026-08-14 |
| Streaming TTS | Yes, chunked playback | 2026-08-14 |
| Coqui Voice Cloning | Yes, set up now (30s freestyle sample) | 2026-08-14 |
| Wake Word (Chat Mode) | Porcupine "Hey Ellie" | 2026-08-14 |
| Terminal Detection | Detect Kitty/iTerm2/WezTerm for image upgrade | 2026-08-14 |
| Online/Offline Check | On-demand (before each voice request) | 2026-08-14 |
| Supabase | Skip for now (local-only MVP) | 2026-08-14 |
| Keyboard Shortcuts | Vim-style (Space leader) | 2026-08-14 |
| Config Wizard | Full (all settings) | 2026-08-14 |
| Sidebar Navigation | Chat, Sessions, Tools, Plugins, Settings | 2026-08-14 |
| Message Bubbles | Rich with metadata (avatar, timestamp, tool badges, thought toggle, copy) | 2026-08-14 |
| Thought Streaming | Inline expandable (click to expand) | 2026-08-14 |
| Code Display | Full syntax highlighting with line numbers | 2026-08-14 |
| Session Management | Tabbed sessions (multiple concurrent) | 2026-08-14 |
| Execution Detail | Verbose (every command, output, timing, exit code) | 2026-08-14 |
| Conversation Panel | Bottom panel (40% height) | 2026-08-14 |
| Long Progress | Spinner + elapsed + progress bar + live tail | 2026-08-14 |
| File Tree | Full IDE-like (expand/collapse, search, git status, drag-drop) | 2026-08-14 |
| Code Editor | Textual TextArea (built-in) | 2026-08-14 |
| Shell Colors | Full ANSI support | 2026-08-14 |
| Browser Automation | Visible option (can watch browser work) | 2026-08-14 |
| Plugin Browse | Search + list | 2026-08-14 |
| Plugin Templates | Python skill, JSON manifest, WASM | 2026-08-14 |
| RAG File Types | Code + docs + config (*.py, *.js, *.ts, *.md, *.txt, *.json, *.yaml, *.toml) | 2026-08-14 |
| Project Detection | Manual + auto (git repos + marker files) | 2026-08-14 |
| Episodic Memory | All tool executions | 2026-08-14 |
| Config Path (Win) | %USERPROFILE%\.ele-agent\ | 2026-08-14 |
| Secrets Encryption | Age (hardware-bound TPM/Windows Hello) | 2026-08-14 |
| Custom Themes | Interactive builder in CLI | 2026-08-14 |
| Status Bar | Connection, Model, Credits, Battery, Voice, Time | 2026-08-14 |
| Command Palette | All actions (Space+h) | 2026-08-14 |
| Notifications | Sidebar badge | 2026-08-14 |
| Mouse Support | Full (click, scroll, sidebar, buttons) | 2026-08-14 |
| Ellie Click Area | Full avatar + label | 2026-08-14 |
| Ellie Anim FPS | 60 FPS | 2026-08-14 |
| Command Highlight | Full shell syntax | 2026-08-14 |
| Git Integration | Full (status icons, branch, diff on hover) | 2026-08-14 |
| Shell History | Both (arrow keys + searchable panel) | 2026-08-14 |
| Browser Screenshots | Both (auto + on demand) | 2026-08-14 |
| Plugin Updates | On startup | 2026-08-14 |
| Plugin Trust | Unrestricted | 2026-08-14 |
| FAISS Rebuild | On session start | 2026-08-14 |
| Embedding Model | Local: BGE-small | 2026-08-14 |
| Metadata DB | SQLite | 2026-08-14 |
| Age KDF | Hardware-bound (TPM/Windows Hello) | 2026-08-14 |
| Config Validation | Schema-based (pydantic) | 2026-08-14 |
| Theme Preview | Preview pane | 2026-08-14 |
| Voice Test in Wizard | Yes (record + playback) | 2026-08-14 |
| Tool Permissions | All enabled by default | 2026-08-14 |
| Crash Reports | Local only (~/.ele-agent/logs/crashes/) | 2026-08-14 |
| Log Levels | Structured JSON + file rotation + per-module | 2026-08-14 |
| WS Auth | JWT in cookie (HttpOnly) | 2026-08-14 |
| Rate Limiting | Per-IP (before auth) | 2026-08-14 |
| Session Storage | SQLite (persistent) | 2026-08-14 |
| LangGraph Checkpointer | SqliteSaver | 2026-08-14 |
| Parallel LLMs | Auto: use all available keys | 2026-08-14 |
| Tool Calling Format | Unified abstraction (adapter per provider) | 2026-08-14 |
| Merge Strategy | Heuristic: longest/best | 2026-08-14 |
| File Sandbox | Home directory (~), full access | 2026-08-14 |
| Shell Safety | Confirm all, no list | 2026-08-14 |
| Browser Library | Both (configurable: Playwright/Selenium) | 2026-08-14 |
| RAG Chunking | Fixed size (512 tokens) | 2026-08-14 |
| Hybrid Search | Yes (FAISS + BM25) | 2026-08-14 |
| Short-term Buffer | Dynamic: fit in token budget | 2026-08-14 |
| Episodic TTL | Forever (manual cleanup) | 2026-08-14 |
| WASM Sandbox | No sandbox (trusted only) | 2026-08-14 |
| Marketplace | Cloud (current plan) | 2026-08-14 |
| Telegram Mode | Webhook (production) | 2026-08-14 |
| Telegram Users | Single user (owner only) | 2026-08-14 |
| Desktop Updater | electron-updater + GitHub Releases | 2026-08-14 |
| System Tray | Full menu (sessions, plugins, etc.) | 2026-08-14 |
| Web Real-time | Both (WS for chat, SSE for notifications) | 2026-08-14 |
| Web Auth | Skip for now (no auth initially) | 2026-08-14 |
| Startup Time | < 2 seconds (lazy-load) | 2026-08-14 |
| Auto Backend | Yes, spawn uvicorn subprocess | 2026-08-14 |
| Config Hot Reload | Yes, watch config file | 2026-08-14 |
| Ellie Idle Anim | Subtle pulse | 2026-08-14 |
| Token Cost Display | Real-time counter | 2026-08-14 |
| Hidden Files | Toggle (Ctrl+h) | 2026-08-14 |
| Editor Auto-save | Yes, instant on focus loss | 2026-08-14 |
| Shell Pager | Built-in pager in TUI | 2026-08-14 |
| Browser Stealth | Yes, playwright-stealth | 2026-08-14 |
| RAG Re-index | On session start only | 2026-08-14 |
| Session Export | Markdown (human readable) | 2026-08-14 |
| Dep Resolution | pip (standard) | 2026-08-14 |
| Plugin Versioning | Semver (^1.0.0) | 2026-08-14 |
| Telegram Commands | Custom: user defines | 2026-08-14 |
| Desktop Window State | Yes (position, size, maximized) | 2026-08-14 |
| Desktop Frameless | Yes, custom titlebar | 2026-08-14 |
| Web PWA | Yes, manifest + service worker | 2026-08-14 |
| Web Offline | Yes, cache static assets | 2026-08-14 |
| Test Framework | pytest (backend), vitest (web) | 2026-08-14 |
| CI Trigger | Push + PR | 2026-08-14 |
| Release Versioning | Semver (1.0.0) | 2026-08-14 |
| Doc Generation | Yes (pdoc/sphinx) | 2026-08-14 |
| Multi-language | English only (v1) | 2026-08-14 |
| Accessibility | Full WCAG AA | 2026-08-14 |
| Voice Interrupt | Stop TTS, start STT immediately | 2026-08-14 |
| Autonomous Multi-task | Parallel tool chains | 2026-08-14 |
| Diff View | Both (side-by-side + unified toggle) | 2026-08-14 |
| Terminal Emulator | Yes (pty + xterm.js in TUI) | 2026-08-14 |
| RAG Cross-ref | Yes, parse imports/links | 2026-08-14 |
| Episodic Dedup | Yes, embed + cluster similar | 2026-08-14 |
| Plugin Signing | No, trust registry | 2026-08-14 |
| Telegram Files | Yes, send/receive files | 2026-08-14 |

---

## Porcupine Wake Word Setup (Action Required)

**Picovoice Console Setup:**
1. Go to https://console.picovoice.ai/
2. Sign up for free account (Personal use: 1 keyword free)
3. Create keyword: "Hey Ellie" (or "Hey ELE")
4. Download `.ppn` file for your platform (Windows/Linux/Mac)
5. Copy **AccessKey** from dashboard
6. Add to config: `PORCUPINE_ACCESS_KEY=your_key_here`

**Free Tier Limits:**
- 1 custom keyword
- Personal/non-commercial use
- No expiry

---

## Coqui Voice Cloning - 30 Second Freestyle

**Recording Tips:**
- Quiet room, good microphone
- Speak naturally, varied intonation
- Include: questions, statements, excitement, calm
- ~30 seconds continuous speech
- Save as: `~/.ele-agent/voice/cloned/my_voice.wav`

---

## Vim-Style Keyboard Shortcuts

| Shortcut | Action | Mode |
|----------|--------|------|
| `Space` | Leader key | Both |
| `Space e` | Toggle Ellie/Autonomous mode | Both |
| `Space v` | Toggle voice listening | Chat |
| `Space q` | Quit / Exit autonomous | Autonomous |
| `Space h` | Help / Command palette | Both |
| `Space s` | Save session | Both |
| `Space n` | New session | Both |
| `Space t` | Theme selector | Both |
| `Space p` | Plugin manager | Both |
| `Space /` | Search messages | Chat |
| `j/k` | Navigate up/down | Both |
| `Ctrl+d/u` | Half-page scroll | Both |
| `gg/G` | Top/Bottom | Both |

---

## Implementation Phases (Final)

### Phase 1: CLI Foundation + Chat Mode (Week 1-2)
- [ ] Unified config system (TOML + env) with pydantic validation
- [ ] Enhanced Textual TUI with built-in themes (10+)
- [ ] **Full first-run wizard**: Theme → API Keys → Voice → Tools → Plugins
- [ ] BYOK API key management in CLI settings (all 5 providers one screen)
- [ ] Direct backend connection (WebSocket with JWT cookie auth)
- [ ] Basic chat with thought streaming
- [ ] **Chat Mode UI**: Sidebar (Chat, Sessions, Tools, Plugins, Settings), message bubbles (rich metadata), input bar, voice button
- [ ] **Wake word**: Porcupine integration for "Hey Ellie"
- [ ] **Terminal detection**: Kitty/iTerm2/WezTerm for image upgrade path
- [ ] **Vim-style keybindings**: Space leader key
- [ ] **Session tabs**: Multiple concurrent sessions
- [ ] **Message features**: Inline thought expand, full syntax highlighting, copy button
- [ ] **Status bar**: Connection, Model, Credits, Battery, Voice, Time
- [ ] **Command palette**: Space+h for all actions
- [ ] **Notifications**: Sidebar badges
- [ ] **Mouse support**: Full click/scroll
- [ ] **Theme system**: 10+ built-in + custom builder with preview pane
- [ ] **Config**: Age encryption with TPM/Windows Hello
- [ ] **Logging**: Structured JSON + file rotation + per-module levels
- [ ] **Backend**: Per-IP rate limiting, SQLite sessions, SqliteSaver checkpointer
- [ ] **Startup**: < 2s, lazy-load, auto-spawn backend
- [ ] **Hot reload**: Config file watcher
- [ ] **Accessibility**: Full WCAG AA (live regions, focus mgmt)
- [ ] **Language**: English only (v1)

### Phase 2: Autonomous Agent Mode + Ellie (Week 2-3)
- [ ] **Mode switch**: Chat ↔ Autonomous toggle (`Space e`)
- [ ] **Ellie avatar**: Abstract geometric braille animation at top-center (60 FPS)
- [ ] **Image upgrade**: Ellie sprite sheet in supported terminals
- [ ] **Full-screen execution view**: Tool streaming, command output (verbose)
- [ ] **Hybrid TTS**: Edge-TTS (online, streaming) → Coqui cloned (offline) → pyttsx3 (fallback)
- [ ] **Hybrid STT**: Whisper API (online) → Vosk Medium (offline)
- [ ] **VAD**: Silero VAD (ONNX) for continuous listening
- [ ] **Audio I/O**: sounddevice for mic capture + speaker playback
- [ ] **Click Ellie to stop**: Return to chat mode (full avatar + label clickable)
- [ ] **Coqui voice cloning**: Record 30s freestyle, set up model
- [ ] **Conversation panel**: Bottom panel (40%)
- [ ] **Progress display**: Spinner + elapsed + progress bar + live tail
- [ ] **Command highlighting**: Full shell syntax in execution stream
- [ ] **Idle animation**: Subtle pulse
- [ ] **Token cost**: Real-time counter
- [ ] **Interrupt handling**: Stop TTS, start STT immediately
- [ ] **Multi-task**: Parallel tool chains
- [ ] File operations in TUI (tree view: full IDE-like with git, editor: Textual TextArea)
- [ ] Shell execution with output streaming (full ANSI)
- [ ] Browser automation panel (visible option, both Playwright/Selenium)
- [ ] Browser screenshots (auto on nav + on demand)
- [ ] Browser stealth: playwright-stealth
- [ ] Confirmation dialogs for all risky actions
- [ ] Shell history: arrow keys + searchable panel
- [ ] Terminal emulator: pty + xterm.js in TUI
- [ ] Diff view: both side-by-side and unified (toggle)
- [ ] Hidden files toggle: Ctrl+h
- [ ] Editor auto-save: instant on focus loss
- [ ] Shell pager: built-in in TUI
- [ ] **Agent**: Auto parallel LLMs, unified tool calling, heuristic merge

### Phase 3: Memory & RAG (Week 3-4)
- [ ] Local FAISS indexer (rebuild on session start)
- [ ] Conversation memory (SQLite)
- [ ] Project memory (file watching)
- [ ] RAG search in CLI (code + docs + config, BGE-small embeddings)
- [ ] Project detection (manual + auto)
- [ ] **RAG**: Fixed 512-token chunks, FAISS + BM25 hybrid search
- [ ] **RAG Cross-ref**: Parse imports/links for graph-aware retrieval
- [ ] **Memory**: Dynamic short-term buffer, forever episodic retention
- [ ] **Episodic Dedup**: Embed + cluster similar memories
- [ ] Session export: Markdown (human readable)

### Phase 4: Plugins & Polish (Week 4-5)
- [ ] Plugin system CLI commands
- [ ] Marketplace browsing in TUI (search + list)
- [ ] Plugin creation wizard (Python, JSON, WASM templates)
- [ ] Plugin auto-update on startup
- [ ] Unrestricted community plugins
- [ ] WASM plugins: no sandbox (trusted only)
- [ ] Plugin signing: no (trust registry)
- [ ] Plugin deps: pip (standard), semver
- [ ] Themes, animations, keyboard shortcuts
- [ ] Custom theme builder in CLI

### Phase 5: Expand to Web/Desktop (Week 5+)
- [ ] Web dashboard improvements (WS for chat, SSE for notifications, no auth initially)
- [ ] Web PWA: manifest + service worker, offline cache
- [ ] Desktop app enhancements (electron-updater, full system tray menu, frameless window, window state persistence)
- [ ] Telegram bot (webhook, single user, custom commands, file upload/download)

---

## Directory Structure for Docs
```
temporary_docs/
├── PROJECT_OVERVIEW.md              # This file
├── ARCHITECTURE_DECISIONS.md        # Detailed tradeoffs
├── CLI_DESIGN.md                    # TUI layout, components, animations
├── CONFIG_SPEC.md                   # Config file structure
├── API_KEY_MANAGEMENT.md            # BYOK flow
├── PLUGIN_SYSTEM.md                 # CLI plugin commands
├── VOICE_INTEGRATION.md             # Wake word, STT, TTS in CLI
├── ELLIE_AUTONOMOUS_MODE.md         # Ellie avatar, two-mode design
├── HYBRID_VOICE_ARCHITECTURE.md     # Online/offline voice engines
├── MEMORY_RAG_DESIGN.md             # Local storage, FAISS, SQLite
├── PHASE_PLAN.md                    # Detailed implementation plan
└── QUESTIONS_LOG.md                 # All Q&A history
```