#!/usr/bin/env python
"""Test script to verify project structure"""
import sys
import os

# Add project root to path so 'cli.src' and 'app' are proper packages
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, "backend"))
sys.path.insert(0, project_root)


def test_backend():
    """Test backend imports"""
    print("Testing backend imports...")
    
    try:
        from app.config.settings import settings
        print("✓ Backend config imported")
    except Exception as e:
        print(f"✗ Backend config: {e}")
        return False

    try:
        from app.db.models import User, Session
        print("✓ Backend models imported")
    except Exception as e:
        print(f"✗ Backend models: {e}")
        return False

    try:
        from app.memory.manager import MemoryManager
        print("✓ Memory manager imported")
    except Exception as e:
        print(f"✗ Memory manager: {e}")
        return False

    try:
        from app.executors.registry import ExecutorRegistry
        print("✓ Executor registry imported")
    except Exception as e:
        print(f"✗ Executor registry: {e}")
        return False

    return True


def test_cli():
    """Test CLI imports"""
    print("\nTesting CLI imports...")
    
    try:
        from cli.src.config import cli_config
        print("✓ CLI config imported")
    except Exception as e:
        print(f"✗ CLI config: {e}")
        return False

    try:
        from cli.src.store import store
        print("✓ CLI store imported")
    except Exception as e:
        print(f"✗ CLI store: {e}")
        return False

    try:
        from cli.src.widgets.message_bubble import MessageBubble
        print("✓ Message bubble imported")
    except Exception as e:
        print(f"✗ Message bubble: {e}")
        return False

    try:
        from cli.src.widgets.ellie_avatar import EllieAvatar
        print("✓ Ellie avatar imported")
    except Exception as e:
        print(f"✗ Ellie avatar: {e}")
        return False

    try:
        from cli.src.screens.chat import ChatScreen
        print("✓ Chat screen imported")
    except Exception as e:
        print(f"✗ Chat screen: {e}")
        return False

    return True


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    from app.config.settings import settings
    from cli.src.config import cli_config
    print(f"Backend URL: {settings.DATABASE_URL}")
    print(f"CLI Theme: {cli_config.theme}")
    print(f"Backend Port: {cli_config.backend_port}")
    print(f"Default Model: {cli_config.default_model}")
    print("✓ Configuration loaded")


def test_store():
    """Test store"""
    print("\nTesting store...")
    from cli.src.store import store, Message
    import uuid
    msg = Message(
        id=f"test_{uuid.uuid4().hex[:8]}",
        role="user",
        content="Test message",
        thoughts=["Thinking..."],
        tools_used=["file"],
    )
    store.add_message(msg)
    print(f"Messages: {len(store.messages)}")
    print(f"Session: {store.current_session_id}")
    print("✓ Store works")


if __name__ == "__main__":
    print("Testing ELE Agent...\n")
    
    backend_ok = True
    try:
        from app.config.settings import settings
        from app.db.models import User, Session
        from app.memory.manager import MemoryManager
        from app.executors.registry import ExecutorRegistry
        print("✓ Backend OK")
    except Exception as e:
        print(f"✗ Backend failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    cli_ok = True
    try:
        from cli.src.config import cli_config
        from cli.src.store import store
        from cli.src.widgets.message_bubble import MessageBubble
        from cli.src.widgets.ellie_avatar import EllieAvatar
        from cli.src.screens.chat import ChatScreen
        print("✓ CLI OK")
    except Exception as e:
        print(f"✗ CLI failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    test_config()
    test_store()
    print("\n✓ All tests passed!")