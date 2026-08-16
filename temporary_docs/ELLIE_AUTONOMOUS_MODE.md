# Ellie Autonomous Mode - Final Design Specification

## Overview

The CLI has **two distinct modes** that the user switches between:

1. **Chat Mode** (Default) - Traditional conversational interface
2. **Autonomous Agent Mode** - Full-screen autonomous execution with Ellie avatar

---

## Mode 1: Chat Mode (Default)

### Layout
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ELE Agent                                    [🎤]  [⚙]  [☐]  [□]  [✕]       │  ← Custom titlebar (frameless)
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

### Key Elements
- **Sidebar** (collapsible, 240px→60px): Chat, Sessions, Tools, Plugins, Settings
- **Chat area**: Message bubbles with rich metadata (avatar, timestamp, tool badges, thought toggle, copy button)
- **Inline thought expansion**: Click message → expands thought stream below
- **Tabbed sessions**: Multiple concurrent sessions as tabs
- **Input bar**: Textarea + voice button + send
- **Status bar**: Connection, Model, Credits, Battery, Voice, Time
- **Command palette** (Space+h): All actions
- **Notifications**: Sidebar badges
- **Voice button** (🎤): Push-to-talk + wake word "Hey Ellie" (Porcupine)

---

## Mode 2: Autonomous Agent Mode

### Trigger
- Click **voice button (🎤)** in Chat Mode
- Hotkey: `Space+e` (Vim-style leader)

### Layout - Full Screen Takeover
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

#### Braille Animation (Primary - Universal)
Using Textual's **Canvas widget** with 2x4 braille dots (8 pixels per cell):
- **60 FPS** smooth animations
- Works in **ALL terminals** (no special support needed)
- **Abstract geometric design**: Clean shapes, particles, minimal - like a digital entity

| State | Braille Pattern | Description |
|-------|-----------------|-------------|
| **Idle** | ⠁⠂⠃⠄⠅⠆⠇⠈ | Subtle pulse (breathing) |
| **Listening** | ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ | Waveform bars |
| **Thinking** | ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ | Spinner |
| **Working** | ▱▰▰▰▰▱▱▱ | Progress bar segments |
| **Speaking** | ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ | Equalizer bars |
| **Error** | ⠿⠿⠿ | Shake + red tint |

#### Image Upgrade (Kitty/iTerm2/WezTerm)
- **Sprite sheet** with Ellie frames
- Automatic detection via terminal capabilities
- Seamless upgrade from braille
- Higher visual fidelity

#### Click Behavior
- **Click area**: Full avatar + label text
- **Action**: Exit autonomous mode → return to Chat Mode
- **Animation**: 300ms ease-out-cubic transition

---

## Voice Integration in Autonomous Mode

### Audio Pipeline
```
Microphone (16kHz mono, 32ms chunks)
       │
       ▼
┌──────────────────┐
│   sounddevice    │  ← PortAudio, async InputStream callback
│   InputStream    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Silero VAD     │  ← ONNX Runtime, streaming
│   (streaming)    │
└────────┬─────────┘
         │ Speech segment detected (500ms silence timeout)
         ▼
┌──────────────────┐
│  Voice Manager   │  ← Auto-selects STT engine
│  (STT)           │
└────────┬─────────┘
         │ Transcribed text
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
                    INTERRUPT HANDLING
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────────┐
    │  Is TTS currently playing?          │
    ├──────────────────────────────────────┤
    │  YES → Stop TTS immediately         │
    │       Start STT on this chunk       │
    │  NO  → Normal STT processing        │
    └──────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│   Agent Core     │  ← Process command, execute tools
│   (LangGraph)    │
└────────┬─────────┘
         │ Response text
         ▼
┌──────────────────┐
│  Voice Manager   │  ← Auto-selects TTS engine
│  (TTS streaming) │
└────────┬─────────┘
         │ Audio chunks (streaming)
         ▼
┌──────────────────┐
│   sounddevice    │  ← OutputStream, non-blocking
│   OutputStream   │
└──────────────────┘
         │
         ▼
   Ellie speaks + conversation panel updates
```

### STT Engine Priority
1. **Whisper API** (online) - Best accuracy, multi-language
2. **Vosk Medium** (offline) - 1.8 GB model, real-time on CPU

