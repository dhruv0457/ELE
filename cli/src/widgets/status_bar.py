from textual.widgets import Static
from rich.text import Text
import os
from datetime import datetime
from ..store import store

class StatusBar(Static):
    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: #0A0E17;
        border-top: solid #1E293B;
        padding: 0 1;
        color: #64748B;
    }
    """

    def on_mount(self) -> None:
        self.update_status()
        self.set_interval(1, self.update_status)

    def update_status(self) -> None:
        status_parts = []
        
        # Connection
        if store.backend_connected:
            status_parts.append("[#00FF9D]● ONLINE[/]")
        else:
            status_parts.append("[#FF3366]○ OFFLINE[/]")
            
        # Workspace
        cwd = os.path.basename(os.getcwd())
        status_parts.append(f"[dim]{cwd}[/]")
        
        # Model
        status_parts.append("[bold #00FFE0]Gemini 3.7[/]")
        
        # Voice
        if store.voice_listening:
            status_parts.append("[#00FF9D]ON[/]")
        else:
            status_parts.append("[dim]OFF[/]")
            
        # Time
        time_str = datetime.now().strftime("%H:%M:%S")
        status_parts.append(f"[dim]{time_str}[/]")
        
        self.update(" │ ".join(status_parts))