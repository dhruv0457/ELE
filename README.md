# ELE Agent - Unified AI Desktop Assistant

A personal AI assistant that runs locally with a beautiful terminal interface (TUI) and supports multiple interfaces (CLI, Web, Desktop, Telegram).

## Features

- **Two-Mode CLI**: Chat mode for conversation, Autonomous mode for hands-free automation
- **Ellie Avatar**: Animated braille character with live animations
- **Hybrid Voice**: Online (Whisper + Edge-TTS) + Offline (Vosk + Coqui + pyttsx3)
- **Tools**: File operations, shell commands, browser automation, app launching
- **Memory**: 4-layer system (short-term, long-term FAISS, episodic, project)
- **Plugins**: Python skills, JSON manifests, WASM modules
- **Multi-LLM**: Gemini, Groq, NVIDIA NIM, Claude, OpenAI, Ollama (auto-orchestration)
- **Streaming Chat**: WebSocket streaming with live thoughts / tool results
- **Themes**: 10+ built-in themes + custom theme builder
- **Vim-style keys**: Space leader keybindings

## Quick Test (local, in 2 commands)

The fastest way to see it work. Uses the bundled `ele-agent` conda environment (no manual installs).

### 1. Start the backend (one terminal)

```powershell
cd D:\ELE\backend
E:\ANACONDA\condabin\conda.bat run -n ele-agent python -m uvicorn app.main:app --host localhost --port 8000
```

You should see `Uvicorn running on http://localhost:8000`.

### 2. Run the CLI TUI (second terminal)

```powershell
cd D:\ELE\cli
E:\ANACONDA\condabin\conda.bat run -n ele-agent python -m src.app
```

That's it — the TUI opens, auto-connects to the backend, and you can type messages. By default it runs in **demo mode** (no API key) which still streams thoughts/tools and can execute file/shell tools.

> Tip: you can also run the pure-text REPL if the TUI doesn't render in your terminal:
> ```powershell
> E:\ANACONDA\condabin\conda.bat run -n ele-agent python -m src.repl
> ```

### Verify it works

- The chat screen shows `Backend: connected as ele@local.dev`
- Type `Hello!` and press Enter — you'll see streamed `thought` events then a `final` response
- Press `Space p` to open the Plugins screen, `Space` then `s` for Settings

---

## Complete Setup (all features)

### Prerequisites

- **Python 3.11+** (we use the `ele-agent` conda env at `E:\ANACONDA\envs\ele-agent`)
- **Node.js 20+** (for the web dashboard and desktop app)
- Optional: Porcupine access key (wake word), Vosk model (offline STT), Ollama (local LLM)

### Installation

```bash
git clone https://github.com/dhruv0457/ELE.git
cd ELE
```

#### Backend (Python)

Two options:

**Option A — use the conda env (easiest, already has all deps):**
```powershell
E:\ANACONDA\condabin\conda.bat create -n ele-agent python=3.11 -y
E:\ANACONDA\condabin\conda.bat run -n ele-agent pip install -r D:\ELE\backend\requirements.txt
```

