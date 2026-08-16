# Phase Implementation Plan

## Overview

5 phases over ~5-6 weeks, CLI-first with backend shared across all interfaces.

## Phase 1: CLI Foundation + Chat Mode (Week 1-2)

### Goals
- Working CLI with Chat Mode
- Backend WebSocket connection
- Configuration system
- First-run wizard

### Backend Tasks (Week 1)
- [ ] **Config System**
  - Pydantic Settings with TOML + env loading
  - Hot-reload config watcher
  - Age encryption with hardware KDF (Windows Hello/TPM)
  - Schema validation

- [ ] **WebSocket API**
  - `/api/v1/ws/chat` endpoint with JWT cookie auth
  - Message types: message, thought, tool_start, tool_result, screenshot, progress, final, error, confirmation_required
  - Per-IP rate limiting (before auth)
  - SQLite session storage + SqliteSaver checkpointer

- [ ] **Agent Core**
  - LangGraph with parallel LLM nodes (auto: use all available keys)
  - Unified tool calling abstraction (OpenAI/Anthropic adapters)
  - Heuristic merge strategy (longest/best)
  - RAG node with FAISS + BM25 hybrid search

- [ ] **Executors**
  - File: read, write, list, glob, delete, patch
  - Shell: run with confirm_all, full ANSI capture
  - Browser: Playwright + Selenium (configurable), stealth mode, visible option
  - App launch: whitelist

- [ ] **Memory**
  - Short-term buffer (dynamic token budget)
  - Long-term FAISS with BGE-small embeddings
  - Episodic SQLite (forever retention, dedup)
  - Project memory with file watcher

### CLI Tasks (Week 1-2)
- [ ] **Textual App Structure**
  - Main app with mode switching (Chat ↔ Autonomous)
  - Vim-style keybindings (Space leader)
  - 10+ built-in themes + custom theme builder (preview pane)
  - Full mouse support

- [ ] **Chat Mode UI**
  - Sidebar: Chat, Sessions, Tools, Plugins, Settings (collapsible)
  - Tabbed sessions (multiple concurrent)
  - Message bubbles: rich metadata, inline thought expand, syntax highlighting, copy button
  - Input bar: textarea + voice button + send
  - Status bar: connection, model, credits, battery, voice, time
  - Command palette (Space+h): all actions
  - Notifications: sidebar badges

- [ ] **Configuration**
  - First-run wizard: Theme → API Keys → Voice → Tools → Plugins
  - All 5 providers in one API key screen
  - Voice test: record + playback
  - Tool permissions: all enabled by default
  - Config hot-reload

- [ ] **Voice (Chat Mode)**
  - Porcupine wake word ("Hey Ellie")
  - Push-to-talk button
  - Backend STT/TTS via WebSocket

- [ ] **Backend Auto-Start**
  - Spawn uvicorn subprocess on CLI launch
  - Startup target: < 2 seconds (lazy-load)

### Deliverables
```
cli/
  src/
    app.py              # Main Textual app
    screens/
      chat.py           # Chat mode screen
      settings.py       # Settings screen
      plugins.py        # Plugins screen
    widgets/
      message_bubble.py
      sidebar.py
      status_bar.py
      command_palette.py
    keybindings.py      # Vim-style Space leader
    themes.py           # 10+ themes + custom builder
    config.py           # TOML + Age encryption

backend/
  app/
    config.py           # Pydantic Settings
    routes/
      chat.py           # WebSocket endpoint
      settings.py       # API keys, config
    agents/
      graph.py          # LangGraph agent
      llm_clients.py    # Unified abstraction
    memory/
      manager.py        # 4-layer memory
    rag/
      indexer.py        # FAISS + BM25
    executors/
      registry.py       # File, shell, browser, app
```

---

## Phase 2: Autonomous Agent Mode + Ellie (Week 2-3)

### Goals
- Full-screen autonomous mode
- Ellie avatar with 60 FPS braille animation
- Hybrid voice pipeline (continuous VAD + streaming TTS)
- All tools integrated

### Autonomous Mode UI
- [ ] **Mode Toggle** (Space+e): Chat ↔ Autonomous with 300ms animation
- [ ] **Ellie Avatar** (top-center):
  - Braille animation via Textual Canvas (60 FPS)
  - States: idle (pulse), listening (waveform), thinking (spinner), working (progress), speaking (equalizer), error (shake)
  - Click area: full avatar + label → exit to chat
  - Image upgrade: sprite sheet in Kitty/iTerm2/WezTerm

- [ ] **Execution Stream** (top 60%):
  - Verbose: every command, args, stdout, stderr, exit code, timing
  - Full shell syntax highlighting
  - Progress: spinner + elapsed + progress bar + live tail
  - Tool calls highlighted

- [ ] **Conversation Panel** (bottom 40%):
  - Text sync: user speech (STT), Ellie speech (TTS), thoughts
  - Independent scroll

