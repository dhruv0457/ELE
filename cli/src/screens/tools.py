"""Tools Screen - File, Shell, Apps, Browser, Desktop"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label, Button, Tree
from textual import events

from ..widgets.browser_view import BrowserView
from ..widgets.desktop_view import DesktopView


class ToolsScreen(Container):
    """Tools Screen - File tree, shell, apps, browser"""

    DEFAULT_CSS = """
    ToolsScreen {
        layout: horizontal;
        display: none;
    }

    ToolsScreen.visible {
        display: block;
    }

    #tools_sidebar {
        width: 32;
        border-right: solid $primary;
        height: 1fr;
        padding: 1;
        background: #f8f9fa;
    }

    #tools_content {
        width: 1fr;
        height: 1fr;
        padding: 1;
    }

    .tool-tab {
        margin: 0 0 1 0;
        width: 1fr;
    }

    .tool-tab.-active {
        background: $primary;
        color: $surface;
    }

    .panel {
        display: none;
        height: 1fr;
        border: solid $border;
        padding: 1;
    }

    .panel.visible {
        display: block;
    }

    .tool-title {
        text-style: bold;
        color: $primary;
        margin: 1 0;
    }
    """

    def compose(self):
        yield Container(
            Static("🔧 Tools", classes="tool-title"),
            Button("📁 Files", id="tab_files", classes="tool-tab -active"),
            Button("💻 Shell", id="tab_shell", classes="tool-tab"),
            Button("🌐 Browser", id="tab_browser", classes="tool-tab"),
            Button("🖥️ Desktop", id="tab_desktop", classes="tool-tab"),
            Button("📱 Apps", id="tab_apps", classes="tool-tab"),
            id="tools_sidebar",
        )
        yield Container(
            Container(Tree("📁 Home", id="file_tree"), id="panel_files", classes="panel visible"),
            Container(Static("💻 Shell - Type commands below", id="shell_text"), id="panel_shell", classes="panel"),
            BrowserView(classes="panel"),
            DesktopView(classes="panel"),
            Container(Static("📱 App Launcher - Click to launch", id="apps_text"), id="panel_apps", classes="panel"),
            id="tools_content",
        )

    def on_mount(self):
        self.load_file_tree()
        # Initialize browser view with backend
        try:
            browser_view = self.query_one(BrowserView)
            from .. import backend as be
            browser_view.set_backend(be)
        except Exception as e:
            self.notify(f"Browser init: {e}", severity="warning")
        
        # Initialize desktop view with backend
        try:
            desktop_view = self.query_one(DesktopView)
            from .. import backend as be
            desktop_view.set_backend(be)
        except Exception as e:
            self.notify(f"Desktop init: {e}", severity="warning")

    def load_file_tree(self):
        tree = self.query_one("#file_tree", expect_type=Tree)
        tree.root.expand()
        home = tree.root.add("🏠 Home", expand=True)
        home.add("📁 Projects")
        home.add("📁 Documents")
        home.add("📁 Downloads")
        home.add("📁 Desktop")

    def _activate_tab(self, tab_id: str):
        tab_map = {
            "tab_files": "panel_files",
            "tab_shell": "panel_shell",
            "tab_browser": "browser_view",
            "tab_desktop": "desktop_view",
            "tab_apps": "panel_apps",
        }
        target = tab_map.get(tab_id)
        if not target:
            return
        for btn_id in tab_map:
            btn = self.query_one(f"#{btn_id}")
            classes = set(btn.classes)
            if btn_id == tab_id:
                classes.add("-active")
            else:
                classes.discard("-active")
            btn.classes = classes
        
        # Get the target panel/widget by type
        if target == "browser_view":
            panel = self.query_one(BrowserView)
        elif target == "desktop_view":
            panel = self.query_one(DesktopView)
        else:
            panel = self.query_one(f"#{target}")
        
        # Update all panels
        for panel_id in ["panel_files", "panel_shell", "panel_apps"]:
            try:
                panel = self.query_one(f"#{panel_id}")
                classes = set(panel.classes)
                if panel_id == target:
                    classes.add("visible")
                else:
                    classes.discard("visible")
                panel.classes = classes
            except Exception:
                pass
        
        # Handle browser and desktop views (no ID)
        if target == "browser_view":
            browser = self.query_one(BrowserView)
            classes = set(browser.classes)
            classes.add("visible")
            browser.classes = classes
        elif target == "desktop_view":
            desktop = self.query_one(DesktopView)
            classes = set(desktop.classes)
            classes.add("visible")
            desktop.classes = classes
        else:
            # Hide the other special views
            try:
                browser = self.query_one(BrowserView)
                if target != "browser_view":
                    classes = set(browser.classes)
                    classes.discard("visible")
                    browser.classes = classes
            except Exception:
                pass
            try:
                desktop = self.query_one(DesktopView)
                if target != "desktop_view":
                    classes = set(desktop.classes)
                    classes.discard("visible")
                    desktop.classes = classes
            except Exception:
                pass

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id in ("tab_files", "tab_shell", "tab_browser", "tab_desktop", "tab_apps"):
            self._activate_tab(event.button.id)