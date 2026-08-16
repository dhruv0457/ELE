# Architecture Decisions & Tradeoffs Log

## Decision Format
| Date | Decision | Choice | Rationale | Alternatives Considered |

---

## Core Architecture

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | Backend architecture | Keep FastAPI + WebSocket | Multi-interface ready, existing 3000+ lines of agent/memory/RAG/plugin/executor code, production patterns (auth, rate limiting, credits) |
| 2026-08-14 | CLI-Backend communication | WebSocket (not direct calls) | Separation of concerns, enables remote backend, matches existing code, WebSocket streaming for real-time |
| 2026-08-14 | Config format | TOML | Python standard (pyproject.toml), readable, supports comments, good tooling |
| 2026-08-14 | Config priority | Defaults → Config file → Env vars → CLI flags | Standard precedence, env for secrets, CLI for overrides |
| 2026-08-14 | Secrets encryption | Age + hardware KDF (TPM/Windows Hello) | Modern, simple, hardware-bound = no master password needed, secure |
| 2026-08-14 | Config validation | Pydantic schema-based | Catch errors early, type safety, automatic parsing |
| 2026-08-14 | Hot reload | Yes, watch config file | Instant theme/setting changes without restart |

---

## Interface Strategy

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | Primary interface | CLI/TUI (Textual) first | Personal use, terminal-native, best for automation |
| 2026-08-14 | Secondary interfaces | Web → Desktop → Telegram | Progressive enhancement, shared backend |
| 2026-08-14 | CLI framework | Textual | Layouts, widgets, CSS styling, animations, mouse support, async |
| 2026-08-14 | Keyboard shortcuts | Vim-style (Space leader) | Power-user efficient, familiar to developers |
| 2026-08-14 | Mouse support | Full (click, scroll, sidebar, buttons) | Accessibility, discoverability, hybrid workflow |

---

## Two-Mode CLI Design

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | Chat Mode | Traditional conversational UI | Familiar, good for Q&A, push-to-talk voice |
| 2026-08-14 | Autonomous Mode | Full-screen agent execution | "Ellie runs commands by herself" - visible automation |
| 2026-08-14 | Mode toggle | Space+e (300ms animation) | Vim-style, smooth transition |
| 2026-08-14 | Ellie avatar | Braille animation (Textual Canvas) | Works in ALL terminals, 60 FPS, no dependencies |
| 2026-08-14 | Ellie design | Abstract geometric | Clean, distinctive, scalable to image sprites |
| 2026-08-14 | Image upgrade | Detect Kitty/iTerm2/WezTerm | Best of both: braille universal, images where supported |
| 2026-08-14 | Ellie click area | Full avatar + label | Easy to click, accessible |
| 2026-08-14 | Ellie idle animation | Subtle pulse | Alive but not distracting |
| 2026-08-14 | Execution stream | Verbose (every command, output, timing, exit code) | Full visibility for debugging/learning |
| 2026-08-14 | Command highlighting | Full shell syntax | Readability |
| 2026-08-14 | Progress display | All: spinner + elapsed + progress bar + live tail | Complete picture |
| 2026-08-14 | Conversation panel | Bottom 40% | Text sync for voice, independent scroll |
| 2026-08-14 | Voice interrupt | Stop TTS, start STT immediately | Natural conversation flow |
| 2026-08-14 | Multi-task | Parallel tool chains | Efficiency for independent tasks |

---

