"""Plugins Screen"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label, Button, Input, ListView, ListItem, Collapsible
from textual import events

from ..store import store


class PluginsScreen(Container):
    """Plugins Screen"""

    DEFAULT_CSS = """
    PluginsScreen {
        layout: vertical;
        padding: 2;
        display: none;
    }

    PluginsScreen.visible {
        display: block;
    }

    .plugin-item {
        margin: 1 0;
        padding: 1;
        border: solid $primary;
    }

    .plugin-enabled {
        background: $success;
        color: $text;
    }

    .plugin-disabled {
        background: $error;
        color: $text;
    }
    """

    def compose(self):
        yield Static("🔌 Plugins", classes="setting-label")

        with Horizontal():
            yield Input(placeholder="Search marketplace...", id="search_input")
            yield Button("Search", id="search_btn")
            yield Button("Browse All", id="browse_btn")

        yield Static("Installed Plugins", classes="setting-label")
        yield ListView(id="installed_list")

        yield Static("Marketplace", classes="setting-label")
        yield ListView(id="marketplace_list")

    def on_mount(self):
        self.load_installed()
        self.load_marketplace()

    def load_installed(self):
        installed_list = self.query_one("#installed_list")
        installed_list.clear()

        for plugin in store.installed_plugins:
            item = Container(
                Horizontal(
                    Label(f"🔌 {plugin.name} v{plugin.version}", classes="plugin-name"),
                    Button("⚙" if plugin.enabled else "▶", id=f"toggle_{plugin.name}", classes="toggle-btn"),
                    Button("🗑", id=f"remove_{plugin.name}", classes="remove-btn"),
                ),
                classes="plugin-item",
            )
            installed_list.append(ListItem(item))

    def load_marketplace(self):
        marketplace_list = self.query_one("#marketplace_list")
        marketplace_list.clear()

        # Demo marketplace plugins
        demo_plugins = [
            {"name": "Python Code Assistant", "version": "2.1.0", "desc": "Write, debug, refactor Python code"},
            {"name": "Web Scraper Pro", "version": "1.5.3", "desc": "Extract data from any website"},
            {"name": "File Processor", "version": "1.2.0", "desc": "Summarize, transform, analyze files"},
            {"name": "Git Helper", "version": "1.0.1", "desc": "Git workflow automation"},
        ]

        for plugin in demo_plugins:
            item = Container(
                Horizontal(
                    Label(f"📦 {plugin['name']} v{plugin['version']}", classes="plugin-name"),
                    Label(plugin['desc'], classes="plugin-desc"),
                    Button("Install", id=f"install_{plugin['name']}", classes="install-btn"),
                ),
                classes="plugin-item",
            )
            marketplace_list.append(ListItem(item))

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "search_btn":
            self.notify("Search not yet implemented")
        elif event.button.id == "browse_btn":
            self.notify("Browse not yet implemented")
        elif event.button.id.startswith("install_"):
            name = event.button.id.replace("install_", "")
            self.notify(f"Installing {name}...")
        elif event.button.id.startswith("toggle_"):
            name = event.button.id.replace("toggle_", "")
            self.notify(f"Toggled {name}")
        elif event.button.id.startswith("remove_"):
            name = event.button.id.replace("remove_", "")
            self.notify(f"Removed {name}")