"""
ELE Agent — Direct Terminal REPL (Developer Minimalist)
Runs directly in your native terminal with zero container lag, rich streaming,
inline tool execution, and dynamic model routing.
"""
import sys
import os
import asyncio
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Windows terminal UTF-8 safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.theme import Theme

from . import llm as engine
from .store import store, Message, Session

# Custom Developer Minimalist Theme
custom_theme = Theme({
    "prompt": "bold green",
    "header": "bold cyan",
    "info": "dim white",
    "thought": "italic magenta",
    "tool": "bold yellow",
    "tool_done": "bold green",
    "error": "bold red",
    "status": "dim",
    "code": "bright_cyan",
})

console = Console(theme=custom_theme, highlight=False)


# ── Complexity & Intent Analyzer ─────────────────────────────────────────────

REASONING_KEYWORDS = {
    "refactor", "architect", "design", "debug", "proof", "algorithm",
    "complex", "optimize", "analyze", "deep", "step by step", "plan",
    "concurrency", "distributed", "race condition", "memory leak"
}

def analyze_prompt_tier(prompt: str) -> str:
    """Classify prompt into 'fast' or 'deep' reasoning tier."""
    p_lower = prompt.lower()
    word_count = len(prompt.split())
    if word_count > 80 or any(k in p_lower for k in REASONING_KEYWORDS):
        return "deep"
    return "fast"


def get_tier_models(tier: str) -> List[Tuple[str, str]]:
    """Return prioritized (provider, model) list for the given tier."""
    engine.reload_keys()
    if tier == "deep":
        candidates = [
            ("nvidia", "deepseek-ai/deepseek-r1"),
            ("anthropic", "claude-3-5-sonnet-20241022"),
            ("openai", "gpt-4o"),
            ("gemini", "gemini-1.5-pro"),
            ("nvidia", "meta/llama-3.3-70b-instruct"),
            ("groq", "llama-3.3-70b-versatile"),
        ]
    else:  # fast tier
        candidates = [
            ("nvidia", "meta/llama-3.3-70b-instruct"),
            ("gemini", "gemini-2.0-flash-exp"),
            ("groq", "llama-3.3-70b-versatile"),
            ("openai", "gpt-4o-mini"),
            ("anthropic", "claude-3-haiku-20240307"),
            ("ollama", "llama3"),
        ]

    # Filter to providers with active API keys (or ollama fallback)
    available = []
    for provider, model in candidates:
        if provider == "ollama":
            available.append((provider, model))
        else:
            key_name = f"{provider.upper()}_API_KEY"
            if engine._KEYS.get(key_name):
                available.append((provider, model))

    if not available:
        available.append(("none", "no-key-set"))
    return available


# ── Banner & Help ─────────────────────────────────────────────────────────────

def print_banner() -> None:
    engine.reload_keys()
    provider, model = engine.get_best_provider()
    model_name = model.split("/")[-1] if model else "none"
    key_count = sum(1 for k in ["NVIDIA_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY"] if engine._KEYS.get(k))

    console.print()
    console.print("[bold cyan]⚡ ELE Agent[/] [dim]v1.0.0[/] — [dim]Developer AI Terminal[/]")
    console.print(f"[dim]Active Provider:[/] [bold green]{provider.upper()}[/] [dim]({model_name})[/]  │  [dim]Keys Loaded:[/] [bold green]{key_count}[/]")
    console.print("[dim]Type your message, prompt, or task. Type [bold cyan]/help[/] for commands.[/]")
    console.print()


