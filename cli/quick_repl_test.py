"""Quick test for direct LLM stream"""
import asyncio
from src import llm

async def test():
    print("Testing direct stream_response with 'hi'...")
    full = ""
    async for evt in llm.stream_response([{"role": "user", "content": "hi"}], provider="auto"):
        if evt.type == "model_info":
            print(f"Model: {evt.model}")
        elif evt.type == "delta":
            print(evt.content, end="", flush=True)
            full += evt.content
        elif evt.type == "error":
            print(f"\n[ERROR] {evt.content}")
        elif evt.type == "final":
            print(f"\n[FINAL] (len={len(evt.content)})")
    print(f"\nDone! Received {len(full)} chars.")

if __name__ == "__main__":
    asyncio.run(test())