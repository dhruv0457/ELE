"""Test Memory Manager"""
import pytest
import tempfile
import os
from app.memory.manager import MemoryManager


@pytest.fixture
def memory_manager():
    """Create a memory manager with temp database"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['DATA_DIR'] = tmpdir
        manager = MemoryManager()
        yield manager


@pytest.mark.asyncio
async def test_short_term_memory(memory_manager):
    """Test short-term memory operations"""
    session_id = "test-session"

    # Add messages
    await memory_manager.short_term_add(session_id, {"role": "user", "content": "Hello"})
    await memory_manager.short_term_add(session_id, {"role": "assistant", "content": "Hi there!"})

    # Retrieve messages
    messages = await memory_manager.short_term_get(session_id, limit=10)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there!"

    # Clear and verify
    await memory_manager.short_term_clear(session_id)
    messages = await memory_manager.short_term_get(session_id)
    assert len(messages) == 0


@pytest.mark.asyncio
async def test_long_term_memory(memory_manager):
    """Test long-term memory operations"""
    user_id = "test-user"

    # Set and get
    await memory_manager.long_term_set(user_id, "preference", "dark_mode", tags=["ui"], confidence=0.9)
    value = await memory_manager.long_term_get(user_id, "preference")
    assert value == "dark_mode"

    # Search
    results = await memory_manager.long_term_search(user_id, "dark", k=5)
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_episodic_memory(memory_manager):
    """Test episodic memory operations"""
    session_id = "test-session"

    # Record episode
    await memory_manager.episodic_record(session_id, "created file", "file created successfully", True, "Use write_file tool")

    # Recall
    episodes = await memory_manager.episodic_recall(session_id, pattern="file", limit=10)
    assert len(episodes) == 1
    assert episodes[0]["action"] == "created file"
    assert episodes[0]["success"] is True


@pytest.mark.asyncio
async def test_project_memory(memory_manager):
    """Test project memory operations"""
    user_id = "test-user"

    # Create project
    project_id = await memory_manager.project_create(user_id, "Test Project", "A test project")
    assert project_id is not None

    # Get project
    project = await memory_manager.project_get(project_id)
    assert project is not None
    assert project["name"] == "Test Project"
    assert project["user_id"] == user_id

    # Update files
    await memory_manager.project_update_files(project_id, ["file1.py", "file2.py"])
    project = await memory_manager.project_get(project_id)
    assert "file1.py" in project["files"]

    # Update todos
    await memory_manager.project_update_todos(project_id, [{"id": "1", "title": "Task 1", "completed": False}])
    project = await memory_manager.project_get(project_id)
    assert len(project["todos"]) == 1


@pytest.mark.asyncio
async def test_project_list(memory_manager):
    """Test listing projects"""
    user_id = "test-user-2"

    await memory_manager.project_create(user_id, "Project 1")
    await memory_manager.project_create(user_id, "Project 2")

    projects = await memory_manager.project_list(user_id)
    assert len(projects) == 2