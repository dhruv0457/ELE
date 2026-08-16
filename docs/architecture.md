# ELE Agent Architecture

## Overview

ELE (Enhanced Language Engine) is a unified AI desktop agent that combines multiple LLM providers (OpenAI, Google Gemini, Local LLMs, OpenClaw) into a single intelligent assistant capable of controlling your computer through voice, text, and programmatic interfaces.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACES                                   │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│   Web UI        │  Telegram Bot   │   CLI / TUI     │    Desktop App        │
│  (Next.js)      │  (Python)       │  (Textual)      │   (Electron + Rust)   │
└────────┬────────┴────────┬────────┴────────┬────────┴───────────┬────────────┘
         │                 │                 │                    │
         └─────────────────┴─────────────────┴────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │      API Gateway            │
                    │   (FastAPI on Rust)         │
                    │  Auth • Rate Limit • Proxy  │
                    └──────────────┬──────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
       ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
       │  ELE Core   │      │    RAG      │      │  Executors  │
       │  (Agent)    │      │  (FAISS)    │      │  (Tools)    │
       └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
              │                    │                    │
    ┌─────────┼─────────┐          │          ┌─────────┼─────────┐
    ▼         ▼         ▼          ▼          ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────────┐ ┌──────────────┐ ┌──────────────┐
│OpenAI │ │Gemini │ │Local  │ │OpenClaw   │ │File System   │ │Browser       │
│API    │ │API    │ │(Ollama)           │ │Operations    │ │Automation    │
└───────┘ └───────┘ └───────┘ └───────────┘ └──────────────┘ └──────────────┐
                                                                          │
                                                     ┌──────────────┐ ┌──────────────┐
                                                     │Shell/CMD     │ │Email/Calendar│
                                                     │Execution     │ │Tasks         │
                                                     └──────────────┘ └──────────────┘
```

## Core Components

### 1. ELE Core (`@ele/core`)

The brain of the agent. Implements:
- **Agent Loop**: Multi-turn conversation management with tool execution
- **Memory System**: Short-term, long-term (FAISS), episodic, and project memory
- **Plugin System**: Dynamic skill loading (Python decorators, JSON manifests, WASM)
- **Multi-LLM Orchestration**: Parallel execution across providers with smart merging

### 2. LLM Core (`@ele/llm-core`)

Unified interface for all LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Google Gemini (Pro, Flash)
- Local LLMs (via Ollama)
- OpenClaw providers
- Streaming, tool calling, structured output

### 3. Memory Core (`@ele/memory-core`)

Four-layer memory architecture:
- **Short-term**: Conversation buffer (last 20 turns)
- **Long-term**: FAISS vector store for facts/preferences
- **Episodic**: Action outcomes and lessons learned
- **Project**: Active project context (files, todos, deadlines)

### 4. Plugin SDK (`@ele/plugin-sdk`)

Three plugin formats:
- **Python Decorators**: `@skill` classes (native performance)
- **JSON Manifests**: Language-agnostic, versioned
- **WASM Modules**: Sandboxed, polyglot, secure

### 5. Executors (Tools)

| Tool | Implementation | Safety |
|------|----------------|--------|
| File Operations | `aiofiles` + `pathlib` | Confirm delete/write |
| App Launch | `subprocess` / `pyautogui` | Whitelist apps |
| Browser | Playwright (headless) | Confirm navigation |
| Shell | `asyncio.subprocess` | Confirm dangerous commands |
| Email | Gmail/Outlook OAuth | Confirm send |
| Calendar | Google/Outlook API | Confirm create/move |

### 6. Voice Stack

- **STT**: Whisper (online, high quality) / Vosk (offline, fast)
- **TTS**: Edge-TTS (Jarvis voice) / pyttsx3 (offline) / Coqui (cloning)
- **Wake Word**: Porcupine "Hey ELE" (always listening)

## Data Flow

### 1. User Command Processing
```
User Input → Interface Adapter → WebSocket/HTTP → API Gateway 
  → Auth Check → Rate Limit → ELE Core Agent
```

### 2. Agent Processing (LangGraph-style)
```
InputNode → SanityCheckNode → RAGNode (parallel) 
  → LLMNodes (PARALLEL: 4 LLMs) → MergeNode 
  → ActionNode → ResponseNode
```

### 3. Response Streaming
```
ResponseNode → WebSocket stream → Interface 
  → User sees: thinking stream + screenshots + progress + final answer
```

## Security Model

- **Secrets**: OS Keyring (Windows Credential Manager) + encrypted `.env`
- **Audit Log**: Append-only SQLite, immutable
- **Confirmation**: Risky actions (delete, send, pay) require explicit approval
- **Sandbox**: Electron `contextIsolation: true`, `nodeIntegration: false`
- **Code Signing**: Self-signed cert for .exe

## Deployment Topology

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Cloudflare     │     │   Oracle Cloud  │     │    Supabase     │
│  Pages (Web)    │────▶│  Free Tier      │────▶│  (PostgreSQL,   │
│  Static + Edge  │     │  (FastAPI,      │     │   Auth, Realtime)│
└─────────────────┘     │   Functions)    │     └─────────────────┘
                        └─────────────────┘
                                │
                        ┌───────┴───────┐
                        ▼               ▼
                 ┌──────────┐    ┌──────────┐
                 │ Telegram │    │  User    │
                 │ Webhook  │    │  Devices │
                 └──────────┘    │(Desktop/ │
                                 │ CLI)     │
                                 └──────────┘
```

## Offline Capability

| Component | Online | Offline |
|-----------|--------|---------|
| LLM | All 4 LLMs | Local Ollama only |
| RAG | Hybrid embeddings | Local FAISS + local embeddings |
| Voice | Whisper + Edge-TTS | Vosk + pyttsx3/Coqui |
| Executor | Browser, Email, Calendar | File, App, Shell, Local LLM |
| Memory | Supabase sync | Local SQLite + FAISS |