#!/usr/bin/env python3
"""
ELE Agent - Universal Installer
Run once: curl -sSL https://raw.githubusercontent.com/your-repo/ele/main/install.py | python
Or download and run: python install.py
"""
import os
import sys
import subprocess
import shutil
import winreg
import urllib.request
import zipfile
import tempfile
from pathlib import Path

# Configuration
REPO_URL = "https://github.com/your-username/ele-agent/archive/refs/heads/main.zip"
ELE_ROOT = Path.home() / ".ele"
PYTHON_URL = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
CONDA_ENV_NAME = "ele-agent"

class ELEInstaller:
    def __init__(self):
        self.ele_root = ELE_ROOT
        self.bin_dir = ELE_ROOT / "bin"
        self.project_dir = ELE_ROOT / "project"
        self.python_exe = None
        
    def log(self, msg, level="info"):
        colors = {"info": "\033[94m", "success": "\033[92m", "warning": "\033[93m", "error": "\033[91m", "reset": "\033[0m"}
        color = colors.get(level, "")
        reset = colors["reset"]
        print(f"{color}[{level.upper()}]{reset} {msg}")

    def run_cmd(self, cmd, cwd=None, shell=False):
        """Run command and return result."""
        try:
            result = subprocess.run(cmd, cwd=cwd, shell=shell, capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def check_python(self):
        """Find or install Python."""
        # Check for existing conda env
        conda_paths = [
            Path(os.environ.get("CONDA_PREFIX", "")) / "envs" / CONDA_ENV_NAME,
            Path(os.environ.get("USERPROFILE", "")) / "miniconda3" / "envs" / CONDA_ENV_NAME,
            Path(os.environ.get("USERPROFILE", "")) / "anaconda3" / "envs" / CONDA_ENV_NAME,
            Path("E:/ANACONDA/envs") / CONDA_ENV_NAME,
        ]
        
        for p in conda_paths:
            python_exe = p / "python.exe"
            if python_exe.exists():
                self.python_exe = str(python_exe)
                self.log(f"Found existing conda env: {self.python_exe}")
                return True
        
        # Check system python
        for cmd in ["python", "python3", "py"]:
            ok, out, _ = self.run_cmd([cmd, "--version"])
            if ok:
                self.python_exe = cmd
                self.log(f"Found system Python: {out.strip()}")
                return True
        
        return False

    def install_miniconda(self):
        """Install Miniconda if needed."""
        self.log("Installing Miniconda...")
        installer = Path(tempfile.gettempdir()) / "miniconda_installer.exe"
        
        self.log("Downloading Miniconda installer...")
        urllib.request.urlretrieve(PYTHON_URL, installer)
        
        self.log("Installing Miniconda silently...")
        ok, out, err = self.run_cmd([
            str(installer), "/S", "/D=" + str(Path.home() / "miniconda3")
        ])
        
        if not ok:
            self.log(f"Miniconda install failed: {err}", "error")
            return False
            
        # Add to PATH for this session
        conda_bin = Path.home() / "miniconda3" / "Scripts"
        os.environ["PATH"] = str(conda_bin) + ";" + os.environ["PATH"]
        
        return True

    def create_conda_env(self):
        """Create conda environment with all dependencies."""
        self.log(f"Creating conda environment '{CONDA_ENV_NAME}'...")
        
        conda_exe = "conda"
        if not shutil.which("conda"):
            conda_path = Path.home() / "miniconda3" / "Scripts" / "conda.exe"
            if conda_path.exists():
                conda_exe = str(conda_path)
        
        # Create env
        ok, out, err = self.run_cmd([conda_exe, "create", "-n", CONDA_ENV_NAME, "python=3.11", "-y"])
        if not ok:
            self.log(f"Conda env creation failed: {err}", "error")
            return False
        
        # Install dependencies
        pip_exe = f"conda run -n {CONDA_ENV_NAME} pip"
        deps = [
            "fastapi", "uvicorn", "pydantic", "pydantic-settings",
            "httpx", "websockets", "sqlalchemy", "aiosqlite",
            "langgraph", "langchain-core",
            "faiss-cpu", "sentence-transformers", "rank-bm25",
            "openai", "google-generativeai", "anthropic",
            "structlog", "python-dotenv", "tomli", "tomli-w",
            "textual", "rich", "watchfiles", "pyyaml",
        ]
        
        self.log("Installing Python dependencies...")
        ok, out, err = self.run_cmd(f"{pip_exe} install {' '.join(deps)}", shell=True)
        if not ok:
            self.log(f"Pip install failed: {err}", "error")
            return False
        
        # Find python exe
        ok, out, _ = self.run_cmd(["conda", "run", "-n", CONDA_ENV_NAME, "python", "-c", "import sys; print(sys.executable)"])
        if ok:
            self.python_exe = out.strip()
            self.log(f"Python executable: {self.python_exe}")
            return True
        
        return False

    def download_project(self):
        """Copy project from local source (since we're already in the repo)."""
        self.log("Setting up project from local source...")
        
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy from current working directory if not already there
        source_dir = Path.cwd()
        if source_dir != self.project_dir:
            self.log("Copying project files...")
            for item in source_dir.iterdir():
                if item.name in ['.git', '__pycache__', '.venv', 'venv', 'env', '.conda', '*.db', '*.sqlite']:
                    continue
                dest = self.project_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        
        self.log("Project ready")
        return True

    def setup_config(self):
        """Setup configuration files."""
        backend_dir = self.project_dir / "backend"
        env_file = backend_dir / ".env"
        
        if not env_file.exists():
            env_example = backend_dir / ".env.example"
            if env_example.exists():
                shutil.copy(env_example, env_file)
                self.log("Created .env from example")
            else:
                # Create minimal .env
                env_content = """# ELE Agent Configuration
DEBUG=True
NVIDIA_API_KEY=your-nvidia-api-key-here
# OPENAI_API_KEY=
# GEMINI_API_KEY=
# GROQ_API_KEY=
# ANTHROPIC_API_KEY=
"""
                env_file.write_text(env_content)
                self.log("Created minimal .env file")
        
        # Create CLI config dir
        cli_config_dir = Path.home() / ".ele-agent"
        cli_config_dir.mkdir(parents=True, exist_ok=True)
        
        return True

    def create_global_command(self):
        """Create global 'ele' command."""
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Windows batch file
        ele_bat = self.bin_dir / "ele.bat"
        bat_content = f'''@echo off
REM ELE Agent - Global Launcher
cd /d {self.project_dir}

echo Starting ELE Agent...

REM Kill any existing python processes
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start backend in NEW window
start "ELE Backend" cmd /c "{self.python_exe} -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info"

REM Wait for backend to be ready using PowerShell
echo Waiting for backend to start...
powershell -Command "$maxAttempts = 30; $attempt = 0; do {{ Start-Sleep -Seconds 2; $attempt++; try {{ $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 3 -ErrorAction Stop; if ($response.StatusCode -eq 200) {{ exit 0 }} }} catch {{ }} }} while ($attempt -lt $maxAttempts); exit 1"
if errorlevel 1 (
    echo Backend failed to start!
    pause
    exit /b 1
)

echo Backend ready! Starting CLI...

REM Launch CLI in THIS window
{self.python_exe} -m src.app
'''
        ele_bat.write_text(bat_content)
        
        # PowerShell version
        ele_ps1 = self.bin_dir / "ele.ps1"
        ps1_content = f'''# ELE Agent - Single Command Launcher (PowerShell)
Write-Host "Starting ELE Agent..." -ForegroundColor Cyan

Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

$backendJob = Start-Job -ScriptBlock {{
    Set-Location "{self.project_dir / "backend"}"
    & "{self.python_exe}" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info
}}

Write-Host "Backend job started (Job ID: $($backendJob.Id))" -ForegroundColor Green

$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt 30 -and -not $ready) {{
    Start-Sleep -Seconds 2
    $attempt++
    try {{
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {{ $ready = $true }}
    }} catch {{ }}
}}

if (-not $ready) {{
    Write-Host "Backend failed to start!" -ForegroundColor Red
    $backendJob | Remove-Job -Force
    Read-Host "Press Enter to exit"
    exit 1
}}

Write-Host "Backend ready! Starting CLI..." -ForegroundColor Green

& "{self.python_exe}" -m src.app

Get-Job | Remove-Job -Force
Write-Host "ELE Agent stopped." -ForegroundColor Cyan
'''
        ele_ps1.write_text(ps1_content)
        
        # Add to PATH
        self.add_to_path(str(self.bin_dir))
        self.log(f"Created global 'ele' command in {self.bin_dir}")
        return True

    def add_to_path(self, path):
        """Add directory to user PATH."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            if path not in current_path:
                new_path = current_path + ";" + path if current_path else path
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                self.log(f"Added to PATH: {path}")
        except Exception as e:
            self.log(f"Failed to update PATH: {e}", "warning")
        finally:
            try:
                winreg.CloseKey(key)
            except:
                pass

    def verify_installation(self):
        """Verify everything works."""
        self.log("Verifying installation...")
        
        # Check Python
        ok, out, _ = self.run_cmd([self.python_exe, "-c", "import sys; print('Python OK')"])
        if not ok:
            self.log("Python verification failed", "error")
            return False
        
        # Check project structure
        if not (self.project_dir / "backend").exists():
            self.log("Backend directory missing", "error")
            return False
        if not (self.project_dir / "cli").exists():
            self.log("CLI directory missing", "error")
            return False
        
        self.log("All verifications passed!")
        return True

    def run(self):
        """Main installation flow."""
        print("=" * 60)
        print("  ELE Agent - Universal Installer")
        print("=" * 60)
        
        # Step 1: Check/Install Python
        self.log("Step 1: Checking Python environment...")
        if not self.check_python():
            self.log("No suitable Python found. Installing Miniconda...")
            if not self.install_miniconda():
                return False
            if not self.create_conda_env():
                return False
        else:
            self.log("Python environment found!")
        
        # Step 2: Download project
        self.log("Step 2: Downloading ELE Agent from GitHub...")
        if not self.download_project():
            return False
        
        # Step 3: Setup config
        self.log("Step 3: Setting up configuration...")
        if not self.setup_config():
            return False
        
        # Step 4: Create global command
        self.log("Step 4: Creating global 'ele' command...")
        if not self.create_global_command():
            return False
        
        # Step 5: Verify
        self.log("Step 5: Verifying installation...")
        if not self.verify_installation():
            return False
        
        # Success!
        print("\n" + "=" * 60)
        print("  INSTALLATION COMPLETE!")
        print("=" * 60)
        print(f"\nRestart your terminal, then run:")
        print(f"  ele")
        print(f"\nOr from PowerShell:")
        print(f"  ele")
        print(f"\nThis will:")
        print(f"  1. Start backend (auto-detects NVIDIA API key from .env)")
        print(f"  2. Launch CLI TUI with professional UI")
        print(f"  3. Auto-connect and chat immediately")
        print(f"\nProject location: {self.project_dir}")
        print(f"Global command: ele (restart terminal first)")
        return True


def main():
    installer = ELEInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()