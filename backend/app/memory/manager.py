"""Memory Manager - Four-Layer Memory System"""
import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config.settings import settings
from app.rag.indexer import RAGIndexer


@dataclass
class MemoryEntry:
    id: int
    text: str
    tags: List[str]
    source: str
    timestamp: float


@dataclass
class Episode:
    id: int
    action: str
    result: str
    success: bool
    context: Dict[str, Any]
    tags: List[str]
    timestamp: float


class ShortTermMemory:
    """Conversation buffer - dynamic token budget"""

    def __init__(self, max_turns: int = 50, dynamic: bool = True):
        self.max_turns = max_turns
        self.dynamic = dynamic
        self.buffer: deque = deque(maxlen=max_turns)

    def add(self, message: Dict[str, Any]):
        self.buffer.append(message)

    def get(self, max_tokens: int = None) -> List[Dict[str, Any]]:
        if not self.dynamic or not max_tokens:
            return list(self.buffer)

        messages = []
        token_count = 0
        for msg in reversed(self.buffer):
            tokens = len(msg.get("content", "")) / 4  # Rough estimate
            if token_count + tokens > max_tokens:
                break
            messages.insert(0, msg)
            token_count += tokens
        return messages

    def clear(self):
        self.buffer.clear()


class LongTermMemory:
    """FAISS Vector Store for facts and knowledge"""

    def __init__(self, index_path: str, embedding_model: str = "bge-small"):
        self.index_path = Path(os.path.expanduser(index_path))
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.embedder = SentenceTransformer(embedding_model)
        self.dimension = self.embedder.get_sentence_embedding_dimension()

        self.index = self._load_index()
        self.metadata: List[Dict[str, Any]] = self._load_metadata()

    def _load_index(self) -> faiss.Index:
        index_file = self.index_path / "index.faiss"
        if index_file.exists():
            return faiss.read_index(str(index_file))
        return faiss.IndexFlatL2(self.dimension)

    def _load_metadata(self) -> List[Dict[str, Any]]:
        meta_file = self.index_path / "index.pkl"
        if meta_file.exists():
            import pickle
            with open(meta_file, "rb") as f:
                return pickle.load(f)
        return []

    def _save(self):
        import pickle
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "index.pkl", "wb") as f:
            pickle.dump(self.metadata, f)

    async def store(self, text: str, tags: List[str] = None, source: str = "user"):
        embedding = self.embedder.encode([text])[0].astype(np.float32)

        entry_id = len(self.metadata)
        self.index.add(np.array([embedding]))
        self.metadata.append({
            "id": entry_id,
            "text": text,
            "tags": tags or [],
            "source": source,
            "timestamp": time.time(),
        })
        self._save()

    async def search(self, query: str, k: int = 5, tags: List[str] = None) -> List[Dict[str, Any]]:
        if not self.metadata:
            return []

        query_embedding = self.embedder.encode([query])[0].astype(np.float32)
        distances, indices = self.index.search(
            np.array([query_embedding]),
            min(k * 3, len(self.metadata))
        )

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                entry = self.metadata[idx]
                if tags and not any(t in entry.get("tags", []) for t in tags):
                    continue
                entry = entry.copy()
                entry["score"] = float(1 / (1 + dist))
                results.append(entry)
                if len(results) >= k:
                    break
        return results


