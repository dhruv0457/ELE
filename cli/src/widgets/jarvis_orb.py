"""JARVIS Visual Live Voice & Speech Animation Widget"""
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Button
from textual.reactive import reactive
import itertools


class JarvisLiveOrb(Container):
    """Visual speaking & listening animation bar inspired by Gemini Live and JARVIS."""

    DEFAULT_CSS = """
    JarvisLiveOrb {
        height: auto;
        min-height: 1;
        width: 100%;
        background: transparent;
        layout: horizontal;
        content-align: center middle;
        padding: 0 1;
        margin: 0;
    }
    #orb_visual {
        width: 1fr;
        content-align: center middle;
        text-align: center;
        height: 1;
    }
    #orb_toggle_btn {
        width: auto;
        height: 1;
        background: transparent;
        color: #00FFE0;
        border: none;
        padding: 0 1;
        text-style: bold;
    }
    #orb_toggle_btn:hover {
        background: #1E293B;
        color: #00FF9D;
    }
    #orb_toggle_btn.active {
        color: #00FF9D;
        background: #00FF9D22;
        border: solid #00FF9D44;
    }
    """

    is_active: reactive[bool] = reactive(False)
    state_mode: reactive[str] = reactive("idle")  # idle, listening, speaking, thinking

    WAVE_FRAMES = [
        "∿ ∿ ∿ ∿ ∿ ∿ ∿",
        "∿ ∿ ◈ ∿ ◈ ∿ ∿",
        "∿ ◈ ✦ ◈ ✦ ◈ ∿",
        "◈ ✦ ◉ ✦ ◉ ✦ ◈",
        "✦ ◉ ● ◉ ● ◉ ✦",
        "◈ ✦ ◉ ✦ ◉ ✦ ◈",
        "∿ ◈ ✦ ◈ ✦ ◈ ∿",
    ]

    SPEAK_FRAMES = [
        "●  ◉  ◈  ✦  ◈  ◉  ●",
        "◉  ◈  ✦  ●  ✦  ◈  ◉",
        "◈  ✦  ●  ◉  ●  ✦  ◈",
        "✦  ●  ◉  ◈  ◉  ●  ✦",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._frame_idx = 0
        self._timer = None

    def compose(self) -> ComposeResult:
        yield Button("🎙️ JARVIS LIVE", id="orb_toggle_btn")
        yield Static("[dim]✦ JARVIS Standby ✦[/]", id="orb_visual")

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.15, self._animate)

    def _animate(self) -> None:
        if not self.is_active:
            return
        self._frame_idx = (self._frame_idx + 1) % len(self.WAVE_FRAMES)
        visual = self.query_one("#orb_visual", Static)

        if self.state_mode == "speaking":
            frame = self.SPEAK_FRAMES[self._frame_idx % len(self.SPEAK_FRAMES)]
            visual.update(f"[bold #00FFE0]{frame}[/]  [bold #00FF9D]✦ JARVIS SPEAKING ✦[/]  [bold #00FFE0]{frame}[/]")
        elif self.state_mode == "thinking":
            visual.update(f"[italic #A855F7]🧠 REASONING... {'·' * ((self._frame_idx % 4) + 1)}[/]")
        else:  # listening / live
            frame = self.WAVE_FRAMES[self._frame_idx]
            visual.update(f"[bold #00FF9D]{frame}[/]  [bold #00FFE0]✦ LIVE LISTENING ✦[/]  [bold #00FF9D]{frame}[/]")

    def toggle(self) -> bool:
        self.is_active = not self.is_active
        btn = self.query_one("#orb_toggle_btn", Button)
        visual = self.query_one("#orb_visual", Static)

        if self.is_active:
            btn.add_class("active")
            btn.label = "🔴 LIVE ACTIVE"
            self.state_mode = "listening"
        else:
            btn.remove_class("active")
            btn.label = "🎙️ JARVIS LIVE"
            self.state_mode = "idle"
            visual.update("[dim]✦ JARVIS Standby ✦[/]")

        return self.is_active

    def set_speaking(self, speaking: bool = True) -> None:
        if not self.is_active:
            return
        self.state_mode = "speaking" if speaking else "listening"

    def set_thinking(self, thinking: bool = True) -> None:
        if not self.is_active:
            return
        self.state_mode = "thinking" if thinking else "listening"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "orb_toggle_btn":
            state = self.toggle()
            status = "Activated" if state else "Deactivated"
            self.app.notify(f"JARVIS Live Voice Mode {status}")