**Option B — your own venv:**
```powershell
cd D:\ELE\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Note: `pyaudio` is commented out in `requirements.txt` on Windows because it needs Visual C++ Build Tools. Voice still works via `sounddevice`/`vosk`/`edge-tts`.

#### CLI (Python)

```powershell
cd D:\ELE\cli
E:\ANACONDA\condabin\conda.bat run -n ele-agent pip install -r requirements.txt
# Optional: install the `ele` entry-point globally
E:\ANACONDA\condabin\conda.bat run -n ele-agent pip install -e .
```

#### Web (Next.js)

```powershell
cd D:\ELE\web
npm install
```

#### Desktop (Electron + React)

```powershell
cd D:\ELE\desktop
npm install
```

### Configuration

All config lives in `~/.ele-agent/config.toml` (created automatically on first run). Secrets live in `D:\ELE\backend\.env`:

```env
# Copy D:\ELE\.env.example to D:\ELE\backend\.env and edit:
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROQ_API_KEY=gsk_...            # free, fast: https://console.groq.com/keys
NVIDIA_API_KEY=nvapi-...
ANTHROPIC_API_KEY=sk-ant-...
PORCUPINE_ACCESS_KEY=...
JWT_SECRET=change-me
DEBUG=True
```

To enable **real LLM responses** (instead of demo mode), set at least one provider key. Recommended free path:
1. Get a free Groq key at https://console.groq.com/keys
2. Add `GROQ_API_KEY=gsk_...` to `D:\ELE\backend\.env`
3. Restart the backend

Or run fully offline with Ollama:
```powershell
winget install Ollama.Ollama
ollama pull llama3.2:1b
ollama serve
```

### Running everything

**Start order: backend first, then the UIs.**

```powershell
# Terminal 1 - Backend
cd D:\ELE\backend
E:\ANACONDA\condabin\conda.bat run -n ele-agent python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - CLI TUI
cd D:\ELE\cli
E:\ANACONDA\condabin\conda.bat run -n ele-agent python -m src.app

# Terminal 3 - Web (http://localhost:3000)
cd D:\ELE\web
npm run dev