### TTS Engine Priority
1. **Edge-TTS** (online, streaming) - Free, 400+ voices, chunked playback
2. **Coqui TTS** (offline, cloned voice) - 30s sample → custom voice
3. **pyttsx3** (offline, system) - Ultimate fallback, zero deps

### Continuous Listening (VAD)
- **Always-on** in Autonomous Mode
- **Silero VAD** (ONNX) for speech detection
- **500ms silence timeout** = end of utterance
- **No wake word needed** (VAD replaces it)
- **Interruptible**: User speaks during TTS → immediate stop, start STT

---

## Text Sync Panel (Conversation Panel - Bottom 40%)

### Content
- **User speech**: STT results with 👤 prefix
- **Ellie speech**: TTS output with 🤖 prefix (streaming as chunks arrive)
- **Agent thoughts**: ◉ prefixed (thinking process)
- **Tool calls**: 🔧 prefixed
- **Results**: ✓/✗ prefixed

### Features
- **Independent scroll** from execution stream
- **Searchable** (Space+/ in chat mode)
- **Markdown rendering** for code blocks
- **Auto-scroll** on new content (toggleable)

---

## Mode Switching Flow

```
┌─────────────┐     Space+e / Click 🎤      ┌──────────────────┐
│  CHAT MODE  │ ──────────────────────────▶  │ AUTONOMOUS MODE  │
│             │                              │                  │
│ • Sidebar   │                              │ • Full-screen    │
│ • Messages  │ ◀──────────────────────────  │ • Ellie avatar   │
│ • Input bar │     Click Ellie / Escape     │ • Execution      │
│ • Status    │                              │ • Conversation   │
└─────────────┘                              └──────────────────┘
```

### Transition Animation (300ms ease-out-cubic)
1. **Chat → Autonomous**: 
   - Sidebar slides left (fade out)
   - Chat area expands to full screen
   - Ellie fades in at top-center (scale 0→1)
   - Execution stream + conversation panel fade in

2. **Autonomous → Chat**:
   - Ellie fades out (scale 1→0)
   - Sidebar slides in from left
   - Chat area restores
   - Execution stream + conversation panel fade out

### State Preservation
- **Scroll position** maintained
- **Conversation history** shared
- **Session state** continuous
- **Active tools** complete gracefully

---

## Technical Implementation (Textual)

### App Structure
```python
# cli/src/app.py
class ELEApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "ELE Agent"
    
    BINDINGS = [
        ("space", "leader", "Leader"),
        ("space,e", "toggle_autonomous", "Toggle Ellie"),
        ("space,v", "toggle_voice", "Voice"),
        ("space,q", "quit_autonomous", "Quit Autonomous"),
        ("space,h", "command_palette", "Commands"),
        ("space,s", "save_session", "Save"),
        ("space,n", "new_session", "New Session"),
        ("space,t", "theme_selector", "Theme"),
        ("space,p", "plugin_manager", "Plugins"),
        ("space,/", "search_messages", "Search"),
        ("space,?", "shell_history", "Shell History"),
        ("escape", "exit_autonomous", "Exit Autonomous"),
        ("ctrl+h", "toggle_hidden", "Hidden Files"),
    ]
    
    def __init__(self):
        super().__init__()
        self.mode = "chat"  # "chat" or "autonomous"
        self.voice_manager = VoiceManager()
        self.backend = BackendClient()
    
    def compose(self):
        yield Header(show_clock=True)
        yield ChatMode(id="chat_mode", classes="mode-panel")
        yield AutonomousMode(id="autonomous_mode", classes="mode-panel hidden")
        yield Footer()
    
    def action_toggle_autonomous(self):
        chat = self.query_one("#chat_mode")
        auto = self.query_one("#autonomous_mode")
        
        # Animate transition
        chat.styles.animate("opacity", 1.0, 0.0, duration=300, easing="ease-out")
        auto.styles.animate("opacity", 0.0, 1.0, duration=300, easing="ease-out")
        
        # Toggle visibility after animation
        self.set_timer(0.3, lambda: self._complete_mode_switch(chat, auto))
    
    def _complete_mode_switch(self, chat, auto):
        chat.display = not chat.display
        auto.display = not auto.display
        self.mode = "autonomous" if auto.display else "chat"
        
        if auto.display:
            auto.start_voice_pipeline()
        else:
            auto.stop_voice_pipeline()
    
    def action_exit_autonomous(self):
        if self.mode == "autonomous":
            self.action_toggle_autonomous()
```

