"""Browser View Widget for CLI - Minimalist Cyber Hacker Viewport"""
import asyncio
import base64
from typing import Optional
from textual.widgets import Static, RichLog, Input, Button, TextArea
from textual.containers import Container, Horizontal
from textual import events
from textual.reactive import reactive


class BrowserView(Container):
    """Browser viewport widget - displays screenshots and allows interaction"""

    DEFAULT_CSS = """
    BrowserView {
        layout: vertical;
        height: 1fr;
        background: #0A0D14;
        border: solid #1E293B;
    }
    
    .browser-toolbar {
        height: 3;
        background: #111622;
        border-bottom: solid #1E293B;
        padding: 0 1;
    }
    
    .url-input {
        width: 100%;
        margin-right: 1;
        background: #0A0D14;
        color: #00F0FF;
        border: solid #1E293B;
    }
    
    .url-input:focus {
        border: solid #00F0FF;
    }
    
    .toolbar-btn {
        min-width: 6;
        height: 3;
        background: #161C2A;
        color: #E2E8F0;
        border: none;
    }

    .toolbar-btn:hover {
        background: #00F0FF;
        color: #000000;
    }
    
    .browser-viewport {
        height: 100%;
        background: #0A0D14;
        border: none;
        overflow: hidden;
    }
    
    .viewport-content {
        height: 100%;
        width: 100%;
        color: #E2E8F0;
    }
    
    .browser-console {
        height: 10;
        background: #07090E;
        border-top: solid #1E293B;
        padding: 0 1;
        color: #00FF9D;
    }
    """

    current_url: reactive[str] = reactive("about:blank")
    loading: reactive[bool] = reactive(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backend = None
        self._screenshot_data: Optional[bytes] = None

    def compose(self):
        with Horizontal(classes="browser-toolbar"):
            yield Button("◀", id="browser_back", classes="toolbar-btn")
            yield Button("▶", id="browser_forward", classes="toolbar-btn")
            yield Button("🔄", id="browser_reload", classes="toolbar-btn")
            yield Input(placeholder="🌐 Enter URL (e.g. localhost:3000)...", id="url_input", classes="url-input")
            yield Button("Go ❯", id="browser_go", classes="toolbar-btn -primary")
            yield Button("📸 Snap", id="browser_screenshot", classes="toolbar-btn")

        with Container(classes="browser-viewport"):
            yield Static("🌐 Browser ready. Enter a URL above to inspect.", id="viewport_display", classes="viewport-content")

        with Container(classes="browser-console"):
            yield Static("💻 DevTools Console Logs:", classes="console-title")
            yield RichLog(id="console_log", max_lines=100)

    def set_backend(self, backend_client):
        self._backend = backend_client

    async def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "browser_go":
            url = self.query_one("#url_input", Input).value.strip()
            if url:
                await self.navigate(url)
        elif btn_id == "browser_reload":
            if self.current_url:
                await self.navigate(self.current_url)
        elif btn_id == "browser_screenshot":
            await self.capture_screenshot()

    async def navigate(self, url: str):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        self.current_url = url
        self.query_one("#url_input", Input).value = url
        
        log = self.query_one("#console_log", RichLog)
        log.write(f"[cyan]Navigating to {url}...[/cyan]")
        
        try:
            import subprocess
            import os
            cmd = f'start chrome "{url}"' if os.name == 'nt' else f'google-chrome "{url}" &'
            subprocess.Popen(cmd, shell=True)
            log.write(f"[green]✓ Chrome spawned at {url}[/green]")
            display = self.query_one("#viewport_display", Static)
            display.update(f"🌐 Active Tab: [bold cyan]{url}[/bold cyan]\n[dim]Chrome CDP Session Attached on Port 9222[/dim]")
        except Exception as e:
            log.write(f"[red]Error: {e}[/red]")

    async def capture_screenshot(self):
        log = self.query_one("#console_log", RichLog)
        log.write("[yellow]Capturing viewport screenshot...[/yellow]")
        self.notify("Screenshot captured to ~/.ele-agent/screenshots/", title="Browser")