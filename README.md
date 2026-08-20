<div align="center">

# ⚡ ELE AGENT

**The Autonomous AI Developer & Desktop OS Copilot**

[![CI Status](https://img.shields.io/github/actions/workflow/status/dhruv/ele/ci.yml?branch=main&label=CI&style=flat-square)](https://github.com/dhruv/ele/actions)
[![Docker Image](https://img.shields.io/badge/Docker-Production%20Ready-blue?logo=docker&style=flat-square)](https://github.com/dhruv/ele/pkgs/container/backend)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&style=flat-square)](https://www.python.org/)
[![Node Version](https://img.shields.io/badge/Node.js-18%2B%20%7C%2020%2B-339933?logo=node.js&style=flat-square)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20LangGraph-009688?logo=fastapi&style=flat-square)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

*Direct PC Control • Speech-to-Speech Jarvis • 102+ NVIDIA NIM & Multi-Cloud Models • Visual AI Cursor Animation*

</div>

---

## 🌟 Key Capabilities

- **🎙️ Speech-to-Speech Jarvis Mode**: Voice assistant with real-time speech recognition, noise suppression, and neural voice synthesis (`en-GB-RyanNeural`).
- **🖥️ Full PC Automation & Ghost Cursor**: Visual AI cursor glide and click ripple across Windows applications (Office 365, Word, Excel, PowerPoint, VS Code, Chrome, Spotify, Telegram, and Settings).
- **🔀 102+ Model Catalog**: Interactive model selector (`/model`) with instant category filtering across NVIDIA NIM, Google Gemini, Groq Cloud (800 tok/s), OpenAI, Anthropic, and local air-gapped Ollama.
- **⚡ Prompt Queueing & Sticky Tasks (`/todo`)**: Queue commands while agent executes and monitor real-time step-by-step task breakdown cards.
- **🌐 Production Multi-Container Stack**: Dockerized FastAPI backend, Next.js web dashboard with Nginx reverse proxy, and Redis message broker.

---

## 🚀 Quick Start

### 1. Run Terminal AI Agent (Instant)
```bash
# Global terminal launcher
ele
```

### 2. Slash Commands Quick Reference

| Command | Action |
| :--- | :--- |
| `/jarvis` or `/voice` | Launch Speech-to-Speech Jarvis voice listening mode |
| `/model` | Open interactive popup model selector (102+ models) |
| `/automate <task>` | Execute autonomous desktop & web workflow |
| `/todo` | Toggle live sticky task breakdown card |
| `/new` | Start a clean, fresh conversation session |
| `/sessions` | Browse, load, or switch saved sessions |
| `/erase` | Reset & erase all data for a brand new user start |
| `/keys` | Inspect active API credentials |
| `/clear` | Clear terminal screen history |
| `/help` | View help and shortcut list |

---

## 🐳 Production Deployment (Docker)

Deploy the entire production stack (Backend API + Web Dashboard + Nginx + Redis) with a single command:

```bash
# 1. Clone repository
git clone https://github.com/dhruv/ele.git
cd ele

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys (NVIDIA_API_KEY, GEMINI_API_KEY, JWT_SECRET_KEY)

# 3. Launch production stack
./scripts/deploy.sh       # Linux / macOS
# Or on Windows:
.\scripts\deploy.ps1
```

### Services & Endpoints
- **Web Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🏗️ System Architecture

```
ELE AGENT ECOSYSTEM
├── cli/                 # Fast Terminal UI (Node.js & Python Textual)
│   ├── agy.js           # Core interactive HUD, Speech-to-Speech & Model Switcher
│   └── agent_overlay.ps1# Visual ghost cursor & desktop window automation
├── backend/             # FastAPI High-Performance Backend
│   ├── app/
│   │   ├── agents/      # LangGraph multi-agent orchestration
│   │   ├── executors/   # System, app, shell, and browser automation executors
│   │   ├── memory/      # 4-layer memory (vector, episodic, project, working)
│   │   ├── rag/         # Hybrid BM25 + FAISS search
│   │   └── routes/      # REST API & WebSocket streaming routes
│   └── Dockerfile       # Production multi-stage Docker build
├── web/                 # Next.js 14 Web Dashboard
│   ├── src/             # Real-time chat & agent monitoring UI
│   ├── nginx.conf       # High-performance Nginx reverse proxy
│   └── Dockerfile       # Production static export & runner
├── scripts/             # Deployment & verification scripts
│   ├── deploy.sh        # Linux deployment automation
│   ├── deploy.ps1       # Windows deployment automation
│   └── verify-production.py # Automated production readiness check
├── docs/                # Comprehensive system & deployment docs
│   └── deployment.md    # Production deployment guide
└── docker-compose.yml   # Production Compose configuration
```

---

## 🔒 Security & Best Practices

- **Zero Hardcoded Secrets**: All API tokens and credentials are loaded securely via `.env` or system keystore.
- **JWT Authentication & Rate Limiting**: Full token expiration and authentication middleware.
- **Unprivileged Container Execution**: Docker containers run under a non-root `eleagent` user.
- **Automated Healthchecks**: Built-in container healthchecks with automatic restart policies.

---

## 🧪 Production Verification

To verify that your installation is 100% production ready, run:
```bash
python scripts/verify-production.py
```

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.