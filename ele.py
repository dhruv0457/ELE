#!/usr/bin/env python3
"""
ELE Agent — Developer AI Terminal Assistant
Usage:
  ele                  Launch direct interactive terminal REPL (default)
  ele tui              Launch full-screen TUI interface
  ele setup            Interactive API key wizard
  ele keys             Show API key status
  ele backend          Start backend server
  ele version          Show version
"""
import sys
import os

# Ensure safe UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    args = sys.argv[1:]
    cmd = args[0].lower() if args else ""

    if cmd in ("version", "--version", "-v"):
        print("ELE Agent v1.0.0 — AI Autonomous Developer & OS Copilot")
        return

    if cmd in ("setup", "init"):
        _run_setup()
        return

    if cmd == "backend":
        _start_backend()
        return

    if cmd == "keys":
        _show_keys()
        return

    if cmd in ("repl", "--repl"):
        _launch_repl()
        return

    if cmd in ("tui", "--tui"):
        _launch_tui()
        return

    if cmd in ("help", "--help", "-h"):
        print(__doc__.strip())
        return

    # Default: launch modern High-FPS Visual AI Agent (agy.js)
    _launch_agy(args)


def _launch_agy(pass_args=None):
    """Launch the Next-Gen Zero-Latency TUI & Automation Copilot."""
    import subprocess
    agy_script = os.path.join(os.path.dirname(__file__), "cli", "agy.js")
    if not os.path.isfile(agy_script):
        agy_script = os.path.join(os.path.dirname(__file__), "..", "first_cli", "app", "agy.js")

    if os.path.isfile(agy_script):
        try:
            cmd = ["node", agy_script]
            if pass_args:
                cmd.extend(pass_args)
            subprocess.run(cmd)
        except FileNotFoundError:
            print("[ELE] Node.js is required for the modern terminal UI.")
            print("[ELE] Falling back to standard REPL...")
            _launch_repl()
    else:
        print("[ELE] Modern TUI script not found. Launching standard REPL...")
        _launch_repl()


def _launch_repl():
    """Instant Terminal REPL launch — 0ms container lag."""
    src_dir = os.path.join(os.path.dirname(__file__), "cli")
    if os.path.isdir(src_dir):
        sys.path.insert(0, src_dir)

    try:
        from src.repl import run_repl
        run_repl()
    except ImportError as e:
        print(f"[ELE] Import error: {e}")
        print("[ELE] Run: pip install -r cli/requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        pass


def _launch_tui():
    """Full-screen TUI launch."""
    src_dir = os.path.join(os.path.dirname(__file__), "cli")
    if os.path.isdir(src_dir):
        sys.path.insert(0, src_dir)

    try:
        from src.app import main as tui_main
        tui_main()
    except ImportError as e:
        print(f"[ELE] Import error: {e}")
        print("[ELE] Run: pip install -r cli/requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        pass


def _start_backend():
    """Start FastAPI backend in foreground."""
    import subprocess
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    if not os.path.isdir(backend_dir):
        print("[ELE] No backend directory found.")
        return
    print("[ELE] Starting backend on http://localhost:8000 ...")
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app",
             "--host", "127.0.0.1", "--port", "8000",
             "--log-level", "info", "--reload"],
            cwd=backend_dir,
        )
    except KeyboardInterrupt:
        print("\n[ELE] Backend stopped.")


def _run_setup():
    """First-time interactive setup."""
    from pathlib import Path
    import getpass

    print("\n⚡ ELE Agent Setup\n" + "─" * 40)
    env_path = Path.home() / ".ele-agent" / ".env"
    env_path.parent.mkdir(parents=True, exist_ok=True)

    existing = {}
    if env_path.exists():
        for line in env_path.read_text("utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                existing[k.strip()] = v.strip()

    key_prompts = [
        ("NVIDIA_API_KEY", "NVIDIA API Key (nvapi-...)", "🚀 Fastest — llama-3.3-70b (Free at build.nvidia.com)"),
        ("GEMINI_API_KEY", "Gemini API Key (AIza...)", "Gemini 2.0 Flash"),
        ("OPENAI_API_KEY", "OpenAI API Key (sk-...)", "GPT-4o / GPT-4o-mini"),
        ("ANTHROPIC_API_KEY", "Anthropic API Key (sk-ant-...)", "Claude 3.5 Sonnet"),
        ("GROQ_API_KEY", "Groq API Key (gsk_...)", "Free & ultra fast"),
    ]

    print("Enter API keys (press Enter to skip):\n")
    for env_key, prompt, note in key_prompts:
        current = existing.get(env_key, "")
        masked = current[:4] + "••••" if current else "(not set)"
        try:
            val = getpass.getpass(f"  {prompt} [{masked}] ({note}): ")
            if val.strip():
                existing[env_key] = val.strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[Setup] Aborted.")
            return

    lines = [f"{k}={v}" for k, v in existing.items()]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n✅ Keys saved to {env_path}")
    print("🚀 Run `ele` to start!\n")


def _show_keys():
    """Show current API key status."""
    from pathlib import Path

    env_path = Path.home() / ".ele-agent" / ".env"
    keys = {}
    for path in [env_path, Path(__file__).parent / ".env"]:
        if path.exists():
            for line in path.read_text("utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    if v.strip():
                        keys[k.strip()] = v.strip()

    print("\n⚡ ELE Agent — API Keys\n" + "─" * 40)
    for env_key, label in [
        ("NVIDIA_API_KEY", "NVIDIA"),
        ("GEMINI_API_KEY", "Gemini"),
        ("OPENAI_API_KEY", "OpenAI"),
        ("ANTHROPIC_API_KEY", "Anthropic"),
        ("GROQ_API_KEY", "Groq"),
    ]:
        val = keys.get(env_key, "")
        if val:
            masked = val[:4] + "•" * 8 + val[-4:] if len(val) > 8 else "••••"
            print(f"  ✅ {label:<14} {masked}")
        else:
            print(f"  ❌ {label:<14} (not set)")
    print(f"\n  📁 Config: {env_path}")
    print("  Run `ele setup` to add keys.\n")


if __name__ == "__main__":
    main()
