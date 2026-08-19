#!/usr/bin/env python3
"""Start backend as daemon and test health."""
import asyncio
import subprocess
import sys
import time
import signal
import os

async def main():
    # Start backend
    backend_dir = r"D:\ELE\backend"
    python_exe = r"E:\ANACONDA\envs\ele-agent\python.exe"
    
    proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # Windows
    )
    
    print(f"Started backend PID: {proc.pid}")
    
    # Wait for startup
    for i in range(15):
        await asyncio.sleep(1)
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://127.0.0.1:8000/health", timeout=3.0)
                if resp.status_code == 200:
                    print(f"Health OK: {resp.json()}")
                    break
        except Exception as e:
            if i % 3 == 0:
                print(f"  waiting... ({i+1}/15)")
    else:
        print("Health check failed after 15s")
        stdout, stderr = proc.communicate(timeout=2)
        print("STDOUT:", stdout.decode()[:500] if stdout else "empty")
        print("STDERR:", stderr.decode()[:500] if stderr else "empty")
        return 1
    
    # Test login
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            r = await client.post("http://127.0.0.1:8000/api/v1/login", 
                json={"email": "ele@example.com", "password": "x"}, timeout=10)
            print(f"Login OK: {r.json()}")
    except Exception as e:
        print(f"Login ERR: {e}")
    
    print("Backend running. Press Ctrl+C to stop.")
    
    # Keep alive
    try:
        while True:
            await asyncio.sleep(5)
            if proc.poll() is not None:
                print(f"Backend exited with code {proc.returncode}")
                stdout, stderr = proc.communicate()
                print("STDERR:", stderr.decode()[:500] if stderr else "empty")
                break
    except KeyboardInterrupt:
        print("Stopping backend...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))