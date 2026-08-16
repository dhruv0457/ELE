# Plugin System Specification

## Overview

ELE Agent supports **three plugin formats** with a unified CLI interface:

| Format | Runtime | Security | Use Case |
|--------|---------|----------|----------|
| **Python `@skill`** | Native Python | Medium (trusted) | First-party, performance-critical |
| **JSON Manifest** | Python/Node/Rust | Medium | Community, versioned, language-agnostic |
| **WASM** | Wasmtime | High (sandboxed) | Untrusted, polyglot, marketplace |

## Plugin Structure

### Python Skill Format
```
my-skill/
├── skill.json          # Optional metadata
├── main.py             # @skill class
├── requirements.txt    # Dependencies
├── README.md
└── tests/
    └── test_skill.py
```

**skill.json**:
```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "Process files with AI",
  "author": "Your Name",
  "entry_point": "main:FileProcessorSkill",
  "min_agent_version": "1.0.0",
  "permissions": ["file:read", "file:write", "shell:run"],
  "config_schema": {
    "default_model": {"type": "string", "default": "gpt-4"},
    "max_file_size_mb": {"type": "integer", "default": 10}
  }
}
```

**main.py**:
```python
from typing import Any, Dict, List, Optional
from ele_sdk import skill, SkillContext

@skill(
    name="file-processor",
    description="Process files with AI: summarize, transform, analyze",
    version="1.0.0",
    permissions=["file:read", "file:write", "shell:run"],
    config_schema={
        "default_model": {"type": "string", "default": "gpt-4"},
        "max_file_size_mb": {"type": "integer", "default": 10}
    }
)
class FileProcessorSkill:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.default_model = config.get("default_model", "gpt-4")
        self.max_file_size = config.get("max_file_size_mb", 10) * 1024 * 1024
    
    async def execute(
        self, 
        ctx: SkillContext, 
        task: str,
        files: Optional[List[str]] = None,
        pattern: Optional[str] = None,
        output_format: str = "markdown"
    ) -> str:
        # 1. Resolve files
        target_files = await self._resolve_files(ctx, files, pattern)
        
        # 2. Read contents
        file_contents = {}
        for f in target_files:
            if f.size > self.max_file_size:
                continue
            content = await ctx.tools.file.read(f.path)
            file_contents[f.path] = content
        
        # 3. Process with LLM
        prompt = self._build_prompt(task, file_contents, output_format)
        result = await ctx.llm.complete(
            prompt=prompt,
            model=self.default_model,
            temperature=0.3
        )
        
        # 4. Write output
        if output_format != "text":
            output_path = await self._write_output(ctx, result, output_format)
            return f"Processed {len(file_contents)} files. Output: {output_path}"
        
        return result
    
    @FileProcessorSkill.command("summarize")
    async def summarize_cmd(ctx: SkillContext, path: str) -> str:
        content = await ctx.tools.file.read(path)
        return await ctx.llm.complete(f"Summarize:\n\n{content}")
```

### JSON Manifest Format
```
my-skill/
├── skill.json          # Required manifest
├── main.py             # Entry point (any language)
├── requirements.txt    # If Python
├── package.json        # If Node.js
└── Cargo.toml          # If Rust
```

**skill.json**:
```json
{
  "name": "web-scraper",
  "version": "2.1.0",
  "description": "Extract structured data from websites",
  "author": "DataWizard",
  "license": "MIT",
  "repository": "https://github.com/user/web-scraper",
  "entry_point": "main:scrape",
  "runtime": "python",
  "permissions": [
    "browser:navigate",
    "browser:click",
    "browser:extract",
    "file:write",
    "network:fetch"
  ],
  "config_schema": {
    "default_timeout": {"type": "integer", "default": 30000},
    "user_agent": {"type": "string", "default": "ELEBot/1.0"},
    "proxy": {"type": "string"}
  },
  "commands": {
    "scrape": {
      "description": "Scrape a single URL",
      "params": {
        "url": {"type": "string", "required": true},
        "selector": {"type": "string"},
        "format": {"type": "string", "enum": ["json", "csv", "markdown"], "default": "json"}
      }
    }
  },
  "ui": {
    "icon": "🌐",
    "category": "automation",
    "screenshots": ["screenshots/1.png"]
  }
}
```

