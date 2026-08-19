"""Browser View Widget for CLI - Displays browser screenshots and viewport"""
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
        background: #ffffff;
        border: solid #1e88e5;
    }
    
    .browser-toolbar {
        height: 3;
        background: #f8f9fa;
        border-bottom: solid #e0e4ec;
        padding: 0 1;
    }
    
    .url-input {
        width: 100%;
        margin-right: 1;
    }
    
    .toolbar-btn {
        width: 8;
        height: 3;
    }
    
    .browser-viewport {
        height: 100%;
        background: #ffffff;
        border: none;
        overflow: hidden;
    }
    
    .viewport-content {
        height: 100%;
        width: 100%;
    }
    
    .browser-console {
        height: 10;
        background: #1a1a2e;
        border-top: solid #e0e4ec;
        padding: 0 1;
    }
    """

    current_url: reactive[str] = reactive("about:blank")
    loading: reactive[bool] = reactive(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backend = None

    def compose(self):
        yield Container(
            Horizontal(
                Input(
                    placeholder="Enter URL...",
                    id="url_input",
                    classes="url-input"
                ),
                Button("Go", id="btn_go", classes="toolbar-btn"),
                Button("Back", id="btn_back", classes="toolbar-btn"),
                Button("Forward", id="btn_forward", classes="toolbar-btn"),
                Button("Reload", id="btn_reload", classes="toolbar-btn"),
                Button("Screenshot", id="btn_screenshot", classes="toolbar-btn"),
                classes="browser-toolbar"
            ),
            Container(
                ListView(id="messages_list"),
                id="messages_container",
            ),
            Container(
                Horizontal(
                    TextArea(id="input_area", placeholder="Type a message... (Enter to send)"),
                    Button("Send", id="send_btn", classes="-primary"),
                    classes="input_row",
                ),
                id="input_bar",
            ),
            id="chat_main",
        )

    def on_mount(self):
        self._auth_task = asyncio.create_task(self._connect_backend())
        self.call_later(self._focus_input)

    def _focus_input(self):
        try:
            self.query_one("#input_area").focus()
        except Exception:
            pass

    async def _connect_backend(self):
        status = self.query_one("#status_line", Static)
        try:
            from .. import backend as be
            if not be.is_backend_up():
                status.update("Backend: NOT running (start backend on :8000)")
                return
            tok = be.login_or_register()
            self._token = tok["access_token"]
            self._session_id = f"session_{__import__('uuid').uuid4().hex[:8]}"
            self._update_status(f"Connected as {tok['email']}")
        except Exception as e:
            self._update_status(f"Error: {e}")

    def _update_status(self, msg: str):
        try:
            self.query_one("#status_line", Static).update(f"Desktop: {msg}")
        except Exception:
            pass

    def _focus_input(self):
        try:
            self.query_one("#input_area").focus()
        except Exception:
            pass

    async def _send_command(self):
        input_area = self.query_one("#input_area", Input)
        text = input_area.value.strip()
        if not text:
            return
        input_area.clear()
        await self._execute_command(text)

    async def _execute_command(self, cmd: str):
        if not self._backend:
            self.log("[red]Backend not connected[/red]")
            return

        parts = cmd.strip().split()
        if not parts:
            return

        action = parts[0].lower()
        args = parts[1:]

        try:
            if action in ("move_mouse", "move"):
                if len(parts) >= 3:
                    await self._exec("move_mouse", {"x": int(parts[1]), "y": int(parts[2])})
                else:
                    self.log("[red]Usage: move_mouse x y[/red]")

            elif parts[0].lower() in ("click", "click_at"):
                if len(parts) >= 3:
                    x, y = int(parts[1]), int(parts[2])
                    btn = parts[3] if len(parts) > 3 else "left"
                    clicks = int(parts[4]) if len(parts) > 4 else 1
                    await self._exec("click", {"x": x, "y": y, "button": btn, "clicks": clicks})
                else:
                    self.log("[red]Usage: click x y [button] [clicks][/red]")

            elif action in ("double_click", "dblclick"):
                if len(parts) >= 3:
                    await self._exec("double_click", {"x": int(parts[1]), "y": int(parts[2])})
                else:
                    self.log("[red]Usage: double_click x y[/red]")

            elif action in ("right_click", "rclick"):
                if len(parts) >= 3:
                    await self._exec("right_click", {"x": int(parts[1]), "y": int(parts[2])})
                else:
                    self.log("[red]Usage: right_click x y[/red]")

            elif action == "drag":
                if len(parts) >= 5:
                    dur = float(parts[5]) if len(parts) > 5 else 1.0
                    await self._exec("drag", {"start_x": int(parts[1]), "start_y": int(parts[2]), "end_x": int(parts[3]), "end_y": int(parts[4]), "duration": float(parts[5]) if len(parts) > 5 else 1.0})
                else:
                    self.log("[red]Usage: drag sx sy ex ey [dur][/red]")

            elif action in ("type", "type_text"):
                text = " ".join(parts[1:])
                if text:
                    await self._exec("type_text", {"text": text})
                else:
                    self.log("[red]Usage: type_text \"text\"[/red]")

            elif action in ("press", "press_key"):
                if len(parts) >= 2:
                    presses = int(parts[2]) if len(parts) > 2 else 1
                    await self._exec("press_key", {"key": parts[1], "presses": int(parts[2]) if len(parts) > 2 else 1})
                else:
                    self.log("[red]Usage: press_key key [presses][/red]")

            elif action == "hotkey":
                if len(parts) >= 2:
                    await self._exec("hotkey", {"keys": parts[1:]})
                else:
                    self.log("[red]Usage: hotkey key1 key2 ...[/red]")

            elif action == "scroll":
                clicks = int(parts[1]) if len(parts) > 1 else 3
                x = int(parts[2]) if len(parts) > 2 else None
                y = int(parts[3]) if len(parts) > 3 else None
                await self._exec("scroll", {"clicks": clicks, "x": x, "y": y})

            elif action == "screenshot":
                full = "full" in " ".join(parts[1:])
                await self._exec("screenshot", {"full_page": full})

            elif action == "capture_region":
                if len(parts) >= 5:
                    await self._exec("capture_region", {"x": int(parts[1]), "y": int(parts[2]), "width": int(parts[3]), "height": int(parts[4])})
                else:
                    self.log("[red]Usage: capture_region x y w h[/red]")

            elif action == "ocr":
                if len(parts) >= 3:
                    r = int(parts[3]) if len(parts) > 3 else 50
                    await self._exec("ocr", {"x": int(parts[1]), "y": int(parts[2]), "radius": r})
                else:
                    self.log("[red]Usage: ocr x y [radius][/red]")

            elif action == "ocr_region":
                if len(parts) >= 5:
                    await self._exec("ocr_region", {"x": int(parts[1]), "y": int(parts[2]), "width": int(parts[3]), "height": int(parts[4])})
                else:
                    self.log("[red]Usage: ocr_region x y w h[/red]")

            elif action == "launch_app":
                if len(parts) >= 2:
                    await self._exec("launch_app", {"name": parts[1], "args": parts[2:]})
                else:
                    self.log("[red]Usage: launch_app name [args...][/red]")

            elif action == "focus_window":
                if len(parts) >= 2:
                    await self._exec("focus_window", {"title": " ".join(parts[1:])})
                else:
                    self.log("[red]Usage: focus_window 'title'[/red]")

            elif action == "close_window":
                if len(parts) >= 2:
                    await self._exec("close_window", {"title": " ".join(parts[1:])})
                else:
                    self.log("[red]Usage: close_window 'title'[/red]")

            elif action == "list_windows":
                await self._exec("list_windows", {})

            elif action == "get_window_info":
                title = " ".join(parts[1:]) if len(parts) > 1 else ""
                await self._exec("get_window_info", {"title": title})

            elif action == "capture_region":
                if len(parts) >= 5:
                    await self._exec("capture_region", {"x": int(parts[1]), "y": int(parts[2]), "width": int(parts[3]), "height": int(parts[4])})
                else:
                    self.log("[red]Usage: capture_region x y w h[/red]")

            elif action == "ocr_region":
                if len(parts) >= 5:
                    await self._exec("ocr_region", {"x": int(parts[1]), "y": int(parts[2]), "width": int(parts[3]), "height": int(parts[4])})
                else:
                    self.log("[red]Usage: ocr_region x y w h[/red]")

            elif action == "help":
                self._show_help()
            else:
                self.log(f"[yellow]Unknown command: {parts[0]}. Type 'help' for commands.[/yellow]")
        except Exception as e:
            self.log(f"[red]Error executing command: {e}[/red]")
        finally:
            pass

    def _show_help(self):
        self.viewport.update("""
