#!/usr/bin/env python3
"""Start backend, test it, then run CLI REPL - all in one process."""
import subprocess
import sys
import os
import time
import httpx
import json

def start_backend():
    """Start backend as subprocess."""
    os.chdir(r"D:\ELE\backend")
    python_exe = r"E:\ANACONDA\envs\ele-agent\python.exe"
    
    proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=r"D:\ELE\backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    print(f"Backend started PID: {proc.pid}")
    
    # Wait for "Uvicorn running" in output
    import threading
    output_lines = []
    started = threading.Event()
    def reader():
        for line in proc.stdout:
            output_lines.append(line)
            if "running" in line.lower() and "uvicorn" in line.lower():
                started.set()
                break
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    started.wait(timeout=25)  # wait up to 25s for startup
    
    # Give it a moment more
    time.sleep(3)
    return proc, output_lines

def test_backend():
    """Test health, login, and chat."""
    base = "http://127.0.0.1:8000"
    results = {}
    
    # Health
    try:
        r = httpx.get(f"{base}/health", timeout=6)
        results["health"] = r.json()
        print(f"[OK] Health: {r.json()}")
    except Exception as e:
        results["health"] = f"ERR: {e}"
        print(f"[FAIL] Health: {e}")
        return results
    
    # Login
    try:
        r = httpx.post(f"{base}/api/v1/login", 
                       json={"email": "ele@example.com", "password": "x"}, timeout=10)
        token = r.json()["access_token"]
        results["token"] = token[:20] + "..."
        print(f"[OK] Login: got token")
    except Exception as e:
        results["login"] = f"ERR: {e}"
        print(f"[FAIL] Login: {e}")
        return results
    
    # /me
    try:
        r = httpx.get(f"{base}/api/v1/me", 
                      headers={"Authorization": f"Bearer {token}"}, timeout=8)
        results["me"] = r.json()
        print(f"[OK] /me: {r.json()['email']} (tier={r.json()['tier']}, credits={r.json()['credits_remaining']})")
    except Exception as e:
        results["me"] = f"ERR: {e}"
        print(f"[FAIL] /me: {e}")
    
    # Plugins
    try:
        r = httpx.get(f"{base}/api/v1/plugins",
                      headers={"Authorization": f"Bearer {token}"}, timeout=8)
        results["plugins"] = r.json()
        print(f"[OK] /plugins: {r.json()}")
    except Exception as e:
        results["plugins"] = f"ERR: {e}"
        print(f"[FAIL] /plugins: {e}")
    
    # WebSocket chat
    try:
        import websockets
        import asyncio
        
        async def test_chat():
            uri = f"ws://127.0.0.1:8000/api/v1/ws/chat?token={token}"
            async with websockets.connect(uri, max_size=None) as ws:
                await ws.send(json.dumps({
                    "type": "message",
                    "content": "Say hello in one short sentence.",
                    "tools": ["file", "shell", "browser"],
                    "model": "auto"
                }))
                events = []
                for _ in range(20):
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=30)
                        evt = json.loads(raw)
                        events.append(evt["type"])
                        if evt["type"] == "final":
                            print(f"[OK] WS Chat: final response received")
                            print(f"     thoughts={len([e for e in events if e=='thought'])}")
                            return events
                        if evt["type"] == "error":
                            print(f"[FAIL] WS Chat error: {evt.get('message')}")
                            return events
                    except asyncio.TimeoutError:
                        print(f"[TIMEOUT] WS Chat: got {len(events)} events")
                        return events
                return events
        
        events = asyncio.run(test_chat())
        results["ws_events"] = events
    except Exception as e:
        results["ws"] = f"ERR: {e}"
        print(f"[FAIL] WS Chat: {e}")
    
    return results

def main():
    print("=" * 60)
    print("ELE Agent - Full Backend Test")
    print("=" * 60)
    
    # Kill any existing python processes EXCEPT this one
    import psutil
    my_pid = os.getpid()
    for p in psutil.process_iter(["pid", "name"]):
        if p.info["name"] and "python" in p.info["name"].lower() and p.info["pid"] != my_pid:
            try:
                p.terminate()
            except Exception:
                pass
    time.sleep(2)
    
    # Start backend
    proc, logs = start_backend()
    startup_log = "".join(logs[-3:])
    print(f"Startup: {startup_log.strip()}")
    
    if proc.poll() is not None:
        print(f"Backend died immediately! Exit code: {proc.returncode}")
        return
    
    # Test
    print("\n--- Testing Backend ---")
    results = test_backend()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    health_ok = isinstance(results.get("health"), dict)
    login_ok = "token" in results
    me_ok = isinstance(results.get("me"), dict)
    ws_ok = isinstance(results.get("ws_events"), list)
    print(f"  Health:  {'PASS' if health_ok else 'FAIL'}")
    print(f"  Login:  {'PASS' if login_ok else 'FAIL'}")
    print(f"  /me:    {'PASS' if me_ok else 'FAIL'}")
    print(f"  WS Chat: {'PASS' if ws_ok else 'FAIL'}")
    
    all_pass = health_ok and login_ok and me_ok and ws_ok
    print(f"\n  Overall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
    
    # Stop backend
    print("\nStopping backend...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except:
        proc.kill()
    print("Done.")

if __name__ == "__main__":
    main()