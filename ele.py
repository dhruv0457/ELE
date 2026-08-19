#!/usr/bin/env python3
"""
ELE Agent — Instant CLI launcher
Usage:
  ele                  Launch the TUI
  ele chat             Launch directly in chat mode
  ele backend          Start only the backend server
  ele setup            Interactive first-time setup
  ele keys             Show/set API keys
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
    cmd = args[0].lower() if args else "tui"

    if cmd in ("version", "--version", "-v"):
        print("ELE Agent v1.0.0")
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

    if cmd in ("help", "--help", "-h"):
        print(__doc__.strip())
        return

    # Default: launch TUI
    _launch_tui()


def _launch_tui():
    """Instant TUI launch — no delays, no blocking."""
    # Ensure we're using the project's cli/src directory
    src_dir = os.path.join(os.path.dirname(__file__), "cli", "src")
    if os.path.isdir(src_dir):
        sys.path.insert(0, os.path.dirname(src_dir))

    try:
        from cli.src.app import main as tui_main
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
        ("NVIDIA_API_KEY", "NVIDIA API Key (nvapi-...)", "🚀 Fastest — llama-3.3-70b"),
        ("OPENAI_API_KEY", "OpenAI API Key (sk-...)", "GPT-4o"),
        ("GEMINI_API_KEY", "Gemini API Key (AIza...)", "Gemini 2.0 Flash"),
        ("ANTHROPIC_API_KEY", "Anthropic API Key (sk-ant-...)", "Claude 3.5"),
        ("GROQ_API_KEY", "Groq API Key (gsk_...)", "Free & fast"),
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
        ("OPENAI_API_KEY", "OpenAI"),
        ("GEMINI_API_KEY", "Gemini"),
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