## Voice Architecture

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | Voice engines | Hybrid: Online + Offline with auto-fallback | Maximum efficiency in both cases, privacy when needed |
| 2026-08-14 | Online STT | Whisper API | Best accuracy, multi-language, no local model |
| 2026-08-14 | Offline STT | Vosk Medium (1.8 GB) | Good accuracy, real-time on CPU, decent model size |
| 2026-08-14 | Online TTS | Edge-TTS (streaming) | Free, 400+ voices, natural prosody, chunked playback |
| 2026-08-14 | Offline TTS primary | Coqui TTS (with voice cloning) | High quality, 30s sample → custom voice |
| 2026-08-14 | Offline TTS fallback | pyttsx3 | Zero deps, always works, ultimate fallback |
| 2026-08-14 | VAD Engine | Silero VAD (ONNX) | Best accuracy, noise robustness, ONNX = no PyTorch at runtime |
| 2026-08-14 | Listening mode | Always-on VAD (Autonomous) + Push-to-talk (Chat) | Natural for autonomous, controlled for chat |
| 2026-08-14 | Wake word | Porcupine "Hey Ellie" | Hardware-accelerated, low false positive |
| 2026-08-14 | Audio I/O | sounddevice (PortAudio) | Cross-platform, async-friendly, low latency |
| 2026-08-14 | Streaming TTS | Yes, chunked playback | Lower perceived latency |
| 2026-08-14 | Coqui voice cloning | Yes, 30s freestyle sample | Personalized Ellie voice |
| 2026-08-14 | Online/offline check | On-demand (before each voice request) | Simple, no background polling |

---

## LLM & Agent

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | LLM providers | External APIs only: Gemini, Groq, NVIDIA, Claude, GPT | User explicitly wants external, no local LLMs |
| 2026-08-14 | Parallel LLM count | Auto: use all available keys | Maximize quality/diversity |
| 2026-08-14 | Tool calling format | Unified abstraction (adapters per provider) | Single interface, provider-specific optimization |
| 2026-08-14 | Merge strategy | Heuristic: longest/best | Fast, no extra LLM call, good enough |
| 2026-08-14 | Agent framework | LangGraph | Stateful, streaming, checkpointing, production-ready |
| 2026-08-14 | Checkpointer | SqliteSaver | Persistent, no extra deps, survives restart |
| 2026-08-14 | Rate limiting | Per-IP (before auth) | Protects unauthenticated endpoints |
| 2026-08-14 | WS Auth | JWT in cookie (HttpOnly) | Secure, works with browser |

---

## Tools & Executors

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | File sandbox | Home directory (~), full access | Maximum flexibility for personal use |
| 2026-08-14 | Shell safety | Confirm all, no allow/denylist | Simple, secure, user decides each time |
| 2026-08-14 | Browser library | Both Playwright + Selenium (configurable) | Flexibility, stealth mode via Playwright |
| 2026-08-14 | Browser mode | Visible option (can watch) | Debugging, learning |
| 2026-08-14 | Browser stealth | Yes, playwright-stealth | Avoid bot detection |
| 2026-08-14 | Shell output | Full ANSI support | Colors, formatting preserved |
| 2026-08-14 | Shell history | Both: arrow keys + searchable panel | Familiar + powerful |
| 2026-08-14 | Shell pager | Built-in TUI pager | Integrated experience |
| 2026-08-14 | Terminal emulator | Yes (pty + xterm.js in TUI) | Interactive commands (vim, python REPL) |
| 2026-08-14 | Diff view | Both side-by-side + unified (toggle) | Flexibility |
| 2026-08-14 | File tree | Full IDE-like (git status, search, drag-drop) | Productivity |
| 2026-08-14 | Hidden files | Toggle (Ctrl+h) | Clean by default, accessible |
| 2026-08-14 | Editor auto-save | Yes, instant on focus loss | Never lose changes |
| 2026-08-14 | Code editor | Textual TextArea | Built-in, no external deps |
| 2026-08-14 | Browser screenshots | Both: auto on nav + on demand | Complete visibility |

---

## Memory & RAG

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | Memory layers | 4-layer: short, long (FAISS), episodic, project | Proven architecture, different retention needs |
| 2026-08-14 | Short-term buffer | Dynamic: fit in token budget | Optimal context usage |
| 2026-08-14 | Long-term vector store | FAISS + BGE-small (384-dim) | Fast, local, good quality for code+text |
| 2026-08-14 | Episodic storage | SQLite, forever retention, dedup | Complete history, semantic dedup |
| 2026-08-14 | Episodic dedup | Yes, embed + cluster (threshold 0.95) | Avoid redundant memories |
| 2026-08-14 | Project memory | File watcher + marker files | Real-time context |
| 2026-08-14 | RAG chunking | Fixed 512 tokens | Simple, consistent |
| 2026-08-14 | Hybrid search | FAISS + BM25 with RRF | Best of semantic + keyword |
| 2026-08-14 | Cross-references | Yes, parse imports/links | Graph-aware retrieval for code |
| 2026-08-14 | FAISS rebuild trigger | On session start | Predictable, batch |
| 2026-08-14 | Session export | Markdown (human readable) | Shareable, portable |
| 2026-08-14 | Metadata DB | SQLite | Standard, built-in, sufficient |