def print_help() -> None:
    help_text = """
[bold cyan]ELE Agent Commands & Shortcuts[/]
  [bold green]/help[/]              Show this help menu
  [bold green]/model <name>[/]     Switch active AI model (/model nvidia, /model gemini, /model auto)
  [bold green]/theme <name>[/]     Switch theme (dark, monochrome, cyberpunk, minimal, matrix, light)
  [bold green]/compact[/]          Toggle compact developer layout mode
  [bold green]/new[/] or [bold green]/session[/]    Start a fresh conversation session
  [bold green]/clear[/]             Clear terminal screen
  [bold green]/screen [prompt][/]  Capture active screen & analyze with multimodal vision
  [bold green]/voice[/]             Activate interactive microphone voice mode
  [bold green]/keys[/]              Inspect loaded API keys status
  [bold green]/status[/]            System diagnostics & provider connection
  [bold green]/models[/]            List available providers and models
  [bold green]/browse <url>[/]     Open a URL in browser
  [bold green]/shell <cmd>[/]      Run a shell command directly
  [bold green]/setup[/]             Run interactive API key setup
  [bold green]/exit[/] or [bold green]/quit[/]     Exit ELE Agent
"""
    console.print(help_text.strip())
    console.print()


# ── REPL Session Loop ─────────────────────────────────────────────────────────

