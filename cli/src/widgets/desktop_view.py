from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Static, RichLog, Label
from textual.reactive import reactive

class DesktopView(Container):
    DEFAULT_CSS = """
    DesktopView {
        background: #0A0E17;
        color: #E2E8F0;
    }
    
    #desktop-toolbar {
        height: 3;
        background: #111622;
        border-bottom: solid #1E293B;
        align: left middle;
        padding: 0 1;
    }
    
    #desktop-toolbar Label {
        color: #00FFE0;
        text-style: bold;
        margin-right: 2;
    }
    
    #desktop-main {
        height: 1fr;
    }
    
    #desktop-sidebar {
        width: 20;
        background: #161C2A;
        border-right: solid #1E293B;
        padding: 1;
    }
    
    .sidebar-group {
        margin-bottom: 1;
    }
    
    .sidebar-group-title {
        color: #A855F7;
        text-style: bold;
    }
    
    RichLog {
        background: #0A0E17;
        border: none;
    }
    
    Button {
        height: 1;
        border: none;
        background: #1E293B;
        color: #00FFE0;
        min-width: 10;
        margin-right: 1;
    }
    
    Button:hover {
        background: #334155;
    }
    """

    backend = reactive(None)

    def compose(self) -> ComposeResult:
        with Horizontal(id="desktop-toolbar"):
            yield Label("Desktop Automation")
            yield Button("Screenshot", id="btn-screenshot")
            yield Button("Click", id="btn-click")
            yield Button("Type", id="btn-type")
            yield Button("Scroll", id="btn-scroll")
            
        with Horizontal(id="desktop-main"):
            with Vertical(id="desktop-sidebar"):
                with Vertical(classes="sidebar-group"):
                    yield Label("Mouse", classes="sidebar-group-title")
                    yield Static("- Move")
                    yield Static("- Click")
                with Vertical(classes="sidebar-group"):
                    yield Label("Keyboard", classes="sidebar-group-title")
                    yield Static("- Type")
                    yield Static("- Hotkey")
                with Vertical(classes="sidebar-group"):
                    yield Label("Windows", classes="sidebar-group-title")
                    yield Static("- List")
                    yield Static("- Focus")
                with Vertical(classes="sidebar-group"):
                    yield Label("Screen", classes="sidebar-group-title")
                    yield Static("- Find Image")
            yield RichLog(id="desktop-log")

    def set_backend(self, backend) -> None:
        self.backend = backend

    def log_message(self, message: str) -> None:
        log_widget = self.query_one("#desktop-log", RichLog)
        log_widget.write(message)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-screenshot":
            self.log_message("[#00FF9D]Taking screenshot...[/]")
            if self.backend:
                self.backend.screenshot()
        elif event.button.id == "btn-click":
            self.log_message("[#FFB800]Simulating click...[/]")
        elif event.button.id == "btn-type":
            self.log_message("[#A855F7]Typing text...[/]")
        elif event.button.id == "btn-scroll":
            self.log_message("[#00FFE0]Scrolling...[/]")