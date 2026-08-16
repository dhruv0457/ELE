# ELE Agent - Unified AI Desktop Assistant

A personal AI assistant that runs locally with a beautiful terminal interface (TUI) and supports multiple interfaces (CLI, Web, Desktop, Telegram).

## Features

- **Two-Mode CLI**: Chat mode for conversation, Autonomous mode for hands-free automation
- **Ellie Avatar**: Animated braille character with 60 FPS animations
- **Hybrid Voice**: Online (Whisper + Edge-TTS) + Offline (Vosk + Coqui + pyttsx3)
- **Tools**: File operations, shell commands, browser automation, app launching
- **Memory**: 4-layer system (short-term, long-term FAISS, episodic, project)
- **Plugins**: Python skills, JSON manifests, WASM modules
- **Themes**: 10+ built-in themes + custom theme builder
- **Vim-style keys**: Space leader keybindings

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+ (for web/desktop)
- Porcupine access key (for wake word)
- Vosk model (for offline STT)

### Installation

```bash
# Clone repo
git clone https://github.com/dhruv0457/ELE.git
cd ELE

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# CLI
cd ../cli
pip install -r requirements.txt

# Install CLI globally
pip install -e .
```

### Configuration

1. Get Porcupine access key from [Picovoice Console](https://console.picovoice.ai/)
2. Download Vosk model: `wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip`
3. Run first-time setup:
```bash
ele
```

### Running

```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: CLI
ele
```

## Keyboard Shortcuts (Vim-style)

| Shortcut | Action |
|----------|--------|
| `Space` | Leader key |
| `Space e` | Toggle Ellie/Autonomous mode |
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

## Architecture

```
ele-agent/
├── backend/          # FastAPI + LangGraph agent
│   ├── app/
│   │   ├── agents/   # LangGraph orchestration
│   │   ├── rag/      # FAISS + BM25 hybrid search
│   │   ├── memory/   # 4-layer memory system
│   │   ├── executors/# File, shell, browser tools
│   │   ├── plugins/  # Plugin loader (Python/JSON/WASM)
│   │   └── voice/    # STT/TTS manager
│   └── pyproject.toml
├── cli/              # Textual TUI
│   ├── src/
│   │   ├── app.py    # Main app
│   │   ├── screens/  # Chat, Autonomous, Settings, Plugins, Tools
│   │   └── widgets/  # Ellie avatar, message bubbles, status bar
│   └── pyproject.toml
├── web/              # Next.js dashboard
├── desktop/          # Electron + React
└── docs/             # Documentation
```

## Voice Setup

### Porcupine Wake Word
1. Sign up at [Picovoice Console](https://console.picovoice.ai/)
2. Create "Hey Ellie" keyword
3. Download `.ppn` file for your platform
4. Add `PORCUPINE_ACCESS_KEY` to `.env`

### Vosk Offline STT
```bash
mkdir -p ~/.ele-agent/voice/vosk-model
cd ~/.ele-agent/voice/vosk-model
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
```

### Coqui Voice Cloning
```bash
# Record 30s freestyle sample
# Save as ~/.ele-agent/voice/cloned/my_voice.wav
```

### Silero VAD ONNX
```bash
python -c "
import torch
model, _ = torch.hub.load('snakers4/silero-vad', 'silero_vad')
torch.onnx.export(model, torch.randn(1, 512), 'silero_vad.onnx', opset_version=13)
"
```

## Project Structure

```
temporary_docs/          # Design documentation
├── PROJECT_OVERVIEW.md
├── ARCHITECTURE_DECISIONS.md
├── CLI_DESIGN.md
├── CONFIG_SPEC.md
├── API_KEY_MANAGEMENT.md
├── PLUGIN_SYSTEM.md
├── VOICE_INTEGRATION.md
├── ELLIE_AUTONOMOUS_MODE.md
├── HYBRID_VOICE_ARCHITECTURE.md
├── MEMORY_RAG_DESIGN.md
├── PHASE_PLAN.md
└── QUESTIONS_LOG.md
```

## License

MIT License - see LICENSE for details.