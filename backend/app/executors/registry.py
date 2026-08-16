"""Executor Registry - File, Shell, Browser Operations"""
import os
import asyncio
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


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

    async def patch(self, path: str, diff: str) -> str:
        # Simple patch implementation
        full_path = self._resolve_path(path)
        content = await self.read(path)
        # Apply unified diff
        import difflib
        old_lines = content.splitlines(keepends=True)
        new_lines = list(difflib.unified_diff(old_lines, diff.splitlines(keepends=True)))
        await self.write(path, ''.join(new_lines))
        return f"Patched {path}"

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

    async def glob(self, pattern: str) -> List[Dict[str, Any]]:
        full_pattern = self.working_dir / pattern
        matches = []
        for path in self.working_dir.glob(pattern):
            stat = path.stat()
            matches.append({
                "name": path.name,
                "path": str(path.relative_to(self.working_dir)),
                "is_dir": path.is_dir(),
                "size": stat.st_size,
            })
        return matches

    async def delete(self, path: str) -> str:
        full_path = self._resolve_path(path)
        if full_path.is_dir():
            import shutil
            shutil.rmtree(full_path)
        else:
            full_path.unlink()
        return f"Deleted {path}"

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

    def __init__(self, working_dir: str = "~", timeout: int = 120):
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


class BrowserExecutor:
    """Browser automation with Playwright"""

    def __init__(self, headless: bool = False, stealth: bool = True):
        self.headless = headless
        self.stealth = stealth
        self.browser = None
        self.page = None

    async def _ensure_browser(self):
        if self.browser is None:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled'] if self.stealth else [],
            )
            self.page = await self.browser.new_page()

            if self.stealth:
                await self.page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                """)

    async def navigate(self, url: str) -> Dict[str, Any]:
        await self._ensure_browser()
        try:
            response = await self.page.goto(url, wait_until="networkidle")
            return {
                "success": True,
                "url": self.page.url,
                "title": await self.page.title(),
                "status": response.status if response else 0,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def click(self, selector: str) -> Dict[str, Any]:
        await self._ensure_browser()
        try:
            await self.page.click(selector)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        await self._ensure_browser()
        try:
            await self.page.fill(selector, text)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def extract(self, selector: str) -> Dict[str, Any]:
        await self._ensure_browser()
        try:
            elements = await self.page.query_selector_all(selector)
            texts = []
            for el in elements:
                text = await el.inner_text()
                texts.append(text)
            return {"success": True, "data": texts}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def screenshot(self, full_page: bool = False) -> Dict[str, Any]:
        await self._ensure_browser()
        try:
            img = await self.page.screenshot(full_page=full_page)
            import base64
            return {
                "success": True,
                "data": base64.b64encode(img).decode(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def close(self):
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            self.browser = None
            self.page = None


class AppLaunchExecutor:
    """Application launching"""

    def __init__(self, whitelist: List[str] = None):
        self.whitelist = whitelist or ["code", "chrome", "firefox", "notepad", "explorer", "terminal"]

    async def launch(self, app: str, args: List[str] = None) -> Dict[str, Any]:
        app_lower = app.lower()
        if app_lower not in [w.lower() for w in self.whitelist]:
            return {"success": False, "error": f"App not in whitelist: {app}"}

        try:
            cmd = [app]
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
    """Registry for all executors"""

    def __init__(self):
        self.file = FileExecutor()
        self.shell = ShellExecutor()
        self.browser = BrowserExecutor()
        self.app = AppLaunchExecutor()

    async def execute(self, tool: str, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        working_dir = context.get("working_dir", "~")

        if tool in ["read_file", "write_file", "list_files", "glob", "patch", "stat", "delete"]:
            self.file.working_dir = Path(os.path.expanduser(working_dir))
            method = getattr(self.file, tool)
            return await method(**args)

        elif tool == "run_shell":
            self.shell.working_dir = Path(os.path.expanduser(working_dir))
            return await self.shell.run(args.get("cmd", ""), args.get("cwd"))

        elif tool in ["browser_navigate", "browser_click", "browser_type", "browser_extract", "browser_screenshot"]:
            method = getattr(self.browser, tool.replace("browser_", ""))
            return await method(**args)

        elif tool == "open_app":
            return await self.app.launch(args.get("name", ""), args.get("args", []))

        raise ValueError(f"Unknown tool: {tool}")