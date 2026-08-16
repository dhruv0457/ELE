# ELE Agent Plugin Development Guide

## Overview

ELE Agent supports **three plugin formats** for maximum flexibility:

| Format | Best For | Learning Curve | Security |
|--------|----------|----------------|----------|
| **Python Decorator** | Native performance, AI-friendly | Low | Medium (full Python) |
| **JSON Manifest** | Language-agnostic, versioned | Low | Medium |
| **WASM** | Sandboxed, polyglot, untrusted code | High | High (capability-based) |

---

## 1. Python Decorator Format (Recommended for v1)

### Structure
```
my-skill/
├── skill.json          # Optional metadata
├── main.py             # @skill class
├── requirements.txt    # Dependencies
├── README.md
└── tests/
    └── test_skill.py
```

### skill.json (Optional)
```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "Does amazing things with files",
  "author": "Your Name",
  "entry_point": "main:MySkill",
  "min_agent_version": "1.0.0",
  "permissions": ["file:read", "file:write", "shell:run"],
  "config_schema": {
    "api_key": {"type": "string", "secret": true, "description": "External API key"},
    "model": {"type": "string", "default": "gpt-4", "enum": ["gpt-4", "gpt-3.5-turbo"]}
  }
}
```

### main.py
```python
from typing import Any, Dict, List, Optional
from ele_sdk import skill, SkillContext, ToolResult

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
    """
    A skill that processes files using AI.
    
    Example usage:
    - "Summarize all Python files in ./src"
    - "Convert all .md files to .rst"
    - "Find TODO comments in the codebase"
    """
    
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
        """
        Execute the file processing task.
        
        Args:
            ctx: Skill context with tools and LLM access
            task: Natural language description of what to do
            files: Explicit list of file paths (optional)
            pattern: Glob pattern to find files (optional)
            output_format: "markdown" | "json" | "text"
        
        Returns:
            Result summary for the user
        """
        # 1. Determine which files to process
        target_files = await self._resolve_files(ctx, files, pattern)
        
        if not target_files:
            return "No files found matching criteria."
        
        # 2. Read file contents
        file_contents = {}
        for f in target_files:
            if f.size > self.max_file_size:
                continue  # Skip large files
            content = await ctx.tools.file.read(f.path)
            file_contents[f.path] = content
        
        # 3. Use LLM to process
        prompt = self._build_prompt(task, file_contents, output_format)
        result = await ctx.llm.complete(
            prompt=prompt,
            model=self.default_model,
            temperature=0.3
        )
        
        # 4. Optionally write output
        if output_format != "text":
            output_path = await self._write_output(ctx, result, output_format)
            return f"Processed {len(file_contents)} files. Output saved to {output_path}"
        
        return result
    
    async def _resolve_files(
        self, 
        ctx: SkillContext, 
        files: Optional[List[str]], 
        pattern: Optional[str]
    ) -> List[FileStat]:
        if files:
            return [await ctx.tools.file.stat(f) for f in files]
        
        if pattern:
            return await ctx.tools.file.glob(pattern)
        
        # Default: current directory Python files
        return await ctx.tools.file.glob("**/*.py")
    
    def _build_prompt(self, task: str, files: Dict[str, str], fmt: str) -> str:
        files_text = "\n\n".join(
            f"=== {path} ===\n{content[:5000]}" 
            for path, content in files.items()
        )
        return f"""Task: {task}

Files to process:
{files_text}

Output format: {fmt}
Provide a clear, structured response."""
    
    async def _write_output(self, ctx: SkillContext, content: str, fmt: str) -> str:
        ext = {"markdown": "md", "json": "json", "text": "txt"}[fmt]
        path = f"skill_output_{ctx.session_id}.{ext}"
        await ctx.tools.file.write(path, content)
        return path


# Additional skill methods (optional)
@FileProcessorSkill.command("summarize")
async def summarize_cmd(ctx: SkillContext, path: str) -> str:
    """Quick command: summarize a single file."""
    content = await ctx.tools.file.read(path)
    result = await ctx.llm.complete(f"Summarize this file:\n\n{content}")
    return result


@FileProcessorSkill.command("find-todos")
async def find_todos_cmd(ctx: SkillContext, pattern: str = "**/*.py") -> str:
    """Quick command: find all TODO/FIXME comments."""
    files = await ctx.tools.file.glob(pattern)
    todos = []
    for f in files:
        content = await ctx.tools.file.read(f.path)
        for i, line in enumerate(content.splitlines(), 1):
            if "TODO" in line or "FIXME" in line:
                todos.append(f"{f.path}:{i}: {line.strip()}")
    return "\n".join(todos) if todos else "No TODOs found."
```

