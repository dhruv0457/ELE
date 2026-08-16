"""File Processor Plugin"""
import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, Any, List


class FileProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_size = self.config.get("max_file_size_mb", 100) * 1024 * 1024
        self.allowed_ext = self.config.get("allowed_extensions", ["*"])
        self.backup = self.config.get("backup_on_write", True)

    async def read(self, path: str) -> str:
        path = Path(path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if path.stat().st_size > self.max_size:
            raise ValueError(f"File too large: {path}")
        return path.read_text(encoding="utf-8")

    async def write(self, path: str, content: str) -> Dict[str, Any]:
        path = Path(path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        if self.backup and path.exists():
            backup_path = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup_path)
        path.write_text(content, encoding="utf-8")
        return {"success": True, "path": str(path), "size": len(content)}

    async def list(self, path: str, pattern: str = "**/*") -> List[Dict[str, Any]]:
        path = Path(path).expanduser()
        if not path.exists():
            return []
        files = []
        for item in path.glob(pattern):
            if item.is_file():
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime,
                })
        return files

    async def search(self, path: str, query: str) -> List[Dict[str, Any]]:
        path = Path(path).expanduser()
        results = []
        for item in path.rglob("*"):
            if item.is_file() and item.stat().st_size < self.max_size:
                try:
                    content = item.read_text(encoding="utf-8")
                    if query.lower() in content.lower():
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                results.append({
                                    "file": str(item),
                                    "line": i + 1,
                                    "content": line.strip()[:200],
                                })
                                break
                except Exception:
                    pass
        return results

    async def delete(self, path: str) -> Dict[str, Any]:
        path = Path(path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return {"success": True, "path": str(path)}


async def initialize(context: Dict[str, Any]) -> FileProcessor:
    return FileProcessor(context.get("config", {}))


async def hook_on_file_read(processor: FileProcessor, path: str) -> None:
    print(f"Reading file: {path}")


async def hook_on_file_write(processor: FileProcessor, path: str) -> None:
    print(f"Writing file: {path}")