### WASM Format
```
my-skill/
├── skill.wasm          # Compiled WebAssembly
├── skill.wit           # WIT interface
├── skill.json          # Manifest (same as JSON format)
└── README.md
```

**skill.wit**:
```wit
package ele:skill;

interface host {
    read-file: func(path: string) -> result<string, error>
    write-file: func(path: string, content: string) -> result<(), error>
    llm-complete: func(prompt: string, model: string, temperature: f32) -> result<string, error>
    log: func(level: string, message: string) -> ()
}

interface skill {
    name: func() -> string
    version: func() -> string
    description: func() -> string
    permissions: func() -> list<string>
    execute: func(task: string, config: string) -> result<string, error>
    commands: func() -> list<command>
    record command {
        name: string
        description: string
        params: string  // JSON schema
    }
}
```

## CLI Commands

```bash
# Scaffold new plugin
ele plugin create my-skill --template python|json|wasm

# Validate plugin
ele plugin validate ./my-skill

# Test plugin locally
ele plugin test ./my-skill "Summarize README.md"

# Package for marketplace
ele plugin package ./my-skill  # Creates my-skill-1.0.0.ele-plugin

# Install from package
ele plugin install ./my-skill-1.0.0.ele-plugin

# Install from marketplace
ele plugin install web-scraper@2.1.0

# Publish to marketplace (requires auth)
ele plugin publish ./my-skill-1.0.0.ele-plugin

# List installed
ele plugin list

# Update all
ele plugin update --all

# Disable/enable
ele plugin disable web-scraper
ele plugin enable web-scraper

# Configure
ele plugin config web-scraper --set default_timeout=60000
```

## Marketplace

### Installation Flow
```
1. ele plugin install web-scraper@2.1.0
2. Fetch manifest from marketplace API
3. Verify signature (cosign/sigstore) - OPTIONAL (trust registry)
4. Download .ele-plugin package
5. Verify checksum
6. Extract to ~/.ele-agent/plugins/installed/web-scraper/
7. Install dependencies (pip/uv for Python, npm for Node, cargo for Rust)
8. Register in plugin registry
9. Notify UI (sidebar badge)
```

### Package Format (`.ele-plugin`)
```
web-scraper-2.1.0.ele-plugin  (ZIP archive)
├── skill.json
├── main.py
├── requirements.txt
├── skill.wasm          # If WASM
├── skill.wit           # If WASM
├── LICENSE
└── README.md
```

### Marketplace API
```
GET  /api/v1/plugins/marketplace?category=coding&sort=trending
GET  /api/v1/plugins/marketplace/{name}
POST /api/v1/plugins/install          # {name, version, source}
GET  /api/v1/plugins/installed
POST /api/v1/plugins/{id}/enable
POST /api/v1/plugins/{id}/disable
DELETE /api/v1/plugins/{id}
GET  /api/v1/plugins/{id}/manifest
```

## Permission System

```python
# backend/app/plugins/permissions.py
PERMISSIONS = {
    # File system
    "file:read": "Read files",
    "file:write": "Write files",
    "file:delete": "Delete files",
    "file:glob": "List files with patterns",
    
    # Shell
    "shell:run": "Execute shell commands",
    
    # Browser
    "browser:navigate": "Navigate to URLs",
    "browser:click": "Click elements",
    "browser:extract": "Extract page content",
    "browser:screenshot": "Take screenshots",
    
    # Network
    "network:fetch": "HTTP requests",
    
    # Apps
    "app:launch": "Launch applications",
    
    # Email/Calendar
    "email:send": "Send emails",
    "email:read": "Read emails",
    "calendar:read": "Read calendar",
    "calendar:write": "Write calendar",
}

class PermissionManager:
    def __init__(self):
        self.granted: Dict[str, Set[str]] = {}  # plugin_id -> permissions
    
    def check(self, plugin_id: str, permission: str) -> bool:
        return permission in self.granted.get(plugin_id, set())
    
    def grant(self, plugin_id: str, permissions: List[str]):
        self.granted[plugin_id] = set(permissions)
    
    def revoke(self, plugin_id: str, permission: str):
        if plugin_id in self.granted:
            self.granted[plugin_id].discard(permission)
```

## SDK Reference

### Installation
```bash
pip install ele-agent-sdk
```

### Core Classes