### Ellie Avatar Widget
```python
# cli/src/widgets/ellie_avatar.py
class EllieAvatar(Static):
    """Animated Ellie avatar using braille(Canvas) - 60 FPS"""
    
    FRAMES = {
        "idle": [
            "⠁  Ellie", "⠂  Ellie", "⠃  Ellie", "⠄  Ellie",
            "⠅  Ellie", "⠆  Ellie", "⠇  Ellie", "⠈  Ellie",
        ],
        "listening": [
            "▁  Ellie", "▂  Ellie", "▃  Ellie", "▄  Ellie",
            "▅  Ellie", "▆  Ellie", "▇  Ellie", "█  Ellie",
            "▇  Ellie", "▆  Ellie", "▅  Ellie", "▄  Ellie",
            "▃  Ellie", "▂  Ellie",
        ],
        "thinking": [
            "⠋  Ellie", "⠙  Ellie", "⠹  Ellie", "⠸  Ellie",
            "⠼  Ellie", "⠴  Ellie", "⠦  Ellie", "⠧  Ellie",
            "⠇  Ellie", "⠏  Ellie",
        ],
        "working": [
            "▱  Ellie", "▰  Ellie", "▰▱  Ellie", "▰▰  Ellie",
            "▰▰▱  Ellie", "▰▰▰  Ellie", "▰▰▰▱  Ellie", "▰▰▰▰  Ellie",
        ],
        "speaking": [
            "▁  Ellie", "▂  Ellie", "▃  Ellie", "▄  Ellie",
            "▅  Ellie", "▆  Ellie", "▇  Ellie", "█  Ellie",
            "▇  Ellie", "▆  Ellie", "▅  Ellie", "▄  Ellie",
            "▃  Ellie", "▂  Ellie",
        ],
        "error": [
            "⠿  Ellie", "⠿  Ellie", "⠿  Ellie",
        ],
    }
    
    def __init__(self):
        super().__init__()
        self.state = "idle"
        self.frame_index = 0
        self.animation_task = None
        self.can_render_images = self._check_image_support()
    
    def _check_image_support(self) -> bool:
        """Detect Kitty/iTerm2/WezTerm for image support"""
        term = os.environ.get("TERM", "")
        term_program = os.environ.get("TERM_PROGRAM", "")
        return "kitty" in term or term_program == "iTerm.app" or "wezterm" in term
    
    def set_state(self, state: str):
        self.state = state
        self.frame_index = 0
        self.start_animation()
    
    def start_animation(self):
        if self.animation_task:
            self.animation_task.cancel()
        # 60 FPS = 16.67ms per frame
        self.animation_task = self.set_interval(1/60, self.animate)
    
    def animate(self):
        frames = self.FRAMES.get(self.state, ["🤖  Ellie"])
        self.frame_index = (self.frame_index + 1) % len(frames)
        self.update(frames[self.frame_index])
    
    def on_click(self, event):
        """Click Ellie to exit autonomous mode"""
        self.app.action_exit_autonomous()
```

