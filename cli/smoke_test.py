"""Headless smoke test for the ELE CLI TUI using Textual pilot."""
import sys
sys.path.insert(0, "src")

import asyncio
from textual.app import App
from textual.dom import DOMNode
from src.app import ELEApp


async def smoke():
    app = ELEApp()
    async with app.run_test(size=(120, 40), headless=True) as pilot:
        # Let the app settle and try to mount everything
        await pilot.pause(0.5)
        # Check which screens are composed
        try:
            chat = app.query_one("#chat_screen")
            print("chat_screen OK, visible=", chat.display)
        except Exception as e:
            print("chat_screen ERR:", e)
        try:
            settings = app.query_one("#settings_screen")
            print("settings_screen OK, display=", settings.display)
        except Exception as e:
            print("settings_screen ERR:", e)
        try:
            plugins = app.query_one("#plugins_screen")
            print("plugins_screen OK, display=", plugins.display)
        except Exception as e:
            print("plugins_screen ERR:", e)
        try:
            tools = app.query_one("#tools_screen")
            print("tools_screen OK, display=", tools.display)
        except Exception as e:
            print("tools_screen ERR:", e)
        try:
            autonomous = app.query_one("#autonomous_screen")
            print("autonomous_screen OK, display=", autonomous.display)
        except Exception as e:
            print("autonomous_screen ERR:", e)
        try:
            avatar = app.query_one("#ellie_avatar")
            print("ellie_avatar OK")
        except Exception as e:
            print("ellie_avatar ERR:", e)
        try:
            status = app.query_one("#status_bar")
            print("status_bar OK")
        except Exception as e:
            print("status_bar ERR:", e)
        # Try sending a message from the chat screen and wait for a streamed response
        try:
            input_area = app.query_one("#input_area")
            input_area.text = "Say hi in one short sentence."
            await pilot.pause()
            send_btn = app.query_one("#send_btn")
            await pilot.click(send_btn)
            # Wait long enough for the backend to authenticate + stream a response
            await pilot.pause(8)
            # Count rendered message bubbles
            from src.widgets.message_bubble import MessageBubble
            bubbles = app.query(MessageBubble)
            print("bubbles after send:", len(list(bubbles)))
            if len(list(bubbles)) >= 2:
                print("send_message OK (user + assistant bubbles present)")
            else:
                print("send_message partial - bubbles:", len(list(bubbles)))
        except Exception as e:
            print("send_message ERR:", type(e).__name__, e)
        # Try switching to settings via leader key sequence
        try:
            await pilot.press("space")
            await pilot.pause()
            print("leader key OK")
        except Exception as e:
            print("leader key ERR:", e)
        # Try the plugins leader key (space, p)
        try:
            app.switch_screen("plugins")
            await pilot.pause(0.5)
            plugins_screen = app.query_one("#plugins_screen")
            print("switch to plugins OK, display=", plugins_screen.display)
            app.switch_screen("settings")
            await pilot.pause(0.5)
            settings_screen = app.query_one("#settings_screen")
            print("switch to settings OK, display=", settings_screen.display)
            app.switch_screen("tools")
            await pilot.pause(0.5)
            tools_screen = app.query_one("#tools_screen")
            print("switch to tools OK, display=", tools_screen.display)
            app.switch_screen("chat")
            await pilot.pause(0.5)
        except Exception as e:
            print("screen switch ERR:", type(e).__name__, e)
        await pilot.pause(0.3)
    print("=== smoke test complete ===")


if __name__ == "__main__":
    try:
        asyncio.run(smoke())
    except Exception as e:
        print("FATAL:", type(e).__name__, e)
        import traceback
        traceback.print_exc()
        sys.exit(1)
