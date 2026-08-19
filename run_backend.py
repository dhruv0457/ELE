#!/usr/bin/env python3
"""Run backend server - stays alive until interrupted."""
import sys
import subprocess
import os

if __name__ == "__main__":
    os.chdir(r"D:\ELE\backend")
    python_exe = r"E:\ANACONDA\envs\ele-agent\python.exe"
    
    # Run uvicorn directly - this blocks until Ctrl+C
    subprocess.run([
        python_exe, "-m", "uvicorn", "app.main:app",
        "--host", "127.0.0.1", "--port", "8000"
    ], check=False)