[bold]ELE Desktop - Available Commands[/bold]

[bold cyan]Mouse:[/bold cyan]
  move_mouse x y           - Move mouse to coordinates
  click x y [button] [clicks]  - Click at coordinates
  double_click x y         - Double click
  right_click x y          - Right click
  drag sx sy ex ey [dur]   - Drag from start to end

[bold cyan]Keyboard:[/bold cyan]
  type_text "text" [interval]  - Type text
  press_key key [presses] [interval]  - Press key
  hotkey key1 key2 ...     - Press key combination
  scroll clicks [x] [y]    - Scroll wheel

[bold cyan]Screen/OCR:[/bold cyan]
  screenshot [full_page]   - Take screenshot
  capture_region x y w h   - Capture region
  ocr x y [radius]         - OCR at point
  ocr_region x y w h       - OCR in region

[bold cyan]Windows/Apps:[/bold cyan]
  launch_app name [args]   - Launch application
  focus_window "title"     - Focus window
  close_window "title"     - Close window
  list_windows             - List all windows
  get_window_info "title"  - Get window info

[bold cyan]Examples:[/bold cyan]
  move_mouse 500 300
  click 100 200 left 1
  type_text "Hello World"
  press_key enter
  hotkey ctrl c
  hotkey ctrl shift esc
  screenshot
  ocr 500 300 100
  launch_app notepad
  focus_window "Visual Studio Code"
  list_windows
        """)

    def set_backend(self, backend):
        """Set the backend client"""
        self._backend = backend
        self.log("[green]Backend connected[/green]")

    async def _exec(self, action: str, params: dict):
        """Execute a desktop action"""
        if not self._backend:
            self.log("[red]Backend not connected[/red]")
            return
        try:
            result = await self._backend.execute_desktop(action, params)
            if result.success:
                self.log(f"[green]OK: {result.output}[/green]")
                if result.screenshot:
                    self.log(f"[cyan]Screenshot captured ({len(result.screenshot)} chars)[/cyan]")
            else:
                self.log(f"[red]Failed: {result.error}[/red]")
        except Exception as e:
            self.log(f"[red]Error: {e}[/red]")