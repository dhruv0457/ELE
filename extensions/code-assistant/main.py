"""Code Assistant Plugin"""
import asyncio
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


class CodeAssistant:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.default_lang = self.config.get("default_language", "python")
        self.auto_format = self.config.get("auto_format", True)
        self.run_tests = self.config.get("run_tests", True)
        self.linter = self.config.get("linter", "ruff")

    async def create_file(self, path: str, content: str, language: str = None) -> Dict[str, Any]:
        path = Path(path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if self.auto_format:
            await self.format_file(path, language)
        return {"success": True, "path": str(path)}

    async def format_file(self, path: Path, language: str = None) -> Dict[str, Any]:
        lang = language or self.default_lang
        try:
            if lang == "python" and self.linter != "none":
                result = await self._run_command(f"{self.linter} format {path}")
                return {"success": result["success"], "output": result["stdout"]}
            elif lang in ["javascript", "typescript"]:
                result = await self._run_command(f"prettier --write {path}")
                return {"success": result["success"], "output": result["stdout"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": True}

    async def run_tests(self, path: str, test_command: str = None) -> Dict[str, Any]:
        if not self.run_tests:
            return {"success": True, "skipped": True}
        cmd = test_command or self._get_test_command(path)
        return await self._run_command(cmd, cwd=Path(path).parent)

    def _get_test_command(self, path: str) -> str:
        path = Path(path)
        if path.suffix == ".py":
            return f"python -m pytest {path} -v"
        elif path.suffix in [".js", ".ts"]:
            return f"npm test -- {path}"
        return f"python -m pytest {path} -v"

    async def lint(self, path: str) -> Dict[str, Any]:
        if self.linter == "none":
            return {"success": True, "skipped": True}
        return await self._run_command(f"{self.linter} check {path}")

    async def _run_command(self, cmd: str, cwd: Path = None) -> Dict[str, Any]:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=cwd or Path.cwd(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return {
            "success": proc.returncode == 0,
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else "",
            "returncode": proc.returncode,
        }

    async def refactor(self, path: str, instructions: str) -> Dict[str, Any]:
        path = Path(path).expanduser()
        if not path.exists():
            return {"success": False, "error": "File not found"}

        content = path.read_text(encoding="utf-8")
        refactored = await self._apply_refactoring(content, instructions)
        path.write_text(refactored, encoding="utf-8")
        if self.auto_format:
            await self.format_file(path)
        return {"success": True, "path": str(path)}

    async def _apply_refactoring(self, content: str, instructions: str) -> str:
        prompt = f"""Refactor the following code according to these instructions:
{instructions}

Code:
```
{content}
```

Return only the refactored code."""
        return content

    async def generate(self, spec: str, language: str = None, framework: str = None) -> str:
        lang = language or self.default_lang
        prompt = f"""Generate {lang} code for: {spec}"""
        if framework:
            prompt += f" using {framework}"
        prompt += "\n\nReturn only the code."
        return f"# Generated code for: {spec}\n# TODO: Implement"


async def initialize(context: Dict[str, Any]) -> CodeAssistant:
    return CodeAssistant(context.get("config", {}))