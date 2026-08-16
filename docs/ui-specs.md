# ELE Agent UI Specifications (Figma-Style)

## Design System

### Colors
```css
:root {
  /* Light Theme */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8F9FA;
  --bg-tertiary: #E9ECEF;
  --text-primary: #1A1A2E;
  --text-secondary: #4A4A68;
  --text-muted: #8888A0;
  --accent: #0066FF;
  --accent-hover: #0052CC;
  --accent-light: #E8F0FE;
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --border: #E0E0E8;
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
  
  /* Dark Theme */
  --bg-primary-dark: #0D0D1A;
  --bg-secondary-dark: #141428;
  --bg-tertiary-dark: #1E1E38;
  --text-primary-dark: #F0F0F8;
  --text-secondary-dark: #B0B0C8;
  --text-muted-dark: #707088;
  --border-dark: #2A2A44;
}
```

### Typography
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 2rem;      /* 32px */

--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
```

### Border Radius
```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-full: 9999px;
```

---

## Screen Specifications

### 1. Onboarding Wizard

#### Step 1: Welcome
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    🤖  ELE Agent                             │
│                                                             │
│              Your AI Desktop Assistant                      │
│                                                             │
│  ─────────────────────────────────────────                  │
│                                                             │
│  ☐ I accept the Privacy Policy & Terms of Service          │
│                                                             │
│                              [Continue →]                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
- Centered card, max-width 480px
- Animated robot icon (Lottie)
- Primary button disabled until checkbox checked

#### Step 2: API Keys
```
┌─────────────────────────────────────────────────────────────┐
│  ← Back                                    Step 2 of 4      │
│                                                             │
│                    API Keys (Optional)                      │
│              Use your own keys or platform credits          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ OpenAI API Key                                      │   │
│  │ [sk-************************]      👁  [Test]        │   │
│  │ Get key: platform.openai.com                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Google Gemini API Key                               │   │
│  │ [AI************************]        👁  [Test]        │   │
│  │ Get key: makersuite.google.com                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ OpenClaw API Key                                    │   │
│  │ [oc_************************]        👁  [Test]        │   │
│  │ Get key: openclaw.dev                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Skip - Use Platform Credits]         [Continue →]        │
└─────────────────────────────────────────────────────────────┘
```

#### Step 3: Permissions
```
┌─────────────────────────────────────────────────────────────┐
│  ← Back                                    Step 3 of 4      │
│                                                             │
│                    Permissions Required                     │
│              ELE needs these to work                        │
│                                                             │
│  ┌─☑─┐ 📁 File System      Read/write files & folders      │
│  ┌─☑─┐ 🚀 App Launch       Open/close applications         │
│  ┌─☑─┐ 🌐 Browser          Web automation & scraping       │
│  ┌─☑─┐ 💻 Shell            Run commands & scripts          │
│  ┌─☐─┐ 🎤 Microphone       Voice commands & wake word      │
│  ┌─☐─┐ 🔔 Notifications    Desktop alerts                  │
│                                                             │
│  [Grant All]                              [Continue →]      │
└─────────────────────────────────────────────────────────────┘
```

#### Step 4: Telegram
```
┌─────────────────────────────────────────────────────────────┐
│  ← Back                                    Step 4 of 4      │
│                                                             │
│                    Connect Telegram                         │
│              Control your PC from your phone                │
│                                                             │
│  1. Open Telegram → Search @ele_agent_bot                  │
│  2. Send /start                                             │
│  3. Enter the 6-digit code shown there:                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ]                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Skip]                              [Verify & Finish →]   │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. Desktop App - Main Window

