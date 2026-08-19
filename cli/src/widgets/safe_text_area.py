from textual.widgets import TextArea
from textual.events import Key

class SafeTextArea(TextArea):
    def on_key(self, event: Key) -> None:
        # Prevent crashes on backspace with empty content
        if event.key == "backspace" and not self.text:
            event.prevent_default()
            
        # Prevent crashes on undo with empty history
        if event.key == "ctrl+z" and not getattr(self, '_undo_stack', []):
            event.prevent_default()

    def action_undo(self) -> None:
        try:
            if hasattr(self, '_undo_stack') and self._undo_stack:
                super().action_undo()
        except Exception:
            pass