---

## 2. JSON Manifest Format

### Structure
```
my-skill/
├── skill.json          # Required manifest
├── main.py             # Entry point (or any language)
├── requirements.txt    # If Python
├── package.json        # If Node.js
└── Cargo.toml          # If Rust
```

### skill.json (Required)
```json
{
  "name": "web-scraper",
  "version": "2.1.0",
  "description": "Extract structured data from websites",
  "author": "DataWizard",
  "license": "MIT",
  "repository": "https://github.com/user/web-scraper",
  "entry_point": "main:scrape",
  "runtime": "python",  // "python" | "node" | "wasm" | "binary"
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
    "proxy": {"type": "string", "description": "Optional proxy URL"}
  },
  "commands": {
    "scrape": {
      "description": "Scrape a single URL",
      "params": {
        "url": {"type": "string", "required": true},
        "selector": {"type": "string", "description": "CSS selector"},
        "format": {"type": "string", "enum": ["json", "csv", "markdown"], "default": "json"}
      }
    },
    "crawl": {
      "description": "Crawl multiple pages",
      "params": {
        "start_url": {"type": "string", "required": true},
        "max_pages": {"type": "integer", "default": 10},
        "follow_links": {"type": "boolean", "default": true}
      }
    }
  },
  "ui": {
    "icon": "🌐",
    "category": "automation",
    "screenshots": ["screenshots/1.png", "screenshots/2.png"]
  }
}
```

### main.py (Python Example)
```python
# Entry point for JSON manifest plugins
async def scrape(ctx, url: str, selector: str = None, format: str = "json"):
    """Scrape a single URL."""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        
        if selector:
            data = await page.eval_on_selector_all(selector, "els => els.map(e => e.innerText)")
        else:
            data = await page.content()
        
        await browser.close()
    
    if format == "json":
        import json
        return json.dumps(data, indent=2)
    elif format == "csv":
        import csv, io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(data)
        return output.getvalue()
    else:
        return str(data)


async def crawl(ctx, start_url: str, max_pages: int = 10, follow_links: bool = True):
    """Crawl multiple pages."""
    # Implementation here
    return f"Crawled {max_pages} pages from {start_url}"


# Plugin registry (auto-discovered)
PLUGIN_EXPORTS = {
    "scrape": scrape,
    "crawl": crawl
}
```

---

## 3. WASM Format (Advanced)

### Structure
```
my-skill/
├── skill.wasm          # Compiled WebAssembly module
├── skill.wit           # WIT interface definition
├── skill.json          # Manifest (same as JSON format)
└── README.md
```

### skill.wit (WIT Interface)
```wit
package ele:skill;

// Host-provided interfaces
interface host {
    // File operations
    read-file: func(path: string) -> result<string, error>
    write-file: func(path: string, content: string) -> result<(), error>
    list-files: func(pattern: string) -> result<list<string>, error>
    
    // LLM access
    llm-complete: func(prompt: string, model: string, temperature: f32) -> result<string, error>
    
    // Logging
    log: func(level: string, message: string) -> ()
}

// Skill exports
interface skill {
    // Metadata
    name: func() -> string
    version: func() -> string
    description: func() -> string
    permissions: func() -> list<string>
    
    // Execution
    execute: func(task: string, config: string) -> result<string, error>
    
    // Commands (optional)
    commands: func() -> list<command>
    
    record command {
        name: string
        description: string
        params: string  // JSON schema
    }
}
```

### Rust Implementation Example
```rust
// Cargo.toml
[package]
name = "my-wasm-skill"
version = "1.0.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
wit-bindgen = { version = "0.30", features = ["guest"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

[profile.release]
opt-level = "z"  // Optimize for size
lto = true
panic = "abort"
```

