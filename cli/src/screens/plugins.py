from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Input, Button, ListView, ListItem, Label
from ..store import store

class PluginsScreen(Container):
    DEFAULT_CSS = """
    PluginsScreen {
        display: none;
        padding: 1;
        background: #0A0E17;
    }
    PluginsScreen.visible {
        display: block;
    }
    .plugin-item {
        background: #111622;
        padding: 1;
        border: solid #00FFE0;
        margin-bottom: 1;
        layout: horizontal;
    }
    .plugin-name {
        color: #00FFE0;
        text-style: bold;
        width: 1fr;
    }
    .plugin-desc {
        color: #8F9BA8;
        width: 2fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Plugins", classes="plugin-name")
        with Horizontal():
            yield Input(placeholder="Search plugins...", id="search_input")
            yield Button("Search", id="search_btn", variant="primary")
            yield Button("Refresh", id="refresh_btn", variant="success")
        
        yield Label("Installed", classes="plugin-name")
        yield ListView(id="installed_list")
        
        yield Label("Marketplace", classes="plugin-name")
        yield ListView(id="marketplace_list")

    def on_mount(self) -> None:
        self.load_installed()
        self.load_marketplace()

    def load_installed(self) -> None:
        lst = self.query_one("#installed_list", ListView)
        for i in range(2):
            lst.append(ListItem(
                Container(
                    Label(f"Demo Plugin {i}", classes="plugin-name"),
                    Label("A demo plugin installed.", classes="plugin-desc"),
                    Button("Toggle", id=f"toggle_{self._slug(f'Demo Plugin {i}')}", variant="warning"),
                    Button("Remove", id=f"remove_{self._slug(f'Demo Plugin {i}')}", variant="error"),
                    classes="plugin-item"
                )
            ))

    def load_marketplace(self) -> None:
        lst = self.query_one("#marketplace_list", ListView)
        for i in range(3):
            lst.append(ListItem(
                Container(
                    Label(f"Marketplace Plugin {i}", classes="plugin-name"),
                    Label("A demo plugin from marketplace.", classes="plugin-desc"),
                    Button("Install", id=f"install_{self._slug(f'Marketplace Plugin {i}')}", variant="success"),
                    classes="plugin-item"
                )
            ))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "search_btn":
            pass
        elif btn_id == "refresh_btn":
            pass
        elif btn_id and btn_id.startswith("toggle_"):
            pass
        elif btn_id and btn_id.startswith("remove_"):
            pass
        elif btn_id and btn_id.startswith("install_"):
            pass

    def _slug(self, name: str) -> str:
        return name.lower().replace(" ", "_")