```
┌────────────────────────────────────────────────────────────────────────┐
│  🤖 ELE Agent                    [Search...]  🔔  ⚙  ☐  □  ✕      │  ← Title bar
├──────────────┬─────────────────────────────────────────────────────────┤
│              │                                                         │
│  💬 Chat     │  ┌─────────────────────────────────────────────────┐   │
│  📊 Dashboard│  │  Welcome back! How can I help?                  │   │
│  🔌 Plugins  │  │                                                 │   │
│  🛒 Market   │  │  ┌─────────────────────────────────────────┐   │   │
│  ⚙ Settings  │  │  │  🤖  I'll help you create that API.     │   │   │
│              │  │  │  ◉ Thinking: Planning FastAPI structure  │   │   │
│  ─────────── │  │  │  ◉ Tool: file.write (main.py)            │   │   │
│  👤 Profile  │  │  │  ◉ Tool: shell.run (uvicorn main:app)    │   │   │
│  ☁ Sync      │  │  │  ✓ Done! Running at http://localhost:8000│  │   │
│              │  │  └─────────────────────────────────────────┘   │   │
│              │  │                                                 │   │
│              │  │  ┌─────────────────────────────────────────┐   │   │
│              │  │  │  👤  Create a REST API for todos        │   │   │
│              │  │  └─────────────────────────────────────────┘   │   │
│              │  └─────────────────────────────────────────────────┘   │
│              │  ┌─────────────────────────────────────────────────┐   │
│              │  │  [🎤]  Type or speak...              [Send]     │   │
│              │  └─────────────────────────────────────────────────┘   │
│              │                                                         │
├──────────────┴─────────────────────────────────────────────────────────┤
│  Status: ● Online  ◆ Auto (Gemini)  ▲ 3/10 credits  🔋 100%          │  ← Status bar
└────────────────────────────────────────────────────────────────────────┘
```

**Components**:
- **Sidebar** (240px): Navigation icons with labels on hover
- **Chat Area**: Message bubbles with avatar, timestamp, tool badges
- **Thinking Stream**: Collapsible panel showing live agent thoughts
- **Input Bar**: Voice button, text input, send, model selector dropdown

---

### 3. Overlay Pop-up (Always on Top)

```
┌────────────────────────────────────┐
│  🤖  Listening...          ✕  ⛶  │  ← Top-center, 400px wide
├────────────────────────────────────┤
│  ████████░░░░░░░░░░░░░░░░  40%    │  ← Audio level meter
│                                    │
│  "Create a Python script..."      │  ← Transcribed text
└────────────────────────────────────┘
```

**States**:
| State | Icon | Text | Animation |
|-------|------|------|-----------|
| Idle | 🤖 | "Hey ELE" | Pulse |
| Listening | 🎤 | "Listening..." | Waveform |
| Processing | ⚙ | "Thinking..." | Spinner |
| Working | 🔨 | "Working..." | Progress bar |
| Speaking | 🔊 | "Speaking..." | Equalizer |
| Error | ⚠ | "Error: ..." | Shake |

**Position**: Top-center, 20px from top, z-index 9999
**Behavior**: Auto-hide after 3s of inactivity, click to pin

---

### 4. Web Dashboard - Chat Page

