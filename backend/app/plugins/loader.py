"""Plugin Loader - Python, JSON, WASM"""
import os
import json
import importlib.util
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class PluginLoader:
    def __init__(self, plugins_dir: str = "~/.ele-agent/plugins"):
        self.plugins_dir = Path(os.path.expanduser(plugins_dir))
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins: Dict[str, Any] = {}

    async def load_all(self):
        """Load all plugins from plugins directory"""
        for plugin_path in self.plugins_dir.iterdir():
            if plugin_path.is_dir():
                await self.load_plugin(plugin_path)

    async def load_plugin(self, plugin_path: Path) -> Optional[Any]:
        """Load a single plugin"""
        manifest_path = plugin_path / "skill.json"
        if not manifest_path.exists():
            # Check for Python @skill format
            main_py = plugin_path / "main.py"
            if main_py.exists():
                return await self._load_python_skill(plugin_path)
            return None

        with open(manifest_path) as f:
            manifest = json.load(f)

        runtime = manifest.get("runtime", "python")
        entry_point = manifest.get("entry_point", "main:skill")

        if runtime == "python":
            return await self._load_python_plugin(plugin_path, entry_point)
        elif runtime == "wasm":
            return await self._load_wasm_plugin(plugin_path, entry_point)
        elif runtime == "json":
            return await self._load_json_plugin(plugin_path, entry_point)

        return None

    async def _load_python_skill(self, plugin_path: Path) -> Optional[Any]:
        """Load Python @skill decorated class"""
        main_py = plugin_path / "main.py"
        spec = importlib.util.spec_from_file_location("skill", main_py)
        module = importlib.util.module_from_spec(spec)

        # Add plugin directory to sys.path for imports
        import sys
        sys.path.insert(0, str(plugin_path))

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.error("plugin_load_error", path=str(plugin_path), error=str(e))
            return None

        # Find @skill decorated class
        for name, obj in module.__dict__.items():
            if hasattr(obj, "_skill_meta"):
                meta = obj._skill_meta
                instance = obj({})  # Pass empty config for now
                self.loaded_plugins[meta["name"]] = {
                    "instance": instance,
                    "manifest": meta,
                    "path": plugin_path,
                }
                return instance

        return None

    async def _load_python_plugin(self, plugin_path: Path, entry_point: str) -> Optional[Any]:
        """Load JSON manifest Python plugin"""
        module_path, class_name = entry_point.split(":")
        main_py = plugin_path / f"{module_path}.py"
        if not main_py.exists():
            main_py = plugin_path / "main.py"

        spec = importlib.util.spec_from_file_location(module_path, main_py)
        module = importlib.util.module_from_spec(spec)

        import sys
        sys.path.insert(0, str(plugin_path))

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.error("plugin_load_error", path=str(plugin_path), error=str(e))
            return None

        plugin_class = getattr(module, class_name, None)
        if plugin_class:
            instance = plugin_class({})
            self.loaded_plugins[plugin_path.name] = {
                "instance": instance,
                "manifest": None,
                "path": plugin_path,
            }
            return instance

        return None

    async def _load_json_plugin(self, plugin_path: Path, entry_point: str) -> Optional[Any]:
        """Load JSON manifest plugin (function-based)"""
        # Similar to python plugin but expects functions
        return await self._load_python_plugin(plugin_path, entry_point)

    async def _load_wasm_plugin(self, plugin_path: Path, entry_point: str) -> Optional[Any]:
        """Load WASM plugin using Wasmtime"""
        try:
            import wasmtime
            wasm_file = plugin_path / "skill.wasm"
            if not wasm_file.exists():
                return None

            engine = wasmtime.Engine()
            module = wasmtime.Module.from_file(engine, str(wasm_file))
            linker = wasmtime.Linker(engine)

            # Define host functions
            # TODO: Implement host function bindings

            store = wasmtime.Store(engine)
            instance = linker.instantiate(store, module)

            self.loaded_plugins[plugin_path.name] = {
                "instance": instance,
                "store": store,
                "manifest": None,
                "path": plugin_path,
            }
            return instance

        except Exception as e:
            logger.error("wasm_load_error", path=str(plugin_path), error=str(e))
            return None

    def get_plugin(self, name: str) -> Optional[Any]:
        return self.loaded_plugins.get(name, {}).get("instance")

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "path": str(info["path"]),
                "loaded": info["instance"] is not None,
            }
            for name, info in self.loaded_plugins.items()
        ]