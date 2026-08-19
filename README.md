# ELE Agent - Unified AI Desktop Assistant

A production-ready AI assistant that runs locally with a beautiful terminal interface (TUI) and supports multiple interfaces (CLI, Web, Desktop).

## Features

- **Terminal Chat (TUI)** - Professional text-based interface with live streaming
- **Multi-LLM Support** - NVIDIA, OpenAI, Anthropic, Google Gemini, Groq, Ollama
- **Automation Tools** - File operations, shell commands, app launching
- **Memory** - 4-layer system (short-term, FAISS vector, episodic, project)
- **RAG** - FAISS + BM25 hybrid search
- **Plugins** - Python, JSON, WASM support
- **Themes** - 10+ built-in themes
- **Vim-style keys** - Space leader keybindings

## Quick Start

### One-Command Install (Windows)

```powershell
# Run in PowerShell as Administrator
irm https://raw.githubusercontent.com/your-username/ele-agent/main/install.py | python
```

Then restart terminal and run:
```powershell
ele
```

### Manual Install

```bash
git clone https://github.com/your-username/ele-agent.git
cd ele-agent
python install.py
```

Then restart terminal and run:
```bash
ele
```

## Configuration

1. Copy `backend/.env.example` to `backend/.env`
2. Add your API keys:
   ```env
   NVIDIA_API_KEY=your-key-here
   # OPENAI_API_KEY=
   # GEMINI_API_KEY=
   # GROQ_API_KEY=
   # ANTHROPIC_API_KEY=
   ```

## Usage

### Terminal Chat (TUI) - Main Interface
```bash
ele
```
- Type messages and press Enter
- `Space` + `e` - Toggle autonomous mode
- `Space` + `s` - Settings
- `Space` + `p` - Plugins
- `Space` + `t` - Theme selector
- `Space` + `n` - New session
- `Esc` - Exit mode

### Web Dashboard
```bash
cd web && npm run dev
# Open http://localhost:3000
```

### Desktop App
```bash
cd desktop && npm run dev
```

## Architecture

```
ele-agent/
├── backend/          # FastAPI + LangGraph agent
│   ├── app/
│   │   ├── agents/   # LangGraph orchestration
│   │   ├── rag/      # FAISS + BM25 hybrid search
│   │   ├── memory/   # 4-layer memory system
│   │   ├── executors/# File, shell, app tools
│   │   ├── plugins/  # Plugin loader
│   │   ├── auth/     # JWT middleware
│   │   └── routes/   # API routes
├── cli/              # Textual TUI
├── web/              # Next.js dashboard
├── desktop/          # Electron + React
├── extensions/       # Built-in plugins
└── docs/             # Documentation
```

## Requirements

- Windows 10/11 (primary), Linux, macOS
- Python 3.11+ (auto-installed via Miniconda)
- NVIDIA API key (free at https://build.nvidia.com)

## License

MIT License