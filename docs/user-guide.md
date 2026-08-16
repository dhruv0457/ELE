# ELE Agent User Guide

## Quick Start

### 1. Download & Install
- **Windows**: Download `ELE-Agent-Setup.exe` from [releases](https://github.com/yourusername/ele-agent/releases)
- Run installer → Click through setup wizard

### 2. Onboarding Wizard (First Launch)
```
┌─────────────────────────────────────┐
│         Welcome to ELE!             │
├─────────────────────────────────────┤
│  ☐ I agree to the privacy policy    │
│                                     │
│  [Continue]                         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         API Keys (Optional)         │
├─────────────────────────────────────┤
│  You can use your own keys (free)   │
│  or use platform credits.           │
│                                     │
│  OpenAI:    [__________________]    │
│  Gemini:    [__________________]    │
│  OpenClaw:  [__________________]    │
│                                     │
│  [Skip - Use Platform Credits]      │
│  [Continue]                         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         Permissions                 │
├─────────────────────────────────────┤
│  ELE needs access to:               │
│  ☑ File system (read/write)         │
│  ☑ Launch applications              │
│  ☑ Browser automation               │
│  ☑ Shell commands                   │
│  ☑ Microphone (voice)               │
│  ☑ Notifications                    │
│                                     │
│  [Grant Permissions]                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         Telegram (Optional)         │
├─────────────────────────────────────┤
│  Control your PC from your phone!   │
│                                     │
│  1. Open Telegram                   │
│  2. Search @ele_agent_bot           │
│  3. Send /start                     │
│  4. Enter the code shown here:      │
│     [________]                      │
│                                     │
│  [Skip]                    [Verify] │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         You're Ready!               │
├─────────────────────────────────────┤
│  Say "Hey ELE" or click the mic     │
│  Try: "Open Chrome and go to GitHub"│
│                                     │
│  [Start Using ELE]                  │
└─────────────────────────────────────┘
```

---

## Interfaces

### Desktop App (Main)
- **System Tray**: Right-click → Open, Pause, Quit
- **Main Window**: Chat history, settings, marketplace, plugins
- **Overlay**: Top-center pop-up shows "Listening...", "Thinking...", "Working..."
- **Hotkey**: `Ctrl+Shift+E` to open/focus

### Web Dashboard
- Visit `https://app.ele-agent.dev`
- Sign in with Google or email
- **Chat**: Full conversation with streaming thoughts
- **Settings**: API keys, preferences, billing
- **Marketplace**: Browse/install plugins
- **Plugins**: Manage installed plugins

### CLI/TUI
```bash
# Install
pip install ele-agent-cli

# Run
ele

# Commands
ele chat "Create a Python script"
ele --model gemini "Explain this code"
ele --voice "Open Notepad"
ele plugin install github.com/user/skill
```

**TUI Layout**:
```
┌────────────────────────────────────────┐
│ ELE  ● Online  ◆ Auto  ▲ 3/10 credits  │  ← Top bar
├────────────────────────────────────────┤
│                                        │
│  > Create a REST API in FastAPI       │  ← Your input
│                                        │
│  ◉ Thinking: Planning API structure   │  ← Live thoughts
│  ◉ Tool: file.write (main.py)         │
│  ◉ Tool: shell.run (uvicorn main:app) │
│                                        │
│  ✓ Done! API running at localhost:8000│  ← Final response
├────────────────────────────────────────┤
│ [Input...]                    /help    │  ← Bottom bar
└────────────────────────────────────────┘
```

### Telegram Bot
1. Open Telegram → Search `@ele_agent_bot`
2. Send `/start`
3. Chat naturally: "Take a screenshot and send it to me"
4. **PC Pop-up**: Overlay appears on your desktop showing activity
5. **Commands**:
   - `/status` — System status
   - `/pause` — Pause agent
   - `/resume` — Resume agent
   - `/settings` — Quick settings

---

## Voice Commands

### Wake Word
- Say **"Hey ELE"** → Overlay shows "Listening..."
- Speak your command → "Thinking..." → "Working..." → Done!

### Supported Voices
| Voice | Engine | Online/Offline | Notes |
|-------|--------|----------------|-------|
| ELE (British Male) | Edge-TTS | Online | Default, high quality |
| System Default | pyttsx3 | Offline | Fast, robotic |
| Cloned (Your Voice) | Coqui | Offline | Requires 30s sample |

### Voice Settings
- **Settings → Voice** → Choose engine, voice, speed, volume
- **Wake Word Sensitivity**: Low / Medium / High (battery impact)

---

## Plugin Marketplace

### Browse & Install
1. Open **Marketplace** tab (Desktop/Web)
2. Search or browse categories: Coding, Productivity, Automation, Fun
3. Click plugin → View details, ratings, screenshots
4. **Install** → Auto-downloads, installs, enables

### Manage Plugins
- **Plugins tab**: Enable/disable, configure, uninstall
- **Updates**: Auto-check on startup, notify in marketplace

### Create Your Own
```bash
# Scaffold
ele plugin create my-skill --template python

# Structure created:
my-skill/
├── skill.json          # Manifest
├── main.py             # @skill class
├── requirements.txt    # Dependencies
├── README.md
└── tests/
```

**skill.json**:
```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "Does amazing things",
  "author": "You",
  "entry_point": "main:MySkill",
  "permissions": ["file:read", "file:write", "shell:run"],
  "config_schema": {
    "api_key": {"type": "string", "secret": true}
  }
}
```

**main.py**:
```python
from ele_sdk import skill, SkillContext

@skill(name="my-skill", description="Does amazing things")
class MySkill:
    async def execute(self, ctx: SkillContext, task: str) -> str:
        # Your logic here
        await ctx.tools.file.write("output.txt", f"Result: {task}")
        return "Done!"
```

### Publish to Marketplace
1. `ele plugin package my-skill` → creates `.ele-plugin`
2. Web Dashboard → Marketplace → Publish
3. Fill details, upload package, submit for review
4. Once approved → visible to all users

---

## Settings

### General
- **Language**: English (v1)
- **Theme**: Light / Dark / System
- **Auto-update**: On / Off
- **Telemetry**: Full / Errors Only / None

### API Keys (BYOK)
- Add your own: OpenAI, Gemini, OpenClaw, Anthropic, etc.
- **Priority**: Your keys used first → Platform credits as fallback
- **Usage**: Shows credits consumed per provider

### Permissions
| Permission | Description | Required For |
|------------|-------------|--------------|
| File System | Read/write/delete files | Coding, documents, automation |
| App Launch | Open/close applications | "Open Chrome", "Launch VS Code" |
| Browser | Web automation, scraping | Research, form filling, testing |
| Shell | Run commands, scripts | Dev tools, system admin |
| Microphone | Voice input | "Hey ELE", voice commands |
| Notifications | Desktop alerts | Task completion, confirmations |
| Email | Send/read email | "Email John the report" |
| Calendar | Manage events | "Schedule meeting tomorrow" |

### Privacy
- **Local Data**: Never leaves your device (conversations, FAISS index, files)
- **Cloud Data**: Only account info + cloud conversations (web/Telegram)
- **Export**: Settings → Privacy → Export All Data
- **Delete**: Settings → Privacy → Delete Account (irreversible)

---

## Troubleshooting

### "Hey ELE" not working
1. Check microphone permission (Windows Settings → Privacy → Microphone)
2. Check wake word enabled: Settings → Voice → Wake Word
3. Try lower sensitivity (High → Medium)
4. Restart app: System Tray → Quit → Reopen

### Agent slow / times out
1. Check internet (cloud LLMs need connectivity)
2. Enable local fallback: Settings → Models → Local Fallback
3. Reduce parallel LLMs: Settings → Models → Max Parallel (2)
4. Check credits: Dashboard → Billing

### Plugin not working
1. Check enabled: Plugins tab → toggle on
2. Check permissions: Plugin details → Permissions
3. View logs: Settings → Advanced → Plugin Logs
4. Reinstall: Uninstall → Install again

### Desktop app won't start
1. Run as Administrator once (for permissions)
2. Check antivirus (add exception for install folder)
3. Reinstall: Download latest .exe from releases
4. Check logs: `%APPDATA%\ele-agent\logs\`

### Telegram bot not responding
1. Check bot status: `/status` in Telegram
2. Verify webhook: Settings → Telegram → Test Connection
3. Check whitelist: Your Telegram ID in web dashboard
4. Restart backend: `sudo systemctl restart ele-api` (server)

---

## Keyboard Shortcuts (Desktop)

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+E` | Open/focus main window |
| `Ctrl+Shift+V` | Toggle voice listening |
| `Ctrl+Shift+P` | Pause/resume agent |
| `Ctrl+Shift+M` | Open marketplace |
| `Ctrl+Shift+S` | Open settings |
| `Escape` | Close overlay / cancel |
| `Ctrl+K` | Command palette (plugins, settings, actions) |

---

## FAQ

**Q: Is my data private?**
A: Yes. Local conversations, files, and vector index never leave your device. Only cloud conversations (web/Telegram) and account metadata are stored on Supabase. You can export/delete anytime.

**Q: Can I use it completely offline?**
A: Yes! Local LLM (Ollama), local embeddings, Vosk STT, pyttsx3 TTS, file ops, app launch, shell all work offline. Browser, email, calendar, cloud LLMs need internet.

**Q: How do platform credits work?**
A: Free tier: 100 credits/day. Each LLM call = 1 credit. BYOK (your API keys) = unlimited, no credits used. Pro/Team tiers get more credits.

**Q: Can I run multiple instances?**
A: One per user profile. Multi-user on same PC: each Windows user gets their own install with separate data.

**Q: How do I update?**
A: Auto-update checks on startup. Manual: Download latest .exe from GitHub Releases.

**Q: Can I contribute plugins?**
A: Yes! Open marketplace, community ratings. See `plugin-guide.md` for development.

---

## Support

- **Documentation**: https://docs.ele-agent.dev
- **Email**: support@ele-agent.dev
- **GitHub Issues**: https://github.com/yourusername/ele-agent/issues
- **Discord**: https://discord.gg/ele-agent (community)