"""Test Plugin Loader"""
import pytest
import tempfile
import os
import json
from pathlib import Path
from app.plugins.loader import PluginLoader, PluginManifest


@pytest.fixture
def plugin_loader():
    """Create a plugin loader with temp directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['DATA_DIR'] = tmpdir
        loader = PluginLoader()
        yield loader


@pytest.fixture
def sample_plugin_dir(plugin_loader):
    """Create a sample plugin directory"""
    plugin_dir = plugin_loader.plugin_dir / "test-plugin"
    plugin_dir.mkdir()

    manifest = {
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "author": "test-author",
        "permissions": ["file:read"],
        "config_schema": {}
    }

    with open(plugin_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)

    return plugin_dir


def test_plugin_manifest():
    """Test PluginManifest creation"""
    data = {
        "id": "test",
        "name": "Test",
        "version": "1.0.0",
        "description": "Test plugin",
        "author": "author",
        "permissions": ["file:read"]
    }
    manifest = PluginManifest(data)
    assert manifest.id == "test"
    assert manifest.name == "Test"
    assert manifest.version == "1.0.0"
    assert manifest.permissions == ["file:read"]


@pytest.mark.asyncio
async def test_discover_plugins(plugin_loader, sample_plugin_dir):
    """Test plugin discovery"""
    manifests = await plugin_loader.discover_plugins()
    assert len(manifests) == 1
    assert manifests[0].id == "test-plugin"
    assert manifests[0].name == "Test Plugin"


@pytest.mark.asyncio
async def test_load_plugin(plugin_loader, sample_plugin_dir):
    """Test loading a plugin"""
    manifests = await plugin_loader.discover_plugins()
    plugin = await plugin_loader.load_plugin(manifests[0])

    assert plugin.manifest.id == "test-plugin"
    assert plugin.enabled is True
    assert "test-plugin" in plugin_loader.plugins


@pytest.mark.asyncio
async def test_list_plugins(plugin_loader, sample_plugin_dir):
    """Test listing plugins"""
    await plugin_loader.load_all()
    plugins = plugin_loader.list_plugins()

    assert len(plugins) == 1
    assert plugins[0]["id"] == "test-plugin"
    assert plugins[0]["name"] == "Test Plugin"
    assert plugins[0]["enabled"] is True


@pytest.mark.asyncio
async def test_enable_disable_plugin(plugin_loader, sample_plugin_dir):
    """Test enabling/disabling plugins"""
    await plugin_loader.load_all()

    await plugin_loader.disable_plugin("test-plugin")
    plugin = plugin_loader.get_plugin("test-plugin")
    assert plugin.enabled is False

    await plugin_loader.enable_plugin("test-plugin")
    plugin = plugin_loader.get_plugin("test-plugin")
    assert plugin.enabled is True


@pytest.mark.asyncio
async def test_uninstall_plugin(plugin_loader, sample_plugin_dir):
    """Test uninstalling a plugin"""
    await plugin_loader.load_all()

    await plugin_loader.uninstall_plugin("test-plugin")
    assert "test-plugin" not in plugin_loader.plugins
    assert not sample_plugin_dir.exists()