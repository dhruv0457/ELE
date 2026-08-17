"""Focused test: settings save/reset and plugins actions."""
import sys
sys.path.insert(0, "src")

import asyncio
from textual.app import App
from src.app import ELEApp
from src.config import cli_config, save_cli_config, CLIConfig, get_config_path


async def settings_test():
    app = ELEApp()
    async with app.run_test(size=(120, 40), headless=True) as pilot:
        app.switch_screen("settings")
        await pilot.pause(0.5)
        s = app.query_one("#settings_screen")

        # Change theme via Select
        from textual.widgets import Select
        theme_sel = app.query_one("#theme_select", Select)
        theme_sel.value = "dracula"
        await pilot.pause(0.5)
        print("theme after change:", cli_config.theme)

        # Save settings (call handler directly since button may be off-screen)
        await s.save_settings()
        await pilot.pause(0.5)
        # Verify config file was written
        p = get_config_path()
        print("config path:", p, "exists:", p.exists())
        if p.exists():
            import tomli
            data = tomli.load(open(p, "rb"))
            print("saved theme in file:", data.get("cli", {}).get("theme"))

        # Reset settings
        await s.reset_settings()
        await pilot.pause(0.5)
        print("theme after reset:", cli_config.theme)
        print("=== settings test complete ===")


async def plugins_test():
    app = ELEApp()
    async with app.run_test(size=(120, 40), headless=True) as pilot:
        app.switch_screen("plugins")
        await pilot.pause(0.5)
        plugins_screen = app.query_one("#plugins_screen")
        # Find the first install button and click it (via handler)
        from textual.widgets import Button
        buttons = list(app.query("Button"))
        install_btns = [b for b in buttons if (b.id or "").startswith("install-")]
        print("install buttons found:", len(install_btns))
        if install_btns:
            await plugins_screen.on_button_pressed(Button.Pressed(install_btns[0]))
            await pilot.pause(0.3)
        # Search via handler
        search_btn = app.query_one("#search_btn")
        await plugins_screen.on_button_pressed(Button.Pressed(search_btn))
        await pilot.pause(0.3)
        # Refresh via handler
        browse_btn = app.query_one("#browse_btn")
        await plugins_screen.on_button_pressed(Button.Pressed(browse_btn))
        await pilot.pause(0.3)
        print("=== plugins test complete ===")


async def main():
    await settings_test()
    await plugins_test()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("FATAL:", type(e).__name__, e)
        import traceback
        traceback.print_exc()
        sys.exit(1)
