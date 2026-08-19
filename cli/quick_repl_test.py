"""Quick REPL test"""
import asyncio
from src import backend as be

async def test():
    print("Backend up:", be.is_backend_up())
    tok = be.login_or_register()
    print("Logged in:", tok["email"])
    print("--- chat ---")
    async for evt in be.stream_chat("Say hi in one sentence.", tok["access_token"]):
        if evt.get("type") in ("final", "error"):
            print(f"{evt['type']}: {evt.get('content', evt.get('message'))[:80]}")
            break

asyncio.run(test())