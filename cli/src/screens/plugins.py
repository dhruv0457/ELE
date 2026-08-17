"""Plugins Screen"""
import re
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label, Button, Input, ListView, ListItem
from textual import events

from ..store import store


def _slug(name: str) -> str:
    """Turn a plugin name into a safe CSS identifier."""
    s = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return s or "plugin"


class PluginsScreen(Container):
    """Plugins Screen"""

    DEFAULT_CSS = """
    PluginsScreen {
        layout: vertical;
        padding: 1 2;
        display: none;
    }

    PluginsScreen.visible {
        display: block;
    }

    .plugin-item {
        margin: 1 0;
        padding: 0 1;
        border: solid $primary;
        height: auto;
    }

    .plugin-name {
        text-style: bold;
        color: $primary;
        width: 1fr;
    }

    .plugin-desc {
        color: $text-muted;
        width: 2fr;
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Map button id -> plugin display name
        self._installed_names: dict[str, str] = {}
        self._market_names: dict[str, str] = {}

    def compose(self):
        yield Static("🔌 Plugins", classes="setting-label")

        with Horizontal():
            yield Input(placeholder="Search marketplace...", id="search_input")
            yield Button("Search", id="search_btn")
            yield Button("Refresh", id="browse_btn")

        yield Static("Installed Plugins", classes="setting-label")
        yield ListView(id="installed_list")

        yield Static("Marketplace", classes="setting-label")
        yield ListView(id="marketplace_list")

    def on_mount(self):
        try:
            self.load_installed()
        except Exception as e:
            self.notify(f"Installed load failed: {e}", severity="error")
        try:
            self.load_marketplace()
        except Exception as e:
            self.notify(f"Marketplace load failed: {e}", severity="error")

    async def _load_installed_from_backend(self):
        """Fetch installed plugins from backend (best effort)."""
        try:
            import httpx
            from .. import backend as be
            if not be.is_backend_up():
                return []
            tok = be.load_token()
            if not tok:
                return []
            r = httpx.get(
                f"{be.backend_url()}/api/v1/plugins",
                headers={"Authorization": f"Bearer {tok['access_token']}"},
                timeout=4.0,
            )
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return []

    def load_installed(self):
        installed_list = self.query_one("#installed_list", ListView)
        installed_list.clear()
        self._installed_names.clear()

        plugins = list(store.installed_plugins)
        if not plugins:
            plugins = [
                {"name": "File Processor", "version": "1.2.0", "enabled": True},
                {"name": "Web Searcher", "version": "1.0.0", "enabled": True},
                {"name": "Code Assistant", "version": "2.1.0", "enabled": False},
            ]

        for plugin in plugins:
            name = plugin.get("name") if isinstance(plugin, dict) else plugin.name
            version = plugin.get("version") if isinstance(plugin, dict) else plugin.version
            enabled = plugin.get("enabled", True) if isinstance(plugin, dict) else plugin.enabled
            slug = _slug(name)
            btn_id = f"toggle-{slug}"
            rm_id = f"remove-{slug}"
            self._installed_names[btn_id] = name
            self._installed_names[rm_id] = name

            item = ListItem(
                Container(
                    Horizontal(
                        Label(f"🔌 {name} v{version}", classes="plugin-name"),
                        Button("⚙" if enabled else "▶", id=btn_id, classes="toggle-btn"),
                        Button("🗑", id=rm_id, classes="remove-btn"),
                    ),
                    classes="plugin-item",
                )
            )
            installed_list.append(item)

    def load_marketplace(self):
        marketplace_list = self.query_one("#marketplace_list", ListView)
        marketplace_list.clear()
        self._market_names.clear()

        demo_plugins = [
            {"name": "Python Code Assistant", "version": "2.1.0", "desc": "Write, debug, refactor Python code"},
            {"name": "Web Scraper Pro", "version": "1.5.3", "desc": "Extract data from any website"},
            {"name": "File Processor", "version": "1.2.0", "desc": "Summarize, transform, analyze files"},
            {"name": "Git Helper", "version": "1.0.1", "desc": "Git workflow automation"},
        ]

        for plugin in demo_plugins:
            name = plugin["name"]
            slug = _slug(name)
            inst_id = f"install-{slug}"
            self._market_names[inst_id] = name

            item = ListItem(
                Container(
                    Horizontal(
                        Label(f"📦 {name} v{plugin['version']}", classes="plugin-name"),
                        Label(plugin["desc"], classes="plugin-desc"),
                        Button("Install", id=inst_id, classes="install-btn"),
                    ),
                    classes="plugin-item",
                )
            )
            marketplace_list.append(item)

    async def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id or ""
        if bid == "search_btn":
            await self._search_marketplace()
        elif bid == "browse_btn":
            self.load_installed()
            self.load_marketplace()
            self.notify("Refreshed plugins")
        elif bid.startswith("install-"):
            name = self._market_names.get(bid, bid.replace("install-", ""))
            self.notify(f"Installing {name}...")
        elif bid.startswith("toggle-"):
            name = self._installed_names.get(bid, bid.replace("toggle-", ""))
            self.notify(f"Toggled {name}")
        elif bid.startswith("remove-"):
            name = self._installed_names.get(bid, bid.replace("remove-", ""))
            self.notify(f"Removed {name}")

    async def _search_marketplace(self):
        try:
            query = self.query_one("#search_input", Input).value.strip()
        except Exception:
            query = ""
        if not query:
            self.notify("Type a search term first")
            return
        self.notify(f"Searching marketplace for '{query}'...")
        self.load_marketplace()