class EpisodicMemory:
    """SQLite for action outcomes and lessons"""

    def __init__(self, db_path: str, embedder: SentenceTransformer):
        self.db_path = Path(os.path.expanduser(db_path))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder
        self._init_db()

    def _init_db(self):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    result TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    context TEXT,
                    tags TEXT,
                    embedding BLOB,
                    timestamp REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON episodes(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_success ON episodes(success)")

    async def record(self, action: str, result: str, success: bool,
                     context: Dict = None, tags: List[str] = None):
        import sqlite3
        embedding = self.embedder.encode([f"Action: {action}\nResult: {result}"])[0]

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO episodes (action, result, success, context, tags, embedding, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                action, result, success,
                json.dumps(context or {}),
                json.dumps(tags or []),
                embedding.astype(np.float32).tobytes(),
                time.time()
            ))

    async def recall(self, pattern: str, k: int = 10, success_only: bool = False) -> List[Dict[str, Any]]:
        import sqlite3
        query_embedding = self.embedder.encode([pattern])[0]

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT id, action, result, success, context, tags, embedding, timestamp
                FROM episodes
                WHERE success = ? OR ? = 1
                ORDER BY timestamp DESC
                LIMIT 1000
            """, (success_only, success_only)).fetchall()

        episodes = []
        for row in rows:
            ep_embedding = np.frombuffer(row[6], dtype=np.float32)
            sim = np.dot(query_embedding, ep_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(ep_embedding)
            )
            episodes.append((sim, {
                "id": row[0], "action": row[1], "result": row[2],
                "success": row[3], "context": json.loads(row[4]),
                "tags": json.loads(row[5]), "timestamp": row[7],
            }))

        episodes.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in episodes[:k]]


class ProjectMemory:
    """Active project context with file watching"""

    def __init__(self, watch_paths: List[str], marker_files: List[str]):
        self.watch_paths = [Path(os.path.expanduser(p)) for p in watch_paths]
        self.marker_files = marker_files
        self.projects: Dict[str, Dict[str, Any]] = {}
        self._load_projects()

    def _load_projects(self):
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
            for root, dirs, files in os.walk(watch_path):
                if any(m in files for m in self.marker_files):
                    rel_path = os.path.relpath(root, watch_path)
                    self.projects[rel_path] = self._scan_project(root)

    def _scan_project(self, path: str) -> Dict[str, Any]:
        files = {}
        for root, _, filenames in os.walk(path):
            for f in filenames:
                if self._should_index(f):
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, path)
                    stat = os.stat(full)
                    with open(full, 'r', errors='ignore') as fp:
                        content = fp.read(5000)
                    files[rel] = {
                        "hash": hash(content),
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                        "summary": self._summarize(content, f)
                    }
        return {
            "name": os.path.basename(path),
            "path": path,
            "files": files,
            "todos": [],
            "specs": [],
            "last_updated": time.time(),
        }

    def _should_index(self, filename: str) -> bool:
        ext = os.path.splitext(filename)[1]
        return ext in {'.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml', '.toml'}

    def _summarize(self, content: str, filename: str) -> str:
        lines = content.split('\n')[:30]
        return '\n'.join(lines)

    def get_context(self, project_name: str, max_files: int = 20) -> str:
        project = self.projects.get(project_name)
        if not project:
            return ""

        sorted_files = sorted(project["files"].items(), key=lambda x: x[1]["mtime"], reverse=True)

        context = f"# Project: {project['name']}\n\n"
        for rel, info in sorted_files[:max_files]:
            context += f"## {rel}\n{info['summary']}\n\n"
        return context


class MemoryManager:
    """Unified memory interface"""

    def __init__(self):
        embedder = SentenceTransformer(settings.memory.long_term.embedding_model)

        self.short_term = ShortTermMemory(
            max_turns=settings.memory.short_term.max_turns,
            dynamic=settings.memory.short_term.dynamic
        )
        self.long_term = LongTermMemory(
            settings.memory.long_term.index_path,
            settings.memory.long_term.embedding_model
        )
        self.episodic = EpisodicMemory(
            settings.memory.episodic.db_path,
            embedder
        )
        self.project = ProjectMemory(
            settings.memory.project.watch_paths,
            settings.memory.project.marker_files
        )
        self.rag = RAGIndexer()

    async def get_context(self, query: str, project: str = None, max_tokens: int = 2000) -> str:
        parts = []

        # Short-term
        recent = self.short_term.get(max_tokens=max_tokens)
        if recent:
            parts.append("## Recent Conversation")
            for msg in recent[-10:]:
                parts.append(f"{msg['role']}: {msg['content'][:200]}")

        # Long-term
        ltm_results = await self.long_term.search(query, k=5)
        if ltm_results:
            parts.append("\n## Relevant Memories")
            for r in ltm_results:
                parts.append(f"- {r['text'][:200]}")

        # Project
        if project:
            proj_ctx = self.project.get_context(project)
            if proj_ctx:
                parts.append(f"\n## Project Context\n{proj_ctx}")

        # Episodic
        episodes = await self.episodic.recall(query, k=3, success_only=True)
        if episodes:
            parts.append("\n## Lessons Learned")
            for ep in episodes:
                parts.append(f"- {ep['action']} → {ep['result']}")

        return "\n".join(parts)