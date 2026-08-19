"""Automate Screen — Task automation with execution log"""
import asyncio
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, ListView, ListItem, Label, Button
from textual.binding import Binding

from ..store import store, Message, AgentStatus
from ..widgets.safe_text_area import SafeTextArea
from .. import llm as engine


class AutomateScreen(Container):
    """JARVIS autonomous task execution mode."""

    BINDINGS = [
        Binding("ctrl+l", "clear_log", "Clear log", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._running = False

    def compose(self) -> ComposeResult:
        yield Static("🤖 AUTOMATE MODE", id="automate_header", classes="screen-header")
        yield Static(
            "[dim]Give me a task and I'll execute it step by step.[/]",
            id="automate_sub"
        )
        with Horizontal(id="automate_layout"):
            # Execution log
            with Vertical(id="log_panel"):
                yield Static("EXECUTION LOG", classes="panel-title")
                yield ListView(id="exec_log")

            # Task input
            with Vertical(id="task_panel"):
                yield Static("TASK", classes="panel-title")
                yield SafeTextArea(
                    id="task_input",
                    tab_behavior="indent",
                )
                with Horizontal(id="task_controls"):
                    yield Button("▶  Execute", id="run_btn", classes="run-btn")
                    yield Button("⏹  Stop", id="stop_btn", classes="stop-btn")
                    yield Button("🗑  Clear", id="clear_btn", classes="clear-btn")

                yield Static("RESULT", classes="panel-title")
                yield Static("", id="task_result", classes="task-result")

    def on_mount(self) -> None:
        self.query_one("#task_input").focus()
        self._reload_log()

    def _reload_log(self) -> None:
        lst = self.query_one("#exec_log", ListView)
        lst.clear()
        for entry in store.execution_log[-50:]:  # last 50
            icon = {
                "command": "[#00FFE0]❯[/]",
                "output": "[#64748B]│[/]",
                "tool": "[#F59E0B]⚙[/]",
                "error": "[#FF3366]✗[/]",
                "success": "[#00FF9D]✓[/]",
                "thought": "[#A855F7]🧠[/]",
                "info": "[dim]·[/]",
            }.get(entry["type"], "[dim]·[/]")
            ts = entry["timestamp"].strftime("%H:%M:%S") if hasattr(entry["timestamp"], "strftime") else ""
            content = str(entry["content"])[:120]
            lst.append(ListItem(Label(f"{icon} [dim]{ts}[/] {content}")))
        lst.scroll_end(animate=False)

    def _log(self, type: str, content: str, source: str = "") -> None:
        store.log_execution(type, content, source)
        # Live update
        lst = self.query_one("#exec_log", ListView)
        icon = {
            "command": "[#00FFE0]❯[/]",
            "output": "[#64748B]│[/]",
            "tool": "[#F59E0B]⚙[/]",
            "error": "[#FF3366]✗[/]",
            "success": "[#00FF9D]✓[/]",
            "thought": "[#A855F7]🧠[/]",
            "info": "[dim]·[/]",
        }.get(type, "[dim]·[/]")
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        lst.append(ListItem(Label(f"{icon} [dim]{ts}[/] {content[:120]}")))
        lst.scroll_end(animate=False)

    async def _run_task(self, task: str) -> None:
        if self._running:
            return
        self._running = True
        store.set_agent_status(AgentStatus.WORKING)

        result_widget = self.query_one("#task_result", Static)
        result_widget.update("[dim]Running...[/]")

        self._log("command", f"Task: {task}")

        full_response = ""
        try:
            messages = [{"role": "user", "content": task}]
            async for event in engine.stream_response(messages=messages):
                if event.type == "model_info":
                    self._log("info", f"Using {event.model}")

                elif event.type == "thought":
                    self._log("thought", event.content)

                elif event.type == "tool_start":
                    self._log("tool", f"→ {event.tool}")
                    store.set_agent_status(AgentStatus.WORKING, event.tool)

                elif event.type == "tool_end":
                    self._log("output", f"  {event.content[:80]}")

                elif event.type == "delta":
                    full_response += event.content
                    result_widget.update(full_response[-500:])

                elif event.type == "final":
                    full_response = event.content or full_response
                    self._log("success", "Task complete")
                    result_widget.update(full_response[-1000:])

                elif event.type == "error":
                    self._log("error", event.content)
                    result_widget.update(f"[#FF3366]Error: {event.content}[/]")
                    break

        except Exception as e:
            self._log("error", str(e))
            result_widget.update(f"[#FF3366]Error: {e}[/]")
        finally:
            self._running = False
            store.set_agent_status(AgentStatus.IDLE)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "run_btn":
            task_input = self.query_one("#task_input", SafeTextArea)
            task = task_input.text.strip()
            if task:
                self.run_worker(self._run_task(task), exclusive=True)
        elif btn_id == "stop_btn":
            self._running = False
        elif btn_id == "clear_btn":
            store.clear_execution_log()
            self._reload_log()
            self.query_one("#task_result", Static).update("")

    def action_clear_log(self) -> None:
        store.clear_execution_log()
        self._reload_log()