```rust
// src/lib.rs
wit_bindgen::generate!({
    path: "../skill.wit",
    world: "skill",
});

use crate::exports::ele::skill::skill::{Guest, Command};
use std::collections::HashMap;

struct MySkill;

impl Guest for MySkill {
    fn name() -> String {
        "wasm-processor".to_string()
    }
    
    fn version() -> String {
        "1.0.0".to_string()
    }
    
    fn description() -> String {
        "High-performance WASM skill for data processing".to_string()
    }
    
    fn permissions() -> Vec<String> {
        vec!["file:read".to_string(), "file:write".to_string()]
    }
    
    fn execute(task: String, config: String) -> Result<String, String> {
        let config: HashMap<String, serde_json::Value> = 
            serde_json::from_str(&config).unwrap_or_default();
        
        // Process task with config
        Ok(format!("Processed: {} with config: {:?}", task, config))
    }
    
    fn commands() -> Vec<Command> {
        vec![
            Command {
                name: "transform".to_string(),
                description: "Transform data format".to_string(),
                params: r#"{"type":"object","properties":{"input":{"type":"string"},"format":{"type":"string"}}}"#.to_string(),
            }
        ]
    }
}

export!(MySkill);
```

### Build
```bash
# Install wasm target
rustup target add wasm32-wasip1

# Build
cargo build --release --target wasm32-wasip1

# Output: target/wasm32-wasip1/release/my_wasm_skill.wasm
# Copy to plugin dir as skill.wasm
```

---

## SDK Reference

### Installation
```bash
pip install ele-agent-sdk
```

### Core Classes

#### SkillContext
```python
class SkillContext:
    session_id: str
    user_id: str
    config: Dict[str, Any]
    tools: ToolClient
    llm: LLMClient
    memory: MemoryClient
    logger: Logger
```

#### ToolClient
```python
class ToolClient:
    # File operations
    async def file.read(path: str) -> str
    async def file.write(path: str, content: str) -> None
    async def file.patch(path: str, diff: str) -> None
    async def file.stat(path: str) -> FileStat
    async def file.glob(pattern: str) -> List[FileStat]
    async def file.delete(path: str) -> None
    
    # Shell
    async def shell.run(cmd: str, cwd: str = None, timeout: int = 60) -> ShellResult
    
    # Browser (Playwright)
    async def browser.navigate(url: str) -> None
    async def browser.click(selector: str) -> None
    async def browser.type(selector: str, text: str) -> None
    async def browser.extract(selector: str) -> List[str]
    async def browser.screenshot() -> bytes
    async def browser.pdf() -> bytes
    
    # System
    async def system.open_app(name: str) -> None
    async def system.notify(title: str, message: str) -> None
```

#### LLMClient
```python
class LLMClient:
    async def complete(
        prompt: str,
        model: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str = None,
        tools: List[Dict] = None
    ) -> LLMResponse
    
    async def stream_complete(...) -> AsyncGenerator[str, None]
    
    async def embed(texts: List[str], model: str = "local") -> List[List[float]]
```

#### MemoryClient
```python
class MemoryClient:
    async def short_term.get() -> List[Message]
    async def short_term.add(message: Message) -> None
    
    async def long_term.search(query: str, k: int = 5) -> List[MemoryEntry]
    async def long_term.store(key: str, value: str, tags: List[str]) -> None
    
    async def episodic.record(action: str, result: str, success: bool) -> None
    async def episodic.recall(pattern: str) -> List[Episode]
```

---

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
```

---

## Marketplace Publishing

### Requirements
- Valid `skill.json` with all required fields
- Passes security scan (no malicious code, minimal permissions)
- Has README with usage examples
- Version follows semver
- Tests included (for Python/JSON formats)

### Review Process
1. Submit via web dashboard or CLI
2. Automated security scan (static analysis)
3. Community review (7 days)
4. Approved → Published
5. Updates: Auto-approved for patch versions, review for minor/major

### Revenue Share (Future)
- Free plugins: 0% platform fee
- Paid plugins: 15% platform fee
- Payouts: Monthly via Stripe Connect

---

## Security Best Practices

1. **Minimal Permissions**: Request only what you need
2. **Input Validation**: Sanitize all user inputs
3. **No Secrets in Code**: Use `config_schema` with `secret: true`
4. **Sandbox Awareness**: WASM plugins run in isolated environment
5. **Error Handling**: Never expose stack traces to users
6. **Dependencies**: Pin versions, audit regularly

---

## Migration Guide

### From v0 to v1
- `@skill` decorator replaces `register_skill()`
- `SkillContext` replaces `ctx` dict
- Tool access via `ctx.tools.*` instead of global functions
- Permissions declared in decorator/manifest, not code