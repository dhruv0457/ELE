"""Tools Screen"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label, Button, Input, Tree
from textual import events


class ToolsScreen(Container):
    """Tools Screen - File tree, shell, browser"""

    DEFAULT_CSS = """
    ToolsScreen {
        layout: horizontal;
        display: none;
    }

    ToolsScreen.visible {
        display: block;
    }

    #tools_sidebar {
        width: 24;
        border-right: solid $primary;
        height: 1fr;
        padding: 1;
    }

    #tools_content {
        width: 1fr;
        height: 1fr;
        padding: 0 1;
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
        border: solid $primary;
        padding: 1;
    }

    .panel.visible {
        display: block;
    }
    """

    def compose(self):
        yield Container(
            Static("🔧 Tools", classes="setting-label"),
            Button("📁 Files", id="tab_files", classes="tool-tab -active"),
            Button("💻 Shell", id="tab_shell", classes="tool-tab"),
            Button("🌐 Browser", id="tab_browser", classes="tool-tab"),
            Button("📱 Apps", id="tab_apps", classes="tool-tab"),
            id="tools_sidebar",
        )
        yield Container(
            Container(Tree("📁 Home", id="file_tree"), id="panel_files", classes="panel visible"),
            Container(Static("$ shell — type a command (coming soon)", id="shell_text"), id="panel_shell", classes="panel"),
            Container(Static("🌐 Browser automation panel (coming soon)"), id="panel_browser", classes="panel"),
            Container(Static("📱 App launcher panel (coming soon)"), id="panel_apps", classes="panel"),
            id="tools_content",
        )

    def on_mount(self):
        self.load_file_tree()

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
            "tab_browser": "panel_browser",
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
        for panel_id in tab_map.values():
            panel = self.query_one(f"#{panel_id}")
            classes = set(panel.classes)
            if panel_id == target:
                classes.add("visible")
            else:
                classes.discard("visible")
            panel.classes = classes

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id in ("tab_files", "tab_shell", "tab_browser", "tab_apps"):
            self._activate_tab(event.button.id)
