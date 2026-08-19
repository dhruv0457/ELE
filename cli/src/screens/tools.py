"""Tools Screen — File browser, shell, browser automation, desktop control"""
import os
import subprocess
from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Tree, Input, Label, ListView, ListItem
from textual.binding import Binding
from textual.widgets import TextArea

from ..store import store
from ..widgets.safe_text_area import SafeTextArea


class ToolsScreen(Container):
    """Tools dashboard — file browser, shell, browser control."""

    BINDINGS = [
        Binding("1", "tab_files", "Files", show=False),
        Binding("2", "tab_shell", "Shell", show=False),
        Binding("3", "tab_browser", "Browser", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Static("🔧  TOOLS", classes="screen-header")
        with Horizontal(id="tools_body"):
            # Tab sidebar
            with Vertical(id="tools_nav"):
                yield Button("📁  Files", id="tab_files", classes="tool-nav-btn active-tab")
                yield Button("💻  Shell", id="tab_shell", classes="tool-nav-btn")
                yield Button("🌐  Browser", id="tab_browser", classes="tool-nav-btn")
                yield Button("🖥  Desktop", id="tab_desktop", classes="tool-nav-btn")

            # Content area
            with Container(id="tools_content"):
                # Files panel
                with Vertical(id="panel_files", classes="tool-panel"):
                    with Horizontal(classes="tool-panel-header"):
                        yield Label("[bold #00FFE0]FILE BROWSER[/]")
                        yield Button("🏠", id="home_btn", classes="icon-btn")
                        yield Button("↑", id="up_btn", classes="icon-btn")
                    yield Label("", id="cwd_label", classes="path-label")
                    yield Tree("/", id="file_tree")

                # Shell panel
                with Vertical(id="panel_shell", classes="tool-panel hidden"):
                    yield Label("[bold #00FFE0]SHELL[/]", classes="tool-panel-title")
                    yield ListView(id="shell_output")
                    with Horizontal(id="shell_input_row"):
                        yield Label("[#00FF9D]❯[/] ", classes="shell-prompt")
                        yield Input(placeholder="Enter command...", id="shell_cmd_input")
                        yield Button("Run", id="run_shell_btn", classes="run-btn")

                # Browser panel
                with Vertical(id="panel_browser", classes="tool-panel hidden"):
                    yield Label("[bold #00FFE0]BROWSER AUTOMATION[/]", classes="tool-panel-title")
                    yield Static(
                        "[dim]Browser automation is handled by the ELE backend.\n"
                        "Start it with: [bold]ele backend[/]  or tell ELE to browse something in Chat.[/]",
                        classes="browser-hint"
                    )
                    with Horizontal(classes="tool-panel-header"):
                        yield Input(placeholder="https://...", id="nav_url_input")
                        yield Button("Go", id="nav_go_btn", classes="run-btn")
                    yield Static("", id="browser_status")

                # Desktop panel
                with Vertical(id="panel_desktop", classes="tool-panel hidden"):
                    yield Label("[bold #00FFE0]DESKTOP AUTOMATION[/]", classes="tool-panel-title")
                    yield Static(
                        "[dim]Desktop automation — launch apps, automate tasks.\n"
                        "Works on Windows via pyautogui + win32api.[/]",
                        classes="browser-hint"
                    )
                    with Horizontal():
                        yield Input(placeholder="App name (e.g. notepad)", id="app_input")
                        yield Button("Launch", id="launch_app_btn", classes="run-btn")
                    yield ListView(id="desktop_log")

    def on_mount(self) -> None:
        self._load_file_tree(Path.home())
        self._active_tab = "files"

    def _load_file_tree(self, path: Path) -> None:
        try:
            tree = self.query_one("#file_tree", Tree)
            tree.clear()
            tree.root.label = str(path)
            tree.root.data = str(path)

            try:
                items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            except PermissionError:
                items = []

            for item in items[:100]:  # Cap at 100
                if item.is_dir():
                    node = tree.root.add(f"📁 {item.name}", data=str(item))
                else:
                    size = ""
                    try:
                        sz = item.stat().st_size
                        size = f" [dim]{self._fmt_size(sz)}[/]"
                    except Exception:
                        pass
                    tree.root.add_leaf(f"📄 {item.name}{size}", data=str(item))

            tree.root.expand()
            cwd_label = self.query_one("#cwd_label", Label)
            cwd_label.update(f"[dim]{path}[/]")
        except Exception as e:
            pass

    def _fmt_size(self, n: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if n < 1024:
                return f"{n:.0f}{unit}"
            n /= 1024
        return f"{n:.1f}TB"

    def _show_tab(self, tab_name: str) -> None:
        for panel in self.query(".tool-panel"):
            panel.add_class("hidden")
        for btn in self.query(".tool-nav-btn"):
            btn.remove_class("active-tab")
        try:
            self.query_one(f"#panel_{tab_name}").remove_class("hidden")
            self.query_one(f"#tab_{tab_name}").add_class("active-tab")
        except Exception:
            pass
        self._active_tab = tab_name

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        # Tab switching
        if btn_id and btn_id.startswith("tab_"):
            self._show_tab(btn_id.replace("tab_", ""))
        elif btn_id == "home_btn":
            self._load_file_tree(Path.home())
        elif btn_id == "up_btn":
            try:
                tree = self.query_one("#file_tree", Tree)
                current = Path(str(tree.root.data))
                self._load_file_tree(current.parent)
            except Exception:
                pass
        elif btn_id == "run_shell_btn":
            await self._run_shell()
        elif btn_id == "nav_go_btn":
            await self._browser_navigate()
        elif btn_id == "launch_app_btn":
            await self._launch_app()

    async def _run_shell(self) -> None:
        cmd_input = self.query_one("#shell_cmd_input", Input)
        cmd = cmd_input.value.strip()
        if not cmd:
            return
        cmd_input.value = ""

        output_list = self.query_one("#shell_output", ListView)
        output_list.append(ListItem(Label(f"[#00FF9D]❯ {cmd}[/]")))

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30,
                cwd=os.getcwd()
            )
            out = result.stdout or result.stderr or "(no output)"
            for line in out.strip().splitlines()[:50]:
                output_list.append(ListItem(Label(f"[dim]  {line}[/]")))
        except subprocess.TimeoutExpired:
            output_list.append(ListItem(Label("[#FF3366]  Timeout after 30s[/]")))
        except Exception as e:
            output_list.append(ListItem(Label(f"[#FF3366]  Error: {e}[/]")))

        output_list.scroll_end(animate=False)

    async def _browser_navigate(self) -> None:
        url_input = self.query_one("#nav_url_input", Input)
        url = url_input.value.strip()
        if not url:
            return

        status = self.query_one("#browser_status", Static)
        import webbrowser
        webbrowser.open(url)
        status.update(f"[#00FF9D]Opened:[/] [dim]{url}[/]")

    async def _launch_app(self) -> None:
        app_input = self.query_one("#app_input", Input)
        app_name = app_input.value.strip()
        if not app_name:
            return

        log = self.query_one("#desktop_log", ListView)
        try:
            subprocess.Popen(app_name, shell=True)
            log.append(ListItem(Label(f"[#00FF9D]✓ Launched: {app_name}[/]")))
        except Exception as e:
            log.append(ListItem(Label(f"[#FF3366]✗ Failed: {e}[/]")))
        log.scroll_end(animate=False)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data:
            path = Path(str(event.node.data))
            if path.is_dir():
                self._load_file_tree(path)

    def action_tab_files(self) -> None:
        self._show_tab("files")

    def action_tab_shell(self) -> None:
        self._show_tab("shell")

    def action_tab_browser(self) -> None:
        self._show_tab("browser")