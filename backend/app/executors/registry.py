"""Executor Registry - File, Shell, Browser, Desktop, App Operations"""
import os
import asyncio
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Any, List, Optional
try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    import logging
    logger = logging.getLogger("ele_agent")


class FileExecutor:
    """File system operations"""

    def __init__(self, working_dir: str = "~"):
        self.working_dir = Path(os.path.expanduser(working_dir))

    async def read(self, path: str) -> str:
        full_path = self._resolve_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    async def write(self, path: str, content: str) -> str:
        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Written to {path}"

    async def list(self, path: str = ".") -> List[Dict[str, Any]]:
        full_path = self._resolve_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        items = []
        for item in full_path.iterdir():
            stat = item.stat()
            items.append({
                "name": item.name,
                "path": str(item.relative_to(self.working_dir)),
                "is_dir": item.is_dir(),
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })
        return items

    async def stat(self, path: str) -> Dict[str, Any]:
        full_path = self._resolve_path(path)
        stat = full_path.stat()
        return {
            "path": path,
            "size": stat.st_size,
            "is_dir": full_path.is_dir(),
            "modified": stat.st_mtime,
        }

    def _resolve_path(self, path: str) -> Path:
        if os.path.isabs(path):
            return Path(path)
        return (self.working_dir / path).resolve()


class ShellExecutor:
    """Shell command execution"""

    def __init__(self, working_dir: str = "~", timeout: int = 60):
        self.working_dir = Path(os.path.expanduser(working_dir))
        self.timeout = timeout

    async def run(self, cmd: str, cwd: str = None, timeout: int = None) -> Dict[str, Any]:
        work_dir = Path(os.path.expanduser(cwd)) if cwd else self.working_dir

        logger.info("shell_executing", cmd=cmd, cwd=str(work_dir))

        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout or self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "error": f"Command timed out after {timeout or self.timeout}s",
                    "stdout": "",
                    "stderr": "",
                    "returncode": -1,
                }

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "returncode": process.returncode,
            }

        except Exception as e:
            logger.error("shell_error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "returncode": -1,
            }


class AppLaunchExecutor:
    """Application launching"""

    def __init__(self, whitelist: List[str] = None):
        self.whitelist = whitelist or [
            "code", "notepad", "calc", "explorer", "cmd", "powershell",
            "chrome", "firefox", "msedge", "terminal", "wt"
        ]

    async def launch(self, name: str, args: List[str] = None) -> Dict[str, Any]:
        name_lower = name.lower()
        if name_lower not in [w.lower() for w in self.whitelist]:
            return {"success": False, "error": f"App not in whitelist: {name}"}

        try:
            cmd = [name]
            if args:
                cmd.extend(args)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            return {"success": True, "pid": process.pid}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ExecutorRegistry:
    """Registry for all executors including Browser and Desktop"""

    def __init__(self):
        self.file = FileExecutor()
        self.shell = ShellExecutor()
        self.app = AppLaunchExecutor()
        self.browser = BrowserExecutor()
        self.desktop = DesktopExecutor()

    async def execute(self, tool: str, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        working_dir = context.get("working_dir", "~")

        if tool in ["read_file", "write_file", "list_files", "stat"]:
            self.file.working_dir = Path(os.path.expanduser(working_dir))
            method = getattr(self.file, tool)
            return await method(**args)

        elif tool == "run_shell":
            self.shell.working_dir = Path(os.path.expanduser(working_dir))
            return await self.shell.run(args.get("cmd", ""), args.get("cwd"))

        elif tool == "open_app":
            return await self.app.launch(args.get("name", ""), args.get("args", []))

        elif tool in ["browser_navigate", "browser_click", "browser_fill", "browser_extract", 
                      "browser_screenshot", "browser_eval_js", "browser_wait",
                      "browser_hover", "browser_select", "browser_back", "browser_forward",
                      "browser_reload", "browser_get_content", "browser_get_text",
                      "browser_get_cookies", "browser_set_cookies"]:
            return await self.browser.execute(tool, args)

        elif tool in ["move_mouse", "click", "double_click", "right_click", "drag", 
                      "type_text", "press_key", "hotkey", "scroll",
                      "screenshot", "screenshot_region", "ocr", "ocr_region", 
                      "launch_app", "focus_window", "close_window", "list_windows",
                      "get_window_info", "ocr_region", "capture_region", "move_mouse",
                      "click_at", "drag_drop"]:
            return await self.desktop.execute(tool, args)

        raise ValueError(f"Unknown tool: {tool}")