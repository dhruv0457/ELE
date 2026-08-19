#!/usr/bin/env python3
"""
ELE Agent - Global Installer
Run once: python install_ele.py
Then use 'ele' from anywhere.
"""
import os
import sys
import subprocess
import shutil
import winreg
from pathlib import Path

ELE_ROOT = Path(r"D:\ELE")
PYTHON_EXE = r"E:\ANACONDA\envs\ele-agent\python.exe"
CLI_DIR = ELE_ROOT / "cli"
BACKEND_DIR = ELE_ROOT / "backend"

def add_to_path(new_path):
    """Add directory to user PATH environment variable."""
    try:
        # Get current user PATH
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""
        
        if new_path not in current_path:
            new_path_value = current_path + ";" + new_path if current_path else new_path
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path_value)
            print(f"Added to PATH: {new_path}")
            return True
        else:
            print(f"Already in PATH: {new_path}")
            return False
    except Exception as e:
        print(f"Failed to update PATH: {e}")
        return False
    finally:
        try:
            winreg.CloseKey(key)
        except:
            pass

def create_ele_script():
    """Create ele.bat wrapper in a bin folder."""
    bin_dir = Path.home() / ".ele" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    ele_bat = bin_dir / "ele.bat"
    content = f'''@echo off
REM ELE Agent - Global Launcher
cd /d {ELE_ROOT}
{ELE_ROOT / "launch_ele.py"} %*
'''
    ele_bat.write_text(content)
    print(f"Created: {ele_bat}")
    return str(bin_dir)

def create_ele_ps1():
    """Create ele.ps1 for PowerShell."""
    bin_dir = Path.home() / ".ele" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    ele_ps1 = bin_dir / "ele.ps1"
    content = f'''# ELE Agent - Global Launcher (PowerShell)
Set-Location "{ELE_ROOT}"
& "{PYTHON_EXE}" "{ELE_ROOT / "launch_ele.py"}" $args
'''
    ele_ps1.write_text(content)
    print(f"Created: {ele_ps1}")
    return str(bin_dir)

def install_ele():
    print("=" * 50)
    print("ELE Agent - Global Installer")
    print("=" * 50)
    
    # Verify paths exist
    if not CLI_DIR.exists():
        print(f"ERROR: CLI not found at {CLI_DIR}")
        return False
    if not BACKEND_DIR.exists():
        print(f"ERROR: Backend not found at {BACKEND_DIR}")
        return False
    if not Path(PYTHON_EXE).exists():
        print(f"ERROR: Python not found at {PYTHON_EXE}")
        return False
    
    print(f"ELE Root: {ELE_ROOT}")
    print(f"Python: {PYTHON_EXE}")
    
    # Create wrapper scripts
    bin_dir = create_ele_script()
    create_ele_ps1()
    
    # Add to PATH
    print("\nAdding to user PATH...")
    if add_to_path(bin_dir):
        print("PATH updated! Restart terminal or run:")
        print("  $env:PATH = [Environment]::GetEnvironmentVariable('PATH','User')")
    else:
        print("Already in PATH or update failed.")
    
    # Test installation
    print("\nTesting installation...")
    result = subprocess.run([PYTHON_EXE, "-c", "import sys; print('Python OK')"], capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] Python environment works")
    else:
        print("[FAIL] Python environment issue")
    
    print("\n" + "=" * 50)
    print("Installation Complete!")
    print("=" * 50)
    print("Restart your terminal, then run:")
    print("  ele")
    print("")
    print("Or from PowerShell:")
    print("  ele")
    print("")
    print("This will:")
    print("  1. Start backend (if not running)")
    print("  2. Launch CLI TUI with professional UI")
    print("  3. Auto-connect and chat immediately")
    return True

if __name__ == "__main__":
    success = install_ele()
    sys.exit(0 if success else 1)