```python
# ele_sdk/__init__.py
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SkillContext:
    session_id: str
    user_id: str
    config: Dict[str, Any]
    tools: "ToolClient"
    llm: "LLMClient"
    memory: "MemoryClient"
    logger: "Logger"

class ToolClient:
    # File operations
    async def file.read(self, path: str) -> str: ...
    async def file.write(self, path: str, content: str) -> None: ...
    async def file.patch(self, path: str, diff: str) -> None: ...
    async def file.stat(self, path: str) -> FileStat: ...
    async def file.glob(self, pattern: str) -> List[FileStat]: ...
    async def file.delete(self, path: str) -> None: ...
    
    # Shell
    async def shell.run(self, cmd: str, cwd: str = None, timeout: int = 60) -> ShellResult: ...
    
    # Browser (Playwright)
    async def browser.navigate(self, url: str) -> None: ...
    async def browser.click(self, selector: str) -> None: ...
    async def browser.type(self, selector: str, text: str) -> None: ...
    async def browser.extract(self, selector: str) -> List[str]: ...
    async def browser.screenshot(self) -> bytes: ...
    async def browser.pdf(self) -> bytes: ...
    
    # System
    async def system.open_app(self, name: str) -> None: ...
    async def system.notify(self, title: str, message: str) -> None: ...

class LLMClient:
    async def complete(
        self,
        prompt: str,
        model: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str = None,
        tools: List[Dict] = None
    ) -> LLMResponse: ...
    
    async def stream_complete(self, ...) -> AsyncGenerator[str, None]: ...
    
    async def embed(self, texts: List[str], model: str = "local") -> List[List[float]]: ...

class MemoryClient:
    async def short_term.get(self) -> List[Message]: ...
    async def short_term.add(self, message: Message) -> None: ...
    
    async def long_term.search(self, query: str, k: int = 5) -> List[MemoryEntry]: ...
    async def long_term.store(self, key: str, value: str, tags: List[str]) -> None: ...
    
    async def episodic.record(self, action: str, result: str, success: bool) -> None: ...
    async def episodic.recall(self, pattern: str) -> List[Episode]: ...

def skill(
    name: str,
    description: str,
    version: str = "1.0.0",
    permissions: List[str] = None,
    config_schema: Dict = None
):
    """Decorator to register a skill class"""
    def decorator(cls):
        cls._skill_meta = {
            "name": name,
            "description": description,
            "version": version,
            "permissions": permissions or [],
            "config_schema": config_schema or {}
        }
        return cls
    return decorator
```

## Built-in Plugins

### file-processor
- Summarize, transform, analyze files
- Permissions: file:read, file:write, shell:run

### web-searcher
- Search web, extract content
- Permissions: browser:navigate, browser:extract, network:fetch

### code-assistant
- Write, debug, refactor code
- Permissions: file:read, file:write, shell:run, browser:navigate

## Dependency Resolution

```python
# cli/src/plugins/dependencies.py
import subprocess
import sys

class DependencyResolver:
    def __init__(self):
        self.use_uv = self._check_uv()
    
    def _check_uv(self) -> bool:
        try:
            subprocess.run(["uv", "--version"], capture_output=True)
            return True
        except FileNotFoundError:
            return False
    
    def install(self, requirements: List[str], target_dir: str):
        if self.use_uv:
            cmd = ["uv", "pip", "install", "--target", target_dir] + requirements
        else:
            cmd = [sys.executable, "-m", "pip", "install", "--target", target_dir] + requirements
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise PluginError(f"Dependency install failed: {result.stderr}")
```

## Version Constraints

- **Semver**: `^1.0.0` (compatible), `~1.0.0` (patch only)
- **Exact**: `1.0.0`
- **Ranges**: `>=1.0.0,<2.0.0`

```toml
# In skill.json
"dependencies": {
    "requests": "^2.31.0",
    "beautifulsoup4": ">=4.12.0,<5.0.0",
    "ele-sdk": "~1.0.0"
}
```

## Security

- **No sandbox** for Python/JSON (trusted only)
- **WASM sandbox**: Wasmtime with capability-based security
- **Permissions**: Declared in manifest, granted on install
- **Signature verification**: Optional (cosign/sigstore) - trust registry for now
- **Network access**: Only if `network:fetch` permission granted