class TerminalREPL:
    def __init__(self):
        self.session = store.create_session("Terminal Session")
        self.conversation: List[Dict[str, str]] = []
        self.active_provider: Optional[str] = None
        self.active_model: Optional[str] = None
        self.manual_override: bool = False

    async def start(self) -> None:
        print_banner()

        while True:
            try:
                # Prompt
                active_p = self.active_provider or "auto"
                prompt_label = f"[bold green]❯[/] "
                user_input = await self._get_input(prompt_label)
                if user_input is None:
                    break

                text = user_input.strip()
                if not text:
                    continue

                # Slash commands
                if text.startswith("/"):
                    handled = await self._handle_command(text)
                    if handled == "exit":
                        break
                    continue

                # Process query
                await self._process_message(text)

            except KeyboardInterrupt:
                console.print("\n[dim]Use /exit or Ctrl+D to quit.[/]")
                continue
            except EOFError:
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/] {e}")

        console.print("\n[dim]ELE Agent session ended. Goodbye![/]\n")

    async def _get_input(self, prompt: str) -> Optional[str]:
        """Async safe input reader."""
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, input, "❯ ")
        except (EOFError, KeyboardInterrupt):
            return None

    async def _handle_command(self, cmd: str) -> Optional[str]:
        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if action in ("/exit", "/quit", "/q"):
            return "exit"

        if action == "/help":
            print_help()
            return "ok"

        if action == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
            print_banner()
            return "ok"

        if action == "/new" or action == "/session":
            self.session = store.create_session("Terminal Session")
            self.conversation.clear()
            console.print("[dim green]✓ New session initialized.[/]")
            return "ok"

        if action == "/theme":
            valid_themes = ["dark", "monochrome", "cyberpunk", "minimal", "matrix", "light"]
            if not arg or arg.lower() not in valid_themes:
                console.print(f"[dim]Usage: /theme <{'|'.join(valid_themes)}>[/]")
                return "ok"
            t = arg.lower()
            if t == "monochrome":
                console._theme = Theme({"prompt": "bold white", "header": "bold white", "code": "white", "tool": "dim white", "tool_done": "bold white"})
            elif t == "cyberpunk":
                console._theme = Theme({"prompt": "bold #ff007f", "header": "bold #00ffff", "code": "#00ffcc", "tool": "bold #39ff14", "tool_done": "bold #00ffff"})
            elif t == "matrix":
                console._theme = Theme({"prompt": "bold green", "header": "bold #22c55e", "code": "#4ade80", "tool": "bold #15803d", "tool_done": "bold #22c55e"})
            else:
                console._theme = custom_theme
            console.print(f"[dim green]✓ Terminal theme set to [bold]{t.upper()}[/].[/]")
            return "ok"

        if action == "/compact":
            console.print("[dim green]✓ Compact developer density mode toggled.[/]")
            return "ok"

        if action == "/screen":
            console.print("[dim cyan]📸 Capturing screen for vision analysis...[/]")
            try:
                from PIL import ImageGrab
                import io, base64
                img = ImageGrab.grab()
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=80)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                console.print(f"[dim green]✓ Screen captured ({img.width}x{img.height}). Sending to vision model...[/]")
                prompt = arg if arg else "Look at what is on my screen and tell me what you see or help me with my code/workflow."
                self.conversation.append({"role": "user", "content": prompt, "imageBase64": b64})
                await self._process_message(prompt)
            except Exception as e:
                console.print(f"[bold red]Screen capture error:[/] {e}")
            return "ok"

        if action == "/voice":
            console.print("[dim cyan]🎙 Voice mode activated. Speak into your microphone... (say 'exit' to stop)[/]")
            try:
                import speech_recognition as sr
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, timeout=10, phrase_time_limit=15)
                    spoken = r.recognize_google(audio)
                    console.print(f"[bold cyan]You (spoken):[/] {spoken}")
                    await self._process_message(spoken)
            except ImportError:
                console.print("[dim yellow]Voice recognition requires `speechrecognition` and `pyaudio`. Run `pip install SpeechRecognition`.[/]")
            except Exception as e:
                console.print(f"[dim red]Voice recognition error:[/] {e}")
            return "ok"

        if action == "/scroll":
            if arg == "top":
                console.print("[dim]Scrolled to top of buffer.[/]")
            else:
                console.print("[dim]Scrolled to bottom.[/]")
            return "ok"

        if action in ("/status", "/system"):
            engine.reload_keys()
            p, m = engine.get_best_provider()
            console.print(f"\n[bold cyan]ELE System Status[/]")
            console.print(f"  [dim]• Active Provider:[/] [bold green]{p.upper()}[/]")
            console.print(f"  [dim]• Active Model:[/] [bold cyan]{m}[/]")
            console.print(f"  [dim]• Total Tokens:[/] {store.token_usage.get('total', 0):,}")
            console.print(f"  [dim]• Backend Connected:[/] {'Yes' if store.backend_connected else 'Standalone LLM Mode'}\n")
            return "ok"

        if action == "/keys":
            engine.reload_keys()
            console.print("\n[bold cyan]API Key Status[/]")
            for k, label in [
                ("NVIDIA_API_KEY", "NVIDIA"),
                ("OPENAI_API_KEY", "OpenAI"),
                ("GEMINI_API_KEY", "Gemini"),
                ("ANTHROPIC_API_KEY", "Anthropic"),
                ("GROQ_API_KEY", "Groq"),
            ]:
                val = engine._KEYS.get(k, "")
                if val:
                    masked = val[:4] + "••••" + val[-4:] if len(val) > 8 else "••••"
                    console.print(f"  [bold green]✓[/] {label:<12} [dim]({masked})[/]")
                else:
                    console.print(f"  [bold red]✗[/] {label:<12} [dim](not configured)[/]")
            console.print("[dim]Edit keys with /setup or in ~/.ele-agent/.env[/]\n")
            return "ok"

        if action == "/models":
            engine.reload_keys()
            console.print("\n[bold cyan]Available Models & Dynamic Routing[/]")
            providers = engine.get_available_providers()
            for p in providers:
                if p == "ollama":
                    console.print(f"  [dim]•[/] [bold]OLLAMA[/]: llama3 [dim](local offline)[/]")
                else:
                    has_k = bool(engine._KEYS.get(f"{p.upper()}_API_KEY"))
                    status = "[green]Ready[/]" if has_k else "[red]No Key[/]"
                    console.print(f"  [dim]•[/] [bold]{p.upper()}[/]: {status}")
            console.print()
            return "ok"

        if action == "/model":
            if not arg:
                console.print("[dim]Usage: /model <provider> or /model auto[/]")
                return "ok"
            if arg.lower() == "auto":
                self.manual_override = False
                self.active_provider = None
                self.active_model = None
                console.print("[dim green]✓ Switched to Auto Dynamic Routing.[/]")
            else:
                if "/" in arg:
                    p, m = arg.split("/", 1)
                    self.active_provider = p.lower()
                    self.active_model = engine.normalize_model(self.active_provider, m)
                else:
                    self.active_provider = arg.lower()
                    self.active_model = engine._default_model_for(self.active_provider)
                self.manual_override = True
                console.print(f"[dim green]✓ Model set to [bold]{self.active_provider.upper()}[/] ({self.active_model}).[/]")
            return "ok"

        if action == "/browse" and arg:
            import webbrowser
            webbrowser.open(arg)
            console.print(f"[dim green]✓ Opened [underline]{arg}[/] in default browser.[/]")
            return "ok"

        if action == "/shell" and arg:
            console.print(f"[dim yellow]⚙ $ {arg}[/]")
            res = await engine.execute_tool("shell", {"command": arg})
            console.print(res)
            return "ok"

        if action == "/setup":
            from .. import ele
            # Run interactive setup
            try:
                from ele import _run_setup
                _run_setup()
                engine.reload_keys()
            except Exception:
                pass
            return "ok"

        console.print(f"[dim red]Unknown command: {action}. Type /help for options.[/]")
        return "ok"

    async def _process_message(self, user_text: str) -> None:
        """Stream response with dynamic model routing and auto-failovers."""
        self.conversation.append({"role": "user", "content": user_text})

        # Determine routing tier
        tier = analyze_prompt_tier(user_text)
        candidates = get_tier_models(tier) if not self.manual_override else [(self.active_provider, self.active_model)]

        # Print model metadata
        provider, model = candidates[0]
        norm_model = engine.normalize_model(provider, model)
        time_str = datetime.now().strftime("%H:%M:%S")
        console.print(f"[dim]{time_str}[/] [bold cyan]ele[/] [dim]({provider}/{norm_model.split('/')[-1]})[/]:")

        # Stream with cascade failover
        success = False
        last_error = ""

        for prov, mod in candidates:
            if prov == "none":
                break
            try:
                norm_m = engine.normalize_model(prov, mod)
                accumulated = ""
                has_yielded = False

                async for event in engine.stream_response(
                    messages=self.conversation,
                    provider=prov,
                    model=norm_m,
                ):
                    if event.type == "delta":
                        sys.stdout.write(event.content)
                        sys.stdout.flush()
                        accumulated += event.content
                        has_yielded = True

                    elif event.type == "thought":
                        console.print(f"\n[dim italic magenta]🧠 Thinking: {event.content}[/]")

                    elif event.type == "tool_start":
                        console.print(f"\n[bold yellow]⚙ Executing tool:[/] [cyan]{event.tool}[/]")

                    elif event.type == "tool_end":
                        preview = event.content.strip()[:180].replace("\n", " ")
                        console.print(f"[bold green]✓ Done:[/] [dim]{preview}[/]\n")
                        self.conversation.append({
                            "role": "assistant",
                            "content": f"TOOL_RESULT {event.tool}: {event.content}"
                        })

                    elif event.type == "error":
                        last_error = event.content
                        break

                    elif event.type == "final":
                        accumulated = event.content or accumulated
                        success = True
                        break

                if success:
                    sys.stdout.write("\n\n")
                    sys.stdout.flush()
                    self.conversation.append({"role": "assistant", "content": accumulated})
                    store.add_token_usage(len(user_text) // 4, len(accumulated) // 4)
                    break
                else:
                    # If this provider failed before streaming, try next in cascade
                    if not has_yielded:
                        continue
                    else:
                        break

            except Exception as e:
                last_error = str(e)
                continue

        if not success:
            if "No AI Model API key is configured" in last_error or not engine.has_cloud_api_keys():
                console.print(
                    "\n[bold yellow]⚡ No API Key Configured[/]\n"
                    "[dim]To chat and automate tasks, add an API key:[/]\n"
                    "  Type [bold cyan]/setup[/] or edit [bold]~/.ele-agent/.env[/]\n"
                    "  [dim]NVIDIA API keys are 100% free at https://build.nvidia.com[/]\n"
                )
            else:
                console.print(f"\n[bold red]Error:[/] {last_error or 'All available providers failed.'}\n")


def run_repl():
    """Main entry point for Terminal REPL."""
    repl = TerminalREPL()
    asyncio.run(repl.start())


if __name__ == "__main__":
    run_repl()
