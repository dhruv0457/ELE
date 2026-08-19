"""Safe Text Area Widget with Enter-to-Submit and Shift+Enter for Newline"""
from textual.widgets import TextArea
from textual.events import Key
from textual.message import Message


class SafeTextArea(TextArea):
    """TextArea that submits on Enter and inserts newline on Shift+Enter / Ctrl+Enter."""

    class Submitted(Message):
        """Posted when user presses Enter to submit."""
        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    def on_key(self, event: Key) -> None:
        # Enter submits message
        if event.key == "enter":
            event.prevent_default()
            event.stop()
            text = self.text
            self.text = ""
            self.post_message(self.Submitted(text))
            return

        # Shift+Enter or Ctrl+J or Alt+Enter inserts newline
        if event.key in ("shift+enter", "ctrl+j", "alt+enter"):
            event.prevent_default()
            event.stop()
            self.insert("\n")
            return

        # Prevent crashes on backspace with empty content
        if event.key == "backspace" and not self.text:
            event.prevent_default()
            return

        # Prevent crashes on undo with empty history
        if event.key == "ctrl+z" and not getattr(self, '_undo_stack', []):
            event.prevent_default()
            return

    def action_undo(self) -> None:
        try:
            if hasattr(self, '_undo_stack') and self._undo_stack:
                super().action_undo()
        except Exception:
            pass