---

## Plugin System

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | Plugin formats | Python @skill, JSON manifest, WASM | Flexibility, security progression |
| 2026-08-14 | WASM sandbox | No sandbox (trusted only) | Simpler for personal use |
| 2026-08-14 | Plugin signing | No, trust registry | Simpler |
| 2026-08-14 | Marketplace | Cloud (current plan) | Centralized, discoverable |
| 2026-08-14 | Plugin updates | On startup | Fresh plugins |
| 2026-08-14 | Community plugins | Unrestricted | Personal use, user decides |
| 2026-08-14 | Dependency resolution | pip (standard) | Compatible, user familiar |
| 2026-08-14 | Version constraints | Semver (^1.0.0) | Standard, flexible |

---

## Other Interfaces

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | Telegram mode | Webhook (production) | Real-time |
| 2026-08-14 | Telegram users | Single user (owner only) | Personal bot |
| 2026-08-14 | Telegram files | Yes, send/receive | Full support |
| 2026-08-14 | Desktop updater | electron-updater + GitHub Releases | Standard, signed |
| 2026-08-14 | System tray | Full menu (sessions, plugins, etc.) | Complete control |
| 2026-08-14 | Desktop window | Frameless + custom titlebar | Modern, integrated |
| 2026-08-14 | Window state | Persist position/size/maximized | Consistent UX |
| 2026-08-14 | Web realtime | WS (chat) + SSE (notifications) | Best of both |
| 2026-08-14 | Web auth | Skip initially | MVP focus |
| 2026-08-14 | Web PWA | Yes, manifest + SW | Installable |
| 2026-08-14 | Web offline | Yes, cache static assets | Partial offline |

---

## Quality & Operations

| Date | Decision | Choice | Rationale |
|------|----------|--------|-----------|
| 2026-08-14 | Startup time target | < 2 seconds | Fast, lazy-load heavy components |
| 2026-08-14 | Auto backend start | Yes, spawn uvicorn subprocess | Seamless single command |
| 2026-08-14 | Themes | All 10+ from Textual gallery + custom builder | Variety + personalization |
| 2026-08-14 | Theme preview | Preview pane | See before confirm |
| 2026-08-14 | Accessibility | Full WCAG AA (live regions, focus mgmt) | Inclusive |
| 2026-08-14 | Multi-language | English only (v1) | Simpler, i18n-ready structure |
| 2026-08-14 | Crash reports | Local only | Privacy |
| 2026-08-14 | Logging | Structured JSON + file rotation + per-module | Production-ready |
| 2026-08-14 | Test framework | pytest (backend), vitest (web) | Standard choices |
| 2026-08-14 | CI trigger | Push + PR | Catch issues early |
| 2026-08-14 | Release versioning | Semver (1.0.0) | Standard |
| 2026-08-14 | Doc generation | Yes (pdoc/sphinx) | Always current |

---

## Tradeoffs Summary

### What We Gained
- **Unified backend** for all interfaces
- **Hybrid voice** working online/offline seamlessly
- **Two-mode CLI** for both chat and autonomous automation
- **Local-first** with cloud-ready architecture
- **Extensible plugin system** with three formats
- **Production patterns** from day one

### What We Deferred
- Supabase/cloud sync (local-only MVP)
- Plugin signature verification (trust registry)
- Web authentication (skip initially)
- WASM sandboxing (trusted only)
- Multi-language (English v1)
- Local LLMs (external APIs only)

### Key Risks Accepted
- **Porcupine access key** needed for wake word (free tier available)
- **Vosk 1.8 GB** download required for offline STT
- **Coqui models** 1-2 GB for offline TTS
- **sounddevice** PortAudio dependency (usually works out of box)
- **Terminal image support** only in Kitty/iTerm2/WezTerm (braille fallback universal)