"""Plugin Loader - Python, JSON, WASM"""
import os
import json
import importlib.util
import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger()


class PluginManifest:
    """Plugin manifest describing metadata and permissions."""

    def __init__(self, data: Dict[str, Any]):
        self.raw = dict(data)
        self.id = data.get("id", "")
        self.name = data.get("name", self.id)
        self.version = data.get("version", "0.0.0")
        self.description = data.get("description", "")
        self.author = data.get("author", "")
        self.permissions = list(data.get("permissions", []))
        self.config_schema = dict(data.get("config_schema", {}))
        self.runtime = data.get("runtime", "python")
        self.entry_point = data.get("entry_point", "main:skill")


@dataclass
class Plugin:
    """A loaded plugin instance."""

    manifest: PluginManifest
    path: Path
    instance: Any = None
    enabled: bool = True


MANIFEST_FILE = "manifest.json"


class PluginLoader:
    def __init__(self, plugins_dir: Optional[str] = None):
        if plugins_dir is None:
            data_dir = os.environ.get("DATA_DIR") or ""
            if data_dir:
                base = Path(os.path.expanduser(data_dir)) / "plugins"
            else:
                base = Path(os.path.expanduser("~/.ele-agent/plugins"))
        else:
            base = Path(os.path.expanduser(plugins_dir))
        self.plugin_dir = base
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, Plugin] = {}

    async def discover_plugins(self) -> List[PluginManifest]:
        """Discover all plugin manifests in the plugins directory."""
        manifests: List[PluginManifest] = []
        if not self.plugin_dir.exists():
            return manifests
        for plugin_path in self.plugin_dir.iterdir():
            if not plugin_path.is_dir():
                continue
            manifest_path = plugin_path / MANIFEST_FILE
            if not manifest_path.exists():
                continue
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
                manifests.append(PluginManifest(data))
            except Exception as e:
                logger.error("plugin_manifest_error", path=str(plugin_path), error=str(e))
        return manifests

    async def load_all(self):
        """Load all plugins from plugins directory."""
        manifests = await self.discover_plugins()
        for manifest in manifests:
            await self.load_plugin(manifest)

    async def load_plugin(self, manifest: PluginManifest) -> Optional[Plugin]:
        """Load a single plugin from its manifest."""
        plugin_path = self.plugin_dir / manifest.id
        if not plugin_path.exists():
            logger.error("plugin_not_found", id=manifest.id)
            return None

        instance: Any = None
        if manifest.runtime == "python":
            instance = await self._load_python_plugin(plugin_path, manifest)
        elif manifest.runtime == "wasm":
            instance = await self._load_wasm_plugin(plugin_path, manifest)
        elif manifest.runtime == "json":
            instance = await self._load_json_plugin(plugin_path, manifest)

        plugin = Plugin(manifest=manifest, path=plugin_path, instance=instance)
        self.plugins[manifest.id] = plugin
        return plugin

    async def _load_python_plugin(self, plugin_path: Path, manifest: PluginManifest) -> Optional[Any]:
        """Load a Python plugin from a manifest."""
        module_path, _, class_name = manifest.entry_point.partition(":")
        if not class_name:
            class_name = "skill"
        main_py = plugin_path / f"{module_path}.py"
        if not main_py.exists():
            main_py = plugin_path / "main.py"
        if not main_py.exists():
            return None

        spec = importlib.util.spec_from_file_location(manifest.id, main_py)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)

        import sys
        sys.path.insert(0, str(plugin_path))
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.error("plugin_load_error", path=str(plugin_path), error=str(e))
            return None
        finally:
            try:
                sys.path.remove(str(plugin_path))
            except ValueError:
                pass

        plugin_class = getattr(module, class_name, None)
        if plugin_class is not None:
            try:
                return plugin_class(manifest.config_schema or {})
            except Exception as e:
                logger.error("plugin_init_error", id=manifest.id, error=str(e))
                return None

        for obj in module.__dict__.values():
            if hasattr(obj, "_skill_meta"):
                try:
                    return obj(manifest.config_schema or {})
                except Exception as e:
                    logger.error("plugin_init_error", id=manifest.id, error=str(e))
        return None

    async def _load_json_plugin(self, plugin_path: Path, manifest: PluginManifest) -> Optional[Any]:
        """Load a JSON function-based plugin."""
        return await self._load_python_plugin(plugin_path, manifest)

    async def _load_wasm_plugin(self, plugin_path: Path, manifest: PluginManifest) -> Optional[Any]:
        """Load a WASM plugin using Wasmtime."""
        try:
            import wasmtime
            wasm_file = plugin_path / "skill.wasm"
            if not wasm_file.exists():
                return None
            engine = wasmtime.Engine()
            module = wasmtime.Module.from_file(engine, str(wasm_file))
            linker = wasmtime.Linker(engine)
            store = wasmtime.Store(engine)
            instance = linker.instantiate(store, module)
            return instance
        except Exception as e:
            logger.error("wasm_load_error", path=str(plugin_path), error=str(e))
            return None

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        return self.plugins.get(plugin_id)

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": plugin.manifest.id,
                "name": plugin.manifest.name,
                "version": plugin.manifest.version,
                "enabled": plugin.enabled,
                "path": str(plugin.path),
            }
            for plugin in self.plugins.values()
        ]

    async def enable_plugin(self, plugin_id: str) -> bool:
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return False
        plugin.enabled = True
        return True

    async def disable_plugin(self, plugin_id: str) -> bool:
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return False
        plugin.enabled = False
        return True

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        plugin = self.plugins.pop(plugin_id, None)
        plugin_path = self.plugin_dir / plugin_id
        if plugin_path.exists():
            shutil.rmtree(plugin_path, ignore_errors=True)
        return plugin is not None or plugin_path.exists() is False