### Autonomous Mode Screen
```python
# cli/src/screens/autonomous.py
class AutonomousMode(Container):
    """Full-screen autonomous agent view"""
    
    def compose(self):
        yield EllieAvatar(id="ellie")
        yield ExecutionStream(id="execution")
        yield ConversationPanel(id="conversation")
    
    def on_mount(self):
        self.query_one("#ellie").set_state("listening")
        self.start_voice_pipeline()
    
    def start_voice_pipeline(self):
        """Start the continuous voice pipeline"""
        self.voice_task = asyncio.create_task(self._voice_loop())
    
    def stop_voice_pipeline(self):
        if self.voice_task:
            self.voice_task.cancel()
    
    async def _voice_loop(self):
        """Main voice processing loop"""
        async with sounddevice.InputStream(
            samplerate=16000,
            channels=1,
            dtype='int16',
            blocksize=512,  # 32ms at 16kHz
            callback=self._audio_callback
        ) as stream:
            await self._process_voice_stream()
    
    async def _process_voice_stream(self):
        """Process audio through VAD → STT → Agent → TTS"""
        vad = SileroVAD()
        audio_buffer = bytearray()
        
        async for chunk in self.audio_queue:
            if vad.is_speech(chunk):
                audio_buffer.extend(chunk)
            elif audio_buffer:
                # End of utterance
                audio_data = bytes(audio_buffer)
                audio_buffer = bytearray()
                
                # STT
                self.query_one("#ellie").set_state("thinking")
                result = await self.voice_manager.transcribe(audio_data)
                
                if result.text:
                    # Add to conversation
                    self.query_one("#conversation").add_user_message(result.text)
                    
                    # Process through agent
                    async for event in self.backend.stream_agent(result.text):
                        await self._handle_agent_event(event)
    
    async def _handle_agent_event(self, event):
        ellie = self.query_one("#ellie")
        execution = self.query_one("#execution")
        conversation = self.query_one("#conversation")
        
        if event.type == "thought":
            execution.add_thought(event.content)
            conversation.add_thought(event.content)
            ellie.set_state("thinking")
        
        elif event.type == "tool_start":
            execution.add_tool_call(event.tool, event.args)
            ellie.set_state("working")
        
        elif event.type == "tool_result":
            execution.add_tool_result(event.tool, event.output)
        
        elif event.type == "tts_chunk":
            if ellie.state != "speaking":
                ellie.set_state("speaking")
            self.audio_player.play_chunk(event.audio)
        
        elif event.type == "tts_start":
            conversation.add_agent_message(event.text)
            ellie.set_state("speaking")
        
        elif event.type == "tts_end":
            ellie.set_state("listening")
        
        elif event.type == "final":
            execution.mark_complete()
            conversation.add_final(event.content)
            ellie.set_state("listening")
        
        elif event.type == "error":
            ellie.set_state("error")
            conversation.add_error(event.message)
```

---

## Configuration for Autonomous Mode

```toml
[autonomous]
# Behavior
auto_enter_on_voice_button = true
exit_on_escape = true
exit_on_ellie_click = true

# Safety (all confirmations enabled)
confirm_file_write = true
confirm_file_delete = true
confirm_shell_all = true
confirm_browser_actions = true
confirm_email_send = true

# Display
show_execution_stream = true
show_conversation_panel = true
conversation_panel_height = 0.4  # 40%
ellie_position = "top-center"
ellie_size = "medium"
animation_fps = 60

# Voice
continuous_listening = true
interrupt_on_user_speech = true
tts_enabled = true
stt_enabled = true
vad_silence_timeout_ms = 500
vad_min_speech_ms = 100

# Token cost tracking
show_token_cost = true
cost_update_interval = 1.0  # seconds
```

---

## Keyboard Shortcuts (Vim-style, Space Leader)

| Shortcut | Chat Mode | Autonomous Mode |
|----------|-----------|-----------------|
| `Space` | Leader key | Leader key |
| `Space e` | Enter Autonomous | Exit Autonomous |
| `Space v` | Toggle voice listening | Toggle voice listening |
| `Space q` | - | Exit Autonomous |
| `Space h` | Command palette | Command palette |
| `Space s` | Save session | Save session |
| `Space n` | New session | New session |
| `Space t` | Theme selector | Theme selector |
| `Space p` | Plugin manager | Plugin manager |
| `Space /` | Search messages | - |
| `Space ?` | Shell history | Shell history |
| `Escape` | - | Exit Autonomous |
| `Click Ellie` | - | Exit Autonomous |

---

## Use Cases

| Scenario | Mode | Example Commands |
|----------|------|------------------|
| Quick question | Chat | "What's the weather?" |
| Code review | Chat | "Review this PR" |
| Write new feature | Autonomous | "Create a REST API for todos with auth" |
| Debug failing test | Autonomous | "Run tests and fix the failures" |
| Research | Autonomous | "Find top 10 Python async libraries" |
| Refactor | Autonomous | "Convert all callbacks to async/await" |
| Deploy | Autonomous | "Deploy to Railway and verify" |
| Learn codebase | Chat | "Explain this module" |