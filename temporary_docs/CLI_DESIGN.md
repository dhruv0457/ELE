# CLI Design Specification

## Chat Mode Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ELE Agent                                    [🎤]  [⚙]  [☐]  [□]  [✕]       │  ← Title bar (custom, frameless)
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │                                                              │
│  💬 Chat     │  ┌──────────────────────────────────────────────────────┐   │
│  📋 Sessions │  │  🤖  I'll help you create that API.                  │   │
│  🔧 Tools    │  │  ◉ Thinking: Planning FastAPI structure              │   │
│  🔌 Plugins  │  │  ◉ Tool: file.write (main.py)                        │   │
│  ⚙ Settings  │  │  ✓ Done! Running at http://localhost:8000          │   │
│              │  │                                                      │   │
│  ─────────── │  │  ┌────────────────────────────────────────────────┐  │   │
│  👤 Profile  │  │  │  👤  Create a REST API for todos               │  │   │
│  ☁ Sync      │  │  └────────────────────────────────────────────────┘  │   │
│              │  └──────────────────────────────────────────────────────┘   │
│              │  ┌──────────────────────────────────────────────────────┐   │
│              │  │  [🎤]  Type or speak...                    [Send]    │   │
│              │  └──────────────────────────────────────────────────────┘   │
│              │                                                              │
├──────────────┴──────────────────────────────────────────────────────────────┤
│  ● Online  ◆ Auto (Gemini)  ▲ 3/10 credits  🔋 100%  🎤 On  10:30 AM       │  ← Status bar
└─────────────────────────────────────────────────────────────────────────────┘
```

### Sidebar (Collapsible, 240px → 60px)
- **Navigation items**: Chat, Sessions, Tools, Plugins, Settings
- **Icons only when collapsed**, labels on hover/expand
- **Session tabs** at top when in Sessions view
- **Profile/Sync** at bottom

### Chat Area
- **Message bubbles** with rich metadata:
  - Avatar (user: 👤, assistant: 🤖)
  - Timestamp (right-aligned)
  - Tool badges (pill-style, colored)
  - Thought stream toggle (chevron down/up)
  - Copy button (hover)
  - Full syntax highlighting for code blocks
- **Inline thought expansion**: Click message → expands thought stream below
- **Tabbed sessions**: Multiple concurrent sessions as tabs

### Input Bar
- **Textarea**: Multi-line, Shift+Enter for newline, Enter to send
- **Voice button**: 🎤 toggles push-to-talk
- **Send button**: Primary action
- **Status indicator**: Right side shows Ellie state

---

## Autonomous Mode Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              🤖 Ellie ◉ Listening...                        │  ← Ellie avatar (top-center, 60 FPS braille)
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ EXECUTION STREAM ──────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ▶  $ cd ~/projects/my-api                                         │   │
│  │  ▶  $ ls -la                                                       │   │
│  │     total 24                                                       │   │
│  │     drwxr-xr-x  user  staff   512 Aug 14 10:00 .                  │   │
│  │     -rw-r--r--  user  staff  1024 Aug 14 10:00 main.py            │   │
│  │                                                                     │   │
│  │  ▶  $ cat main.py                                                  │   │
│  │     from fastapi import FastAPI                                    │   │
│  │     app = FastAPI()                                                │   │
│  │     ...                                                            │   │
│  │                                                                     │   │
│  │  ◉ Thinking: Need to add CORS middleware                          │   │
│  │  ▶  $ cat > main.py << 'EOF'                                      │   │
│  │     from fastapi import FastAPI                                    │   │
│  │     from fastapi.middleware.cors import CORSMiddleware            │   │
│  │     app = FastAPI()                                                │   │
│  │     app.add_middleware(CORSMiddleware, ...)                       │   │
│  │     ...                                                            │   │
│  │     EOF                                                            │   │
│  │                                                                     │   │
│  │  ▶  $ uvicorn main:app --reload                                    │   │
│  │     INFO: Started server process [12345]                          │   │
│  │     INFO: Uvicorn running on http://127.0.0.1:8000                │   │
│  │                                                                     │   │
│  │  ✓ Done! API running at http://localhost:8000                    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─ CONVERSATION PANEL (40% height) ──────────────────────────────────┐   │
│  │                                                                     │   │
│  │  👤  "Go to github.com and check trending Python repos"           │   │
│  │                                                                     │   │
│  │  🤖 Ellie: "I'll check GitHub trending for Python repos..."       │   │
│  │  ◉ Navigating to github.com/trending/python                       │   │
│  │  ◉ Extracting repository names and descriptions                   │   │
│  │                                                                     │   │
│  │  🤖 Ellie: "Here are the top 5 trending Python repos:"            │   │
│  │  1. **astral-sh/ruff** - An extremely fast Python linter          │   │
│  │  2. **pydantic/pydantic** - Data validation using Python types    │   │
│  │  3. **langchain-ai/langchain** - Building LLM applications        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Ellie Avatar (Top-Center)
- **Braille animation** using Textual Canvas widget
- **60 FPS** smooth animations
- **States**: Idle (pulse), Listening (waveform), Thinking (spinner), Working (progress), Speaking (equalizer), Error (shake)
- **Click area**: Full avatar + label text
- **Image upgrade**: Sprite sheet in Kitty/iTerm2/WezTerm

### Execution Stream (Top 60%)
- **Verbose output**: Every command, args, stdout, stderr, exit code, timing
- **Syntax highlighting**: Full shell syntax (commands, args, pipes, redirections)
- **Progress display**: Spinner + elapsed + progress bar + live tail (last N lines)
- **Tool calls**: Highlighted with 🔧 icon
- **Thoughts**: Prefixed with ◉

### Conversation Panel (Bottom 40%)
- **Text sync**: Everything spoken shown as text
- **User speech**: STT results with 👤
- **Ellie speech**: TTS output with 🤖
- **Agent thoughts**: ◉ prefixed
- **Scrollable**: Independent scroll from execution stream

---

## Tools Panel (Tools Sidebar Item)

### File Tree (Full IDE-like)
```
📁 my-project
├── 📁 .git
│   ├── 📄 config
│   └── 📄 HEAD
├── 📁 src
│   ├── 📄 main.py          ● (modified)
│   ├── 📄 models.py        ● (staged)
│   └── 📄 utils.py
├── 📁 tests
│   ├── 📄 test_main.py
│   └── 📄 test_models.py
├── 📄 pyproject.toml
├── 📄 README.md
└── 📄 .env                 🚫 (gitignored)
```
- **Git status icons**: ● modified, ● staged, + untracked, 🚫 ignored
- **Branch display**: `main ↑2 ↓1` on hover
- **Diff on hover**: Unified diff preview
- **Search**: Ctrl+f filters tree
- **Drag-drop**: Move files/folders
- **Hidden files**: Toggle with Ctrl+h

### Code Editor (Textual TextArea)
- **Syntax highlighting**: Full language support
- **Line numbers**: Toggleable
- **Auto-save**: Instant on focus loss
- **Tabs**: Multiple files as tabs
- **Find/Replace**: Ctrl+f / Ctrl+h

### Shell Panel
- **Built-in pager**: Scrollable output panel
- **History**: Arrow keys + searchable panel (Space+?)
- **ANSI colors**: Full support
- **Interactive commands**: pty + xterm.js for vim, python REPL, etc.

### Browser Panel
- **Visible option**: Watch browser work (configurable)
- **Stealth mode**: playwright-stealth for bot detection avoidance
- **Screenshots**: Auto on navigation + on demand
- **Console logs**: Capture and display

---

## Plugins Panel

### Marketplace Browser
- **Search bar**: Text search with debounce
- **Categories**: Coding, Productivity, Automation, Fun
- **List view**: Name, description, rating, installs, version
- **Install button**: One-click install
- **Details**: Click for manifest, permissions, screenshots

### Plugin Manager
- **Installed list**: Enable/disable toggle, configure, uninstall
- **Updates**: Badge on Plugins nav item
- **Create wizard**: Python skill, JSON manifest, WASM templates

---

## Settings Panel (Tabbed)

### General
- Theme selector (preview pane)
- Language (English only v1)
- Auto-update, start minimized, telemetry

### Voice
- Wake word toggle + sensitivity
- STT engine (auto/whisper/vosk)
- TTS voice/engine/speed/volume
- Voice test: record + playback

### API Keys
- All 5 providers in one screen
- Masked display, test button, remove
- Platform credits display

### Tools
- Per-tool toggles (all enabled by default)
- Confirmations: file write/delete, shell, browser, email
- Shell: confirm all (no allowlist)

### Plugins
- Auto-update on startup
- Community plugins: unrestricted
- Marketplace endpoint (configurable)

### Privacy
- Crash reports: local only
- Export all data (Markdown)
- Delete account

---

## Animations & Transitions

| Interaction | Duration | Easing |
|-------------|----------|--------|
| Sidebar collapse/expand | 200ms | ease-out |
| Mode switch (Chat ↔ Autonomous) | 300ms | ease-out-cubic |
| Message appear | 150ms | ease-out |
| Thought stream expand | 200ms | ease-out |
| Ellie avatar frame | 16.67ms (60 FPS) | linear |
| Toast/sidebar badge | 200ms | ease-out |
| Theme switch | 100ms | ease-out |
| Tab switch | 100ms | ease-out |

---

## Color Themes (10+ Built-in)

All themes from Textual gallery:
1. **Tokyo Night** (dark, purple/blue accents)
2. **Catppuccin Mocha** (dark, warm)
3. **Dracula** (dark, purple/green)
4. **Gruvbox** (dark, earth tones)
5. **Nord** (dark, arctic)
6. **Solarized Dark** (dark, blue/yellow)
7. **One Dark** (dark, Atom-style)
8. **Monokai** (dark, vibrant)
9. **GitHub Dark** (dark, GitHub)
9. **Custom** (user-created)

Each theme defines:
- Primary/secondary/accent colors
- Background layers (primary, secondary, surface)
- Text colors (primary, secondary, muted)
- Border, shadow, selection
- Syntax highlighting palette

---

## Keyboard Shortcuts (Vim-style, Space Leader)

| Shortcut | Action | Context |
|----------|--------|---------|
| `Space` | Leader key | Global |
| `Space e` | Toggle Ellie/Autonomous | Global |
| `Space v` | Toggle voice listening | Chat |
| `Space q` | Quit / Exit autonomous | Autonomous |
| `Space h` | Command palette | Global |
| `Space s` | Save session | Global |
| `Space n` | New session | Chat |
| `Space t` | Theme selector | Global |
| `Space p` | Plugin manager | Global |
| `Space /` | Search messages | Chat |
| `Space ?` | Shell history panel | Tools |
| `j/k` | Navigate up/down | Lists |
| `Ctrl+d/u` | Half-page scroll | Panels |
| `gg/G` | Top/Bottom | Panels |
| `Ctrl+h` | Toggle hidden files | File Tree |
| `Ctrl+f` | Find in panel | Editor/Tree |
| `Escape` | Close modal/cancel | Modals |
| `Enter` | Confirm/activate | Buttons |
| `Tab` | Next focusable | Forms |

---

## Mouse Interactions

- **Click message**: Select, show copy button
- **Double-click message**: Expand thoughts
- **Click sidebar item**: Navigate
- **Click Ellie avatar**: Exit autonomous mode
- **Scroll**: Mouse wheel in any scrollable panel
- **Drag**: File tree drag-drop, splitter resize
- **Right-click**: Context menus (future)

---

## Responsive Behavior

| Terminal Width | Layout |
|----------------|--------|
| ≥ 140px | Full layout (sidebar + chat) |
| 100-139px | Collapsed sidebar (icons only) |
| < 100px | Sidebar overlay (hamburger menu) |

---

## Accessibility (WCAG AA)

- **Live regions**: For streaming thoughts, Ellie speech
- **Focus management**: Visible focus rings, logical tab order
- **ARIA labels**: All interactive elements
- **Contrast**: 4.5:1 minimum (enforced by themes)
- **Keyboard-only**: Full operation without mouse
- **Screen reader**: Semantic HTML/Textual roles
- **Reduced motion**: Respects `prefers-reduced-motion`