### Voice Pipeline (Hybrid)
- [ ] **STT**: Whisper API (online) → Vosk Medium (offline, 1.8 GB)
- [ ] **TTS**: Edge-TTS streaming (online) → Coqui cloned (offline) → pyttsx3 (fallback)
- [ ] **VAD**: Silero ONNX for continuous listening
- [ ] **Audio I/O**: sounddevice (PortAudio) async streams
- [ ] **Interrupt**: Stop TTS immediately when user speaks
- [ ] **Coqui Voice Cloning**: 30s freestyle sample → custom voice

### Tools Integration
- [ ] **File Tree**: Full IDE-like (git status icons, branch, diff on hover, search, drag-drop, hidden files toggle Ctrl+h)
- [ ] **Code Editor**: Textual TextArea with syntax highlighting, line numbers, auto-save on focus loss
- [ ] **Shell**: Built-in pager, history (arrow keys + searchable panel), full ANSI
- [ ] **Browser**: Visible option, stealth mode, screenshots (auto + on demand)
- [ ] **Terminal Emulator**: pty + xterm.js for interactive commands
- [ ] **Diff View**: Side-by-side + unified (toggle)

### Agent Enhancements
- [ ] **Multi-task**: Parallel tool chains for independent tasks
- [ ] **Token Cost**: Real-time counter in status bar
- [ ] **Idle Animation**: Subtle pulse

### Deliverables
```
cli/src/
  screens/
    autonomous.py       # Autonomous mode screen
  widgets/
    ellie_avatar.py     # Braille animation (60 FPS)
    execution_stream.py # Verbose tool output
    conversation_panel.py # Text sync panel
    file_tree.py        # IDE-like with git
    code_editor.py      # Textual TextArea
    shell_panel.py      # Pager, history, ANSI
    browser_panel.py    # Visible, stealth, screenshots
    terminal_emulator.py # pty + xterm.js
    diff_view.py        # Side-by-side + unified

backend/app/voice/
  manager.py            # Hybrid STT/TTS with fallback
  stt_whisper.py
  stt_vosk.py
  tts_edge.py
  tts_coqui.py
  tts_pyttsx3.py
  vad.py                # Silero ONNX
  wake_word.py          # Porcupine
  audio_pipeline.py     # sounddevice streams
```

---

## Phase 3: Memory & RAG Polish (Week 3-4)

### Goals
- Production-ready memory system
- Cross-file references for code
- Session export/import

### Tasks
- [ ] **RAG Enhancements**
  - Fixed 512-token chunking
  - FAISS + BM25 hybrid search with RRF
  - Cross-reference extraction (Python imports, JS imports, symbols)
  - Symbol boosting in search

- [ ] **Memory Features**
  - Episodic deduplication (embedding clustering, threshold 0.95)
  - Project context with file watcher (real-time updates)
  - Session export: Markdown (human-readable)
  - Session import: restore conversation

- [ ] **Rebuild Triggers**
  - Session start: full rebuild
  - File save: debounced 2s incremental
  - Manual: Space+r
  - Project switch: project-only

- [ ] **Performance**
  - Embedding cache
  - FAISS index persistence
  - Async memory operations

### Deliverables
```
backend/app/rag/
  cross_ref.py          # Import/symbol extraction
  hybrid_search.py      # FAISS + BM25 + RRF

backend/app/memory/
  long_term.py          # FAISS with caching
  episodic.py           # Deduplication
  project.py            # File watcher
  sessions.py           # Markdown export/import
```

---

## Phase 4: Plugins & Polish (Week 4-5)

### Goals
- Complete plugin system
- Marketplace browsing
- Polish & animations

### Tasks
- [ ] **Plugin System**
  - Python `@skill` decorator
  - JSON manifest loader
  - WASM loader (Wasmtime, no sandbox)
  - Dependency resolution (pip, semver)

- [ ] **CLI Plugin Commands**
  - `ele plugin create/test/package/install/update/list/disable/enable/config/publish`
  - Marketplace browse: search + list
  - Create wizard: Python, JSON, WASM templates

- [ ] **Marketplace**
  - Cloud API (current plan)
  - Trust registry (no signature verification yet)
  - Auto-update on startup

- [ ] **Polish**
  - All animations (sidebar, mode switch, message appear, Ellie 60 FPS)
  - Theme system: 10+ built-in + custom builder with live preview
  - Keyboard shortcuts complete
  - Accessibility: WCAG AA (live regions, focus management)
  - Crash reports: local only
  - Structured JSON logging + file rotation + per-module levels

### Deliverables
```
cli/src/
  plugins/
    loader.py           # Python/JSON/WASM
    marketplace.py      # Browse, install, update
    commands.py         # CLI commands
    templates/          # Python, JSON, WASM scaffolds

backend/app/plugins/
  loader.py             # Backend plugin loader
  registry.py           # Plugin registry
  marketplace.py        # Marketplace API
```