```
┌────────────────────────────────────────────────────────────────────┐
│  ELE Agent  [Dashboard ▼]  [Marketplace]  [Settings]  👤  ☐    │  ← Nav bar
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────┐  ┌──────────────────────────────┐ │
│  │        Chat                │  │    Thinking Stream (Live)    │ │
│  │  ┌──────────────────────┐  │  │  ┌────────────────────────┐  │ │
│  │  │ 🤖  I'll analyze...  │  │  │  │ ◉ Planning approach   │  │ │
│  │  │  ◉ Reading files...  │  │  │  │ ◉ Retrieving context  │  │ │
│  │  │  ◉ Running tests...  │  │  │  │ ◉ Generating code     │  │ │
│  │  │  ✓ All tests pass!   │  │  │  │ ✓ Complete            │  │ │
│  │  └──────────────────────┘  │  │  └────────────────────────┘  │ │
│  │                            │  │                              │ │
│  │  ┌──────────────────────┐  │  │  📸 Screenshot Preview      │ │
│  │  │ 👤  Fix the bug in   │  │  │  ┌────────────────────────┐  │ │
│  │  │    auth.py           │  │  │  │  [screenshot image]    │  │ │
│  │  └──────────────────────┘  │  │  └────────────────────────┘  │ │
│  │                            │  │                              │ │
│  │  ┌────────────────────┐    │  │  📊 Progress: ████████░░ 80%  │ │
│  │  │ [🎤] Message...   │    │  │                              │ │
│  │  └────────────────────┘    │  │  [Clear]  [Export]  [Pin]    │ │
│  └────────────────────────────┘  └──────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Responsive**:
- Desktop: Side-by-side (70/30)
- Tablet: Stacked, thinking stream collapsible
- Mobile: Chat only, thinking stream in drawer

---

### 5. Settings Panel

```
┌────────────────────────────────────────────────────────────────┐
│  Settings                                    [×]               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ General │ │  Voice  │ │ API Keys│ │Plugins │ │ Privacy │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
│       │           │           │           │           │        │
│  ────▼────────────────────────────────────────────────────▼──   │
│                                                                 │
│  GENERAL                                                         │
│  ────────                                                         │
│  Theme:        [Light ▼]  [Dark] [System]                        │
│  Language:     [English ▼]                                       │
│  Auto-update:  ☑ Enabled                                         │
│  Start minimized: ☐                                              │
│  Telemetry:    [Full ▼] [Errors Only] [None]                    │
│                                                                 │
│  VOICE                                                           │
│  ───────                                                         │
│  Wake Word:      ☑ Enabled    Sensitivity: [Medium ▼]           │
│  STT Engine:     [Whisper (Online) ▼] [Vosk (Offline)]          │
│  TTS Voice:      [Jarvis (Edge-TTS) ▼] [System] [Cloned]        │
│  Voice Speed:    ████████░░  1.0x                               │
│  Volume:         ██████████  100%                               │
│                                                                 │
│  API KEYS (BYOK)                                                 │
│  ─────────────                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ OpenAI          ••••••••••••••••  [Edit] [Test] [Remove] │   │
│  │ Gemini          ••••••••••••••••  [Edit] [Test] [Remove] │   │
│  │ OpenClaw        ••••••••••••••••  [Edit] [Test] [Remove] │   │
│  │ Anthropic       [Add Key]                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Platform Credits:  847 / 1000  [Upgrade]                       │
│                                                                 │
│  PLUGINS                                                         │
│  ───────                                                         │
│  ☑ Auto-update plugins                                           │
│  ☑ Allow community plugins                                       │
│  [Manage Installed]  [Browse Marketplace]                        │
│                                                                 │
│  PRIVACY                                                         │
│  ────────                                                         │
│  ☐ Share anonymous usage analytics                               │
│  ☐ Share crash reports                                           │
│  [Export All Data]  [Delete Account]                             │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### 6. Plugin Marketplace

```
┌────────────────────────────────────────────────────────────────┐
│  Marketplace                                    🔍  [Filters]  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Categories:  [All] [Coding] [Productivity] [Automation] [Fun] │
│  Sort:        [Trending ▼] [Newest] [Top Rated] [Most Installed]│
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🐍  Python Code Assistant                    ⭐ 4.9      │  │
│  │  Write, debug, refactor Python code with AI              │  │
│  │  by @ele-team  •  12.4k installs  •  v2.1.0             │  │
│  │  Permissions: file:read, file:write, shell:run          │  │
│  │  [Install]  [Details]  [★★★★★ 234 reviews]              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🌐  Web Scraper Pro                          ⭐ 4.7      │  │
│  │  Extract data from any website, export to CSV/JSON       │  │
│  │  by @datawizard  •  8.2k installs  •  v1.5.3            │  │
│  │  Permissions: browser:navigate, file:write              │  │
│  │  [Install]  [Details]  [★★★★☆ 156 reviews]              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [Load More]                                                   │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Plugin Detail Modal**:
```
┌────────────────────────────────────────────────────────────────┐
│  Python Code Assistant                              [×]        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⭐ 4.9 (234 reviews)    📦 12.4k installs    🏷 v2.1.0        │
│                                                                 │
│  Write, debug, refactor, and test Python code with AI          │
│  assistance. Supports FastAPI, Django, Flask, and more.        │
│                                                                 │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  Permissions Required:                                          │
│  ☑ File System (read/write)                                     │
│  ☑ Shell (run tests, lint)                                      │
│  ☐ Browser                                                      │
│  ☐ Network                                                      │
│                                                                 │
│  Configuration:                                                 │
│  • Default model: [Auto ▼]                                      │
│  • Auto-format on save: ☑                                       │
│  • Lint on type: ☐                                              │
│                                                                 │
│  Screenshots: [📷] [📷] [📷]                                    │
│                                                                 │
│  Version History:                                               │
│  v2.1.0 - Added Django support, fixed async bug                │
│  v2.0.0 - Major rewrite, new plugin API                         │
│                                                                 │
│  [Install]  [Uninstall]  [Report]                               │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### 7. CLI/TUI Layout

