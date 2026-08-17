"""Ellie Avatar Widget - Braille Animation"""
from textual.widgets import Static
from textual.containers import Container
from textual import events

from ..store import store, OverlayStatus


class EllieAvatar(Static):
    """Animated Ellie avatar using braille"""

    FRAMES = {
        OverlayStatus.IDLE: [
            "⠁ Ellie", "⠂ Ellie", "⠃ Ellie", "⠄ Ellie",
            "⠅ Ellie", "⠆ Ellie", "⠇ Ellie", "⠈ Ellie",
        ],
        OverlayStatus.LISTENING: [
            "▁ Ellie", "▂ Ellie", "▃ Ellie", "▄ Ellie",
            "▅ Ellie", "▆ Ellie", "▇ Ellie", "█ Ellie",
            "▇ Ellie", "▆ Ellie", "▅ Ellie", "▄ Ellie",
            "▃ Ellie", "▂ Ellie",
        ],
        OverlayStatus.THINKING: [
            "⠋ Ellie", "⠙ Ellie", "⠹ Ellie", "⠸ Ellie",
            "⠼ Ellie", "⠴ Ellie", "⠦ Ellie", "⠧ Ellie",
            "⠇ Ellie", "⠏ Ellie",
        ],
        OverlayStatus.WORKING: [
            "▱ Ellie", "▰ Ellie", "▰▱ Ellie", "▰▰ Ellie",
            "▰▰▱ Ellie", "▰▰▰ Ellie", "▰▰▰▱ Ellie", "▰▰▰▰ Ellie",
        ],
        OverlayStatus.SPEAKING: [
            "▁ Ellie", "▂ Ellie", "▃ Ellie", "▄ Ellie",
            "▅ Ellie", "▆ Ellie", "▇ Ellie", "█ Ellie",
            "▇ Ellie", "▆ Ellie", "▅ Ellie", "▄ Ellie",
            "▃ Ellie", "▂ Ellie",
        ],
        OverlayStatus.ERROR: [
            "⠿ Ellie", "⠿ Ellie", "⠿ Ellie",
        ],
    }

    DEFAULT_CSS = """
    EllieAvatar {
        dock: top;
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        background: $surface;
        border-bottom: solid $primary;
    }

    EllieAvatar.listening {
        color: $success;
    }

    EllieAvatar.thinking {
        color: $primary;
    }

    EllieAvatar.working {
        color: $warning;
    }

    EllieAvatar.speaking {
        color: $accent;
    }

    EllieAvatar.error {
        color: $error;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = OverlayStatus.IDLE
        self.frame_index = 0
        self.animation_task = None

    def on_mount(self):
        self.update_animation()

    def update_animation(self):
        """Start 60 FPS animation"""
        if self.animation_task:
            self.animation_task.cancel()
        # 60 FPS = 16.67ms
        self.animation_task = self.set_interval(1/60, self.animate)

    def animate(self):
        frames = self.FRAMES.get(self.state, ["🤖 Ellie"])
        self.frame_index = (self.frame_index + 1) % len(frames)
        self.update(frames[self.frame_index])

        # Update CSS class for color
        self.remove_class(*[s.value for s in OverlayStatus])
        self.add_class(self.state.value)

    def watch_state(self, state: str):
        """Called when store.overlay_status changes"""
        if hasattr(OverlayStatus, state.upper()):
            self.state = OverlayStatus[state.upper()]
            self.frame_index = 0

    def on_click(self, event):
        """Click Ellie to exit autonomous mode"""
        if store.mode == "autonomous":
            self.app.action_toggle_mode()