---

## Phase 5: Web/Desktop/Telegram (Week 5+)

### Goals
- Expand to other interfaces
- Shared backend

### Web (Next.js)
- [ ] Chat page: WebSocket + SSE (notifications)
- [ ] PWA: manifest + service worker, offline cache
- [ ] Auth: Skip initially, add Supabase later
- [ ] Dashboard, Marketplace, Settings pages

### Desktop (Electron + React)
- [ ] Frameless window with custom titlebar
- [ ] Window state persistence (position, size, maximized)
- [ ] electron-updater + GitHub Releases (signed)
- [ ] System tray: full menu (sessions, plugins, etc.)
- [ ] Native notifications
- [ ] Auto-update

### Telegram Bot
- [ ] Webhook mode (production)
- [ ] Single user (owner only)
- [ ] Custom commands (user-defined)
- [ ] File upload/download support
- [ ] PC pop-up overlay on desktop

### Deliverables
```
web/
  src/app/
    chat/page.tsx       # WS + SSE
    layout.tsx          # PWA manifest
    dashboard/page.tsx

desktop/
  src/main/             # Electron main
  src/preload/          # IPC bridge
  src/renderer/         # React app

backend/app/routes/
  telegram.py           # Webhook endpoint
```

---

## Dependency Graph

```
Phase 1 (Foundation)
    │
    ├── Config System ◄──────────────────────────────────────┐
    ├── WebSocket API ◄──────────────────────────────────────┤
    ├── Agent Core ◄─────────────────────────────────────────┤
    ├── Executors ◄──────────────────────────────────────────┤
    ├── Memory ◄─────────────────────────────────────────────┤
    └── CLI Chat Mode ◄──────────────────────────────────────┤
                                                             │
Phase 2 (Autonomous + Voice) ────────────────────────────────┤
    ├── Autonomous UI ◄──────────────────────────────────────┤
    ├── Ellie Avatar ◄───────────────────────────────────────┤
    ├── Voice Pipeline ◄─────────────────────────────────────┤
    └── Tools Integration ◄──────────────────────────────────┤
                                                             │
Phase 3 (Memory & RAG) ──────────────────────────────────────┤
    ├── RAG Hybrid Search ◄──────────────────────────────────┤
    ├── Cross-References ◄───────────────────────────────────┤
    ├── Episodic Dedup ◄─────────────────────────────────────┤
    └── Session Export ◄─────────────────────────────────────┤
                                                             │
Phase 4 (Plugins) ───────────────────────────────────────────┤
    ├── Plugin System ◄──────────────────────────────────────┤
    ├── Marketplace ◄────────────────────────────────────────┤
    └── Polish ◄─────────────────────────────────────────────┤
                                                             │
Phase 5 (Other Interfaces) ──────────────────────────────────┘
    ├── Web ◄────────────────────────────────────────────────┤
    ├── Desktop ◄────────────────────────────────────────────┤
    └── Telegram ◄───────────────────────────────────────────┘
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Voice latency | Streaming TTS, VAD optimization, local-first |
| Memory performance | Embedding cache, incremental FAISS, async ops |
| Plugin security | Trust registry, no sandbox for now, WASM isolated |
| Cross-platform audio | sounddevice (PortAudio) works on Win/Mac/Linux |
| Terminal compatibility | Braille fallback, image upgrade only for Kitty/iTerm2/WezTerm |
| Backend startup time | Lazy-load, target < 2s |
| Config complexity | Pydantic validation, hot-reload, good defaults |

---

## Success Criteria

### Phase 1 Complete When:
- [ ] `ele` launches Chat Mode in < 2s
- [ ] Backend auto-starts, WebSocket connects
- [ ] Chat with thought streaming works
- [ ] First-run wizard completes all settings
- [ ] All 5 API keys can be configured and tested
- [ ] Themes switch instantly (hot-reload)

### Phase 2 Complete When:
- [ ] Space+e toggles to Autonomous mode
- [ ] Ellie avatar animates at 60 FPS
- [ ] Continuous voice conversation works (interrupt handling)
- [ ] All tools work in autonomous mode
- [ ] Coqui voice clone speaks with user's voice
- [ ] Click Ellie returns to chat mode

### Phase 3 Complete When:
- [ ] RAG finds relevant code across files
- [ ] Cross-references work (imports → definitions)
- [ ] Sessions export to readable Markdown
- [ ] Memory rebuild completes in < 10s

### Phase 4 Complete When:
- [ ] `ele plugin create/install/test` works
- [ ] Marketplace browse + install works
- [ ] Custom plugins load and execute
- [ ] Animations smooth, accessibility passes

### Phase 5 Complete When:
- [ ] Web dashboard works (chat, settings, marketplace)
- [ ] Desktop app builds, auto-updates, system tray works
- [ ] Telegram bot responds to commands and files