```
┌────────────────────────────────────────────────────────────────┐
│ ELE Agent  ● Online  ◆ Auto  ▲ 847/1000  🔋 100%  🎤 On    │  ← Header
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ Chat ──────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  👤  Create a FastAPI todo API                           │   │
│  │                                                           │   │
│  │  🤖  I'll create a complete todo API with FastAPI        │   │
│  │  ◉ Planning: REST endpoints, models, database            │   │
│  │  ◉ Tool: file.write (models.py)                          │   │
│  │  ◉ Tool: file.write (schemas.py)                         │   │
│  │  ◉ Tool: file.write (main.py)                            │   │
│  │  ◉ Tool: shell.run (pip install fastapi uvicorn)         │   │
│  │  ◉ Tool: shell.run (uvicorn main:app --reload)           │   │
│  │  ✓ Done! API running at http://localhost:8000/docs      │   │
│  │                                                           │   │
│  │  👤  Add authentication                                  │   │
│  │                                                           │   │
│  │  🤖  Adding JWT authentication...                        │   │
│  │  ◉ Tool: file.write (auth.py)                            │   │
│  │  ◉ Tool: file.patch (main.py)                            │   │
│  │  ✓ Authentication added!                                 │   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│  [🎤]  > Type command or ask...                    /help  /plugins│  ← Footer
└────────────────────────────────────────────────────────────────┘
```

**Slash Commands**:
```
/help              Show help
/model <name>      Switch model (auto/openai/gemini/local/openclaw)
/rag <on|off>      Toggle RAG
/skill <name>      Run specific skill
/plugin <cmd>      Plugin management
/clear             Clear chat history
/export            Export session
/settings          Open settings TUI
/voice             Toggle voice
```

---

### 8. Telegram Bot

**Chat View**:
```
┌─────────────────────────────────────┐
│  ELE Agent                    ⋮  │
├─────────────────────────────────────┤
│                                     │
│  🤖  I'll create that Python file  │
│  ◉ Writing main.py...              │
│  ◉ Installing dependencies...      │
│  ✓ Done!                           │
│                    10:30 AM         │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  👤  Add tests for it              │
│                    10:31 AM         │
│                                     │
│  🤖  Adding pytest tests...        │
│  ✓ Tests created and passing!      │
│                    10:32 AM         │
│                                     │
├─────────────────────────────────────┤
│  [🎤]  Message...          [Send]   │
└─────────────────────────────────────┘
```

**Commands Menu** (via `/`):
```
/start      - Welcome & setup
/chat       - Start chat mode
/status     - System status
/pause      - Pause agent
/resume     - Resume agent
/settings   - Quick settings
/help       - Command help
```

---

### 9. Mobile Web (Responsive)

**Breakpoints**:
- **Desktop**: ≥ 1024px — Full layout
- **Tablet**: 768-1023px — Collapsible sidebar, stacked chat/thinking
- **Mobile**: < 768px — Bottom nav, chat only, thinking in drawer

**Mobile Nav**:
```
┌─────────────────────┐
│  ☰  ELE  👤      │  ← Top bar
├─────────────────────┤
│                     │
│      Chat View      │
│                     │
├─────────────────────┤
│ 💬  📊  🔌  🛒  ⚙   │  ← Bottom tab bar
└─────────────────────┘
```

---

## Accessibility (WCAG AA)

- **Contrast**: 4.5:1 minimum for text, 3:1 for UI elements
- **Focus**: Visible focus rings on all interactive elements
- **Keyboard**: Full keyboard navigation (Tab, Enter, Escape, Arrows)
- **Screen Readers**: ARIA labels, roles, live regions for streaming
- **Motion**: `prefers-reduced-motion` respected
- **Zoom**: Functional at 200% zoom

## Animation Guidelines

| Interaction | Duration | Easing |
|-------------|----------|--------|
| Page transition | 200ms | ease-out |
| Modal open/close | 150ms | ease-out |
| Tooltip | 100ms | ease-out |
| Loading spinner | 1000ms | linear |
| Thinking stream | 50ms/line | none |
| Overlay appear | 200ms | ease-out-cubic |