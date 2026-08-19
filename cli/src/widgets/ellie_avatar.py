from textual.widgets import Static
from textual.reactive import reactive
from ..store import store, OverlayStatus

class EllieAvatar(Static):
    DEFAULT_CSS = """
    EllieAvatar {
        dock: top;
        width: 100%;
        height: 1;
        content-align: center middle;
        text-style: bold;
        color: #00FFE0;
        background: #0A0E17;
        border-bottom: solid #1E293B;
    }
    
    EllieAvatar.listening { color: #00FF9D; }
    EllieAvatar.thinking { color: #A855F7; }
    EllieAvatar.working { color: #FFB800; }
    EllieAvatar.speaking { color: #00FFE0; }
    EllieAvatar.error { color: #FF3366; }
    """

    FRAMES = {
        OverlayStatus.IDLE: ['⠁ IDLE', '⠂ IDLE', '⠄ IDLE', '⡀ IDLE', '⢀ IDLE', '⠠ IDLE', '⠐ IDLE', '⠈ IDLE'],
        OverlayStatus.LISTENING: ['▁ 🎙 LISTENING', '▂ 🎙 LISTENING', '▃ 🎙 LISTENING', '▄ 🎙 LISTENING', '▅ 🎙 LISTENING'],
        OverlayStatus.THINKING: ['⠋ 🧠 THINKING', '⠙ 🧠 THINKING', '⠹ 🧠 THINKING', '⠸ 🧠 THINKING', '⠼ 🧠 THINKING', '⠴ 🧠 THINKING', '⠦ 🧠 THINKING', '⠧ 🧠 THINKING', '⠇ 🧠 THINKING', '⠏ 🧠 THINKING'],
        OverlayStatus.WORKING: ['▱ ⚙ WORKING', '▰ ⚙ WORKING', '▱ ⚙ WORKING', '▰ ⚙ WORKING'],
        OverlayStatus.SPEAKING: ['▁ 🗣 SPEAKING', '▂ 🗣 SPEAKING', '▃ 🗣 SPEAKING', '▄ 🗣 SPEAKING'],
        OverlayStatus.ERROR: ['⠿ ❌ ERROR', '⠷ ❌ ERROR']
    }

    state = reactive(OverlayStatus.IDLE)
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.frame_index = 0
        self._animation_timer = None

    def on_mount(self) -> None:
        self._animation_timer = self.set_interval(0.12, self.animate)

    def animate(self) -> None:
        frames = self.FRAMES.get(self.state, self.FRAMES[OverlayStatus.IDLE])
        self.frame_index = (self.frame_index + 1) % len(frames)
        self.update(frames[self.frame_index])

    def watch_state(self, old_state, new_state) -> None:
        self.frame_index = 0
        self.remove_class("listening", "thinking", "working", "speaking", "error")
        if new_state == OverlayStatus.LISTENING:
            self.add_class("listening")
        elif new_state == OverlayStatus.THINKING:
            self.add_class("thinking")
        elif new_state == OverlayStatus.WORKING:
            self.add_class("working")
        elif new_state == OverlayStatus.SPEAKING:
            self.add_class("speaking")
        elif new_state == OverlayStatus.ERROR:
            self.add_class("error")
        self.animate()

    def on_click(self) -> None:
        pass