"""Safe TextArea that handles undo/backspace crashes."""
from textual.widgets import TextArea
from textual import events


class SafeTextArea(TextArea):
    """TextArea that handles undo/backspace gracefully on empty content."""

    async def on_key(self, event: events.Key) -> None:
        """Handle key events, prevent undo crash on empty content."""
        # Prevent undo (Ctrl+Z) and backspace on empty content
        if event.key in ("ctrl+z", "backspace"):
            if not self.text or self.text.strip() == "":
                event.prevent_default()
                event.stop()
                return
        
        # Also prevent undo when at start of document
        if event.key == "ctrl+z":
            if self.cursor_location == (0, 0):
                event.prevent_default()
                event.stop()
                return
        
        # Call parent class on_key
        await super()._on_key(event)

    def action_undo(self) -> None:
        """Override undo to handle empty content gracefully."""
        try:
            if not self.text or self.text.strip() == "":
                return
            if self.cursor_location == (0, 0):
                return
            super().action_undo()
        except Exception:
            # Silently ignore undo errors
            pass