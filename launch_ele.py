#!/usr/bin/env python3
"""ELE Agent - Universal Launcher"""
import subprocess
import sys
import os
import time
import httpx
import threading

def main():
    os.chdir(r"D:\ELE")
    
    print("Starting ELE Agent...", flush=True)
    
    # Kill existing python processes
    os.system("taskkill /f /im python.exe >nul 2>&1")
    time.sleep(2)
    
    # Start backend in background thread (detached)
    backend_dir = r"D:\ELE\backend"
    python_exe = r"E:\ANACONDA\envs\ele-agent\python.exe"
    
    proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"],
        cwd=backend_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    )
    
    print(f"Backend started PID: {proc.pid}", flush=True)
    
    # Wait for startup
    for i in range(30):
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get("http://127.0.0.1:8000/health")
                if resp.status_code == 200:
                    print("Backend ready!", flush=True)
                    break
        except Exception:
            pass
        time.sleep(2)
    else:
        print("Backend failed to start!", flush=True)
        return 1
    
    print("Backend ready! Starting CLI...", flush=True)
    
    # Launch CLI (blocks)
    cli_proc = subprocess.Popen(
        [r"E:\ANACONDA\envs\ele-agent\python.exe", "-m", "src.app"],
        cwd=r"D:\ELE\cli",
    )
    
    # Wait for CLI to exit
    cli_proc.wait()
    
    # Cleanup
    proc.terminate()
    print("ELE Agent stopped.")
    return 0

if __name__ == "__main__":
    sys.exit(main())