# Terminal 4 - Desktop app
cd D:\ELE\desktop
npm run dev
```

---

## CLI Features & Keyboard Shortcuts

The TUI has 5 screens shown below with Vim-style `Space` leader keybindings.

### Screens

| Screen | What it does | How to open |
|---|---|---|
| **Chat** | Stream responses from the backend (thoughts → tool calls → final answer) | default on launch |
| **Autonomous** | Hands-free voice pipeline (wake word → STT → agent → TTS) | `Space e` |
| **Settings** | Theme, backend port, default LLM, tools, voice engine | `Space s` |
| **Plugins** | Install / enable / remove plugins from the marketplace | `Space p` |
| **Tools** | File tree, shell, browser, app launcher panes | (Settings + custom keys) |

### Keybindings

| Shortcut | Action |
|---|---|
| `Space` | Leader key (then press the next key) |
| `Space e` | Toggle Ellie / Autonomous mode |
| `Space v` | Toggle voice listening |
| `Space q` | Quit / Exit autonomous |
| `Space h` | Command palette |
| `Space s` | Save session |
| `Space n` | New session |
| `Space t` | Theme selector |
| `Space p` | Plugin manager |
| `Space /` | Search messages |
| `Space ?` | Shell history |
| `Escape` | Exit mode / Cancel |
| `Ctrl+h` | Toggle hidden files |
| `Ctrl+d` / `Ctrl+u` | Half page down / up |

### Chat screen

- Bottom input bar — type and press Enter to send
- Responses stream live with `◉ thought` lines and `🔧 tool` outputs
- `On`/`Off` voice toggle, click `Send`

---

## Backend Features

### Multi-LLM orchestration (`/api/v1/ws/chat`)

The agent graph runs: `input → sanity_check → rag → llm_parallel → merge → action → response`. If no provider keys are set, it returns a helpful **demo-mode** response that still exercises the WS streaming protocol.

- WebSocket endpoint accepts `?token=<jwt>` or the `access_token` cookie
- Events: `thought`, `tool_start`, `tool_result`, `screenshot`, `progress`, `final`, `error`, `pong`

### REST API

| Method | Path | Description |
|---|---|---|
| GET  | `/health` | health check (no auth) |
| POST | `/api/v1/register` | create user (auto-creates missing) |
| POST | `/api/v1/login` | login, returns JWT (auto-creates on first call) |
| POST | `/api/v1/logout` | clear cookie |
| GET  | `/api/v1/me` | current user info |
| POST | `/api/v1/chat` | non-streaming chat |
| WS   | `/api/v1/ws/chat` | streaming chat |
| GET  | `/api/v1/plugins` | list installed plugins |

### Tools (executors)

`file` (read/write/list/patch/delete/stat), `shell` (run with timeout), `browser` (Playwright: navigate/click/type/extract/screenshot), `app_launch` (whitelisted).

### Memory (4 layers)

- **Short-term**: per-session deque with dynamic token budget
- **Long-term**: FAISS vector store + SQLite KV fallback
- **Episodic**: SQLite action/outcome log with embeddings
- **Project**: file-tree scan with marker files (`pyproject.toml`, `package.json`, ...)

### RAG

FAISS + BM25 hybrid search with Reciprocal Rank Fusion. Falls back to a deterministic hash embedder when `sentence-transformers` is offline (so it always works).

---

## Voice Setup

### Porcupine Wake Word
1. Sign up at [Picovoice Console](https://console.picovoice.ai/)
2. Create a "Hey Ellie" keyword and download the `.ppn` for your platform
3. Add `PORCUPINE_ACCESS_KEY` to `.env`

### Vosk Offline STT
```powershell
mkdir ~/.ele-agent/voice/vosk-model -Force
cd ~/.ele-agent/voice/vosk-model
Invoke-WebRequest https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip -OutFile model.zip
Expand-Archive model.zip
```

### TTS engines
`edge-tts` (online, no key), `pyttsx3` (system), `coqui` (cloned). Pick one in Settings → Voice.

---

## Plugins

Drop a plugin into `~/.ele-agent/plugins/<name>/` with a `manifest.json`:

```json
{
  "id": "my-skill",
  "name": "My Skill",
  "version": "1.0.0",
  "runtime": "python",
  "entry_point": "main:MySkill",
  "permissions": ["file"],
  "config_schema": {}
}
```

Plus `main.py` with a class that takes a config dict. Runtimes: `python`, `json`, `wasm`. Built-in plugins live under `D:\ELE\extensions\plugins\`.

---

## Architecture

```
ele-agent/
├── backend/          # FastAPI + LangGraph agent
│   ├── app/
│   │   ├── agents/    # LangGraph orchestration + LLM clients
│   │   ├── rag/       # FAISS + BM25 hybrid search
│   │   ├── memory/    # 4-layer memory system
│   │   ├── executors/ # File, shell, browser tools
│   │   ├── plugins/   # Plugin loader (Python/JSON/WASM)
│   │   ├── voice/     # STT/TTS manager
│   │   ├── auth/      # JWT middleware
│   │   ├── db/        # SQLAlchemy async (SQLite)
│   │   ├── config/    # Pydantic settings + TOML
│   │   └── routes/    # auth, chat, plugins, voice, settings, health
├── cli/              # Textual TUI
│   └── src/
│       ├── app.py     # main app + keybindings
│       ├── screens/   # chat, autonomous, settings, plugins, tools
│       ├── widgets/   # ellie avatar, message bubbles, status bar
│       ├── backend.py # WS client (auth + stream)
│       └── store.py   # central state
├── web/              # Next.js dashboard (Supabase auth)
├── desktop/          # Electron + React
└── docs/             # architecture.md, api.md, deployment.md, ...
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'app'`** — run uvicorn from inside `D:\ELE\backend`, not the repo root.

**CLI says "Backend: NOT running"** — start the backend first in another terminal.

**Login fails with `EmailStr` error** — the backend accepts any real-looking email. The CLI auto-uses `ele@example.com`.

**Chat returns "demo mode"** — no LLM API key set. Add a `GROQ_API_KEY` to `backend/.env` or run `ollama serve`, then restart the backend.

**`pyaudio` fails to install on Windows** — it needs Visual C++ Build Tools; we already commented it out. Voice still works via `sounddevice`.

**`TabbedContent`/CSS errors at startup** — make sure you're on the matching Textual version (`textual>=8.0` for this build).

---

## Development

```powershell
# Run the headless smoke test (verifies all screens mount + chat streams)
cd D:\ELE\cli
E:\ANACONDA\condabin\conda.bat run -n ele-agent python smoke_test.py

# Run the focused settings/plugins test
E:\ANACONDA\condabin\conda.bat run -n ele-agent python settings_test.py
```

## License

MIT License - see LICENSE for details.
