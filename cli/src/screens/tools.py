"""Tools Screen"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label, Button, Input, Tree, TabbedContent, TabPane
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
        width: 40;
        border-right: solid $primary;
        height: 1fr;
    }

    #tools_content {
        width: 1fr;
        height: 1fr;
    }

    .tool-tab {
        margin: 1;
    }
    """

    def compose(self):
        yield Container(
            Static("🔧 Tools", classes="setting-label"),
            Button("📁 Files", id="tab_files"),
            Button("💻 Shell", id="tab_shell"),
            Button("🌐 Browser", id="tab_browser"),
            Button("📱 Apps", id="tab_apps"),
            id="tools_sidebar",
        )
        yield Container(
            TabbedContent(
                TabPane("Files", Tree("📁 Home", id="file_tree")),
                TabPane("Shell", id="shell_pane"),
                TabPane("Browser", id="browser_pane"),
                TabPane("Apps", id="apps_pane"),
            ),
            id="tools_content",
        )

    def on_mount(self):
        self.load_file_tree()

    def load_file_tree(self):
        tree = self.query_one("#file_tree", expect_type=Tree)
        tree.root.expand()
        # Add some demo directories
        home = tree.root.add("🏠 Home", expand=True)
        home.add("📁 Projects")
        home.add("📁 Documents")
        home.add("📁 Downloads")
        home.add("📁 Desktop")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "tab_files":
            self.query_one(TabbedContent).active = "files"
        elif event.button.id == "tab_shell":
            self.query_one(TabbedContent).active = "shell"
        elif event.button.id == "tab_browser":
            self.query_one(TabbedContent).active = "browser"
        elif event.button.id == "tab_apps":
            self.query_one(TabbedContent).active = "apps"