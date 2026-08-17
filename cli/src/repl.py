"""Simple interactive REPL that talks to the ELE backend.

Run with (from D:\ELE\cli):
    E:\ANACONDA\condabin\conda.bat run -n ele-agent python -m src.repl

It auto-registers a local user, connects to the backend on :8000, and lets
you type messages. Streaming thoughts/tools are printed inline. Type
/quit or press Ctrl-C to exit.
"""
import asyncio
import uuid

from . import backend as be


BANNER = r"""
  ______   __  ______  _   __
 |  ____| / _\|  ____|| | / /
 | |__   / / | |__   | |/ /
 |  __| / /__|  __|  |   <
 | |___/ /  | |_____| |\ \
 |______/   |______ |_| \__\

  ELE Agent - terminal chat. Backend: {url}
  Commands: /quit   /clear   /help
"""


def _print_thought(t):
    print(f"  ◉ {t}")


async def main(host: str = "localhost", port: int = 8000) -> None:
    print(BANNER.format(url=f"http://{host}:{port}"))

    if not be.is_backend_up(host, port):
        print("Backend is NOT running. Start it first with:")
        print("  E:\\ANACONDA\\condabin\\conda.bat run -n ele-agent python -m uvicorn app.main:app --port 8000")
        return

    print("Connecting...", end=" ", flush=True)
    try:
        tok = be.login_or_register(host=host, port=port)
    except Exception as e:
        print(f"failed: {e}")
        return
    print(f"ready. Logged in as {tok['email']}")

    session_id = f"session_{uuid.uuid4().hex[:8]}"
    tools = ["file", "shell", "browser"]

    print("Type a message and press Enter. /quit to exit.\n")

    loop = asyncio.get_event_loop()
    while True:
        try:
            user_text = await loop.run_in_executor(None, lambda: input("you > ").strip())
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return
        if not user_text:
            continue
        if user_text == "/quit":
            print("bye")
            return
        if user_text == "/clear":
            print("\x1b[2J\x1b[H", end="")
            continue
        if user_text == "/help":
            print("/quit /clear /help  - then anything else is sent to the agent.")
            continue

        print("ellie > ", end="", flush=True)
        try:
            async for evt in be.stream_chat(user_text, tok["access_token"], session_id=session_id, tools=tools, host=host, port=port):
                t = evt.get("type")
                if t == "thought":
                    print()
                    _print_thought(evt.get("content", ""))
                    print("ellie > ", end="", flush=True)
                elif t == "tool_start":
                    print(f"\n   🔧 calling {evt.get('tool')}...")
                    print("ellie > ", end="", flush=True)
                elif t == "tool_result":
                    out = evt.get("output") or evt.get("error") or ""
                    if isinstance(out, str):
                        out = out[:300].replace("\n", " ")
                    print(f"     └─ {out}")
                    print("ellie > ", end="", flush=True)
                elif t == "final":
                    content = evt.get("content", "")
                    print(f"\n{content}" if not content.startswith("\n") else content)
                    meta = evt.get("metadata", {}) or {}
                    if meta.get("tools_used"):
                        print(f"   tools used: {', '.join(meta['tools_used'])}")
                elif t == "error":
                    print(f"\n[error] {evt.get('message','unknown')}")
        except Exception as e:
            print(f"\n[error] {e}")
        print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nbye")
