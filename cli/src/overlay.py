"""Overlay Pop-up Component"""
import asyncio
from textual.app import App
from textual.widgets import Static
from textual.containers import Horizontal
from textual.reactive import reactive
from rich.text import Text


class OverlayStatus:
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    WORKING = "working"
    SPEAKING = "speaking"
    ERROR = "error"


class OverlayWidget(Static):
    """Top-center overlay showing agent status"""

    status: reactive[str] = reactive(OverlayStatus.IDLE)

    def __init__(self, status: str = OverlayStatus.IDLE):
        super().__init__()
        self.status = status

    def render(self):
        icons = {
            OverlayStatus.IDLE: "🤖",
            OverlayStatus.LISTENING: "🎤",
            OverlayStatus.THINKING: "⚙️",
            OverlayStatus.WORKING: "🔨",
            OverlayStatus.SPEAKING: "🔊",
            OverlayStatus.ERROR: "⚠️"
        }

        labels = {
            OverlayStatus.IDLE: "Hey ELE",
            OverlayStatus.LISTENING: "Listening...",
            OverlayStatus.THINKING: "Thinking...",
            OverlayStatus.WORKING: "Working...",
            OverlayStatus.SPEAKING: "Speaking...",
            OverlayStatus.ERROR: "Error"
        }

        icon = icons.get(self.status, "🤖")
        label = labels.get(self.status, "Hey ELE")

        return Text(f"{icon} {label}", style="bold")

    def watch_status(self, old: str, new: str) -> None:
        self.refresh()

        if new == OverlayStatus.IDLE:
            self.set_timer(3, self.hide)

    def hide(self) -> None:
        self.display = False

    def show(self, status: str = OverlayStatus.IDLE) -> None:
        self.status = status
        self.display = True


async def main():
    """Demo overlay"""
    app = App()
    overlay = OverlayWidget()
    app.mount(overlay)
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())