"""Test RAG Indexer"""
import pytest
import tempfile
import os
from pathlib import Path
from app.rag.indexer import RAGIndexer


@pytest.fixture
def rag_indexer():
    """Create a RAG indexer with temp directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['DATA_DIR'] = tmpdir
        indexer = RAGIndexer()
        yield indexer


@pytest.mark.asyncio
async def test_rag_indexer_initialize(rag_indexer):
    """Test RAG indexer initialization"""
    await rag_indexer.initialize()
    assert rag_indexer._initialized is True


@pytest.mark.asyncio
async def test_rag_index_file(rag_indexer):
    """Test indexing a file"""
    await rag_indexer.initialize()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document about Python programming. Python is a great language.")
        f.flush()
        temp_path = f.name

    try:
        await rag_indexer.index_file(temp_path)

        # Search for content
        results = await rag_indexer.search("test-user", "Python", k=5)
        assert len(results) > 0
        assert any("Python" in r["content"] for r in results)
    finally:
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_rag_search_empty(rag_indexer):
    """Test search with no indexed documents"""
    await rag_indexer.initialize()
    results = await rag_indexer.search("test-user", "nonexistent", k=5)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_rag_remove_file(rag_indexer):
    """Test removing a file from index"""
    await rag_indexer.initialize()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Document to be removed")
        f.flush()
        temp_path = f.name

    try:
        await rag_indexer.index_file(temp_path)
        results = await rag_indexer.search("test-user", "removed", k=5)
        assert len(results) > 0

        await rag_indexer.remove_file(temp_path)
        results = await rag_indexer.search("test-user", "removed", k=5)
        assert len(results) == 0
    finally:
        os.unlink(temp_path)