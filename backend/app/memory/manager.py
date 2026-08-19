"""Memory Manager - Four-Layer Memory System"""
import os
import json
import time
import asyncio
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid as _uuid

try:
    import faiss
except ImportError:
    faiss = None

try:
    import numpy as np
except ImportError:
    np = None

from contextlib import contextmanager

from app.config.settings import settings
from app.rag.indexer import RAGIndexer
from app.rag.embedder import get_embedder, FALLBACK_DIM


@contextmanager
def _open_db(path):
    """Open a sqlite connection that actually closes (unlike `with conn`)."""
    conn = sqlite3.connect(str(path))
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


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

    def __init__(self, index_path: str = None, embedding_model: str = "bge-small"):
        data_dir = os.environ.get("DATA_DIR")
        if index_path:
            base = Path(os.path.expanduser(index_path))
        elif data_dir:
            base = Path(os.path.expanduser(data_dir)) / "memory" / "faiss"
        else:
            base = Path(os.path.expanduser(settings.memory.long_term.index_path))
        self.index_path = base
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.embedder = get_embedder(embedding_model, dim=FALLBACK_DIM)
        try:
            self.dimension = self.embedder.get_sentence_embedding_dimension()
        except Exception:
            self.dimension = FALLBACK_DIM

        self.index = self._load_index()
        self.metadata: List[Dict[str, Any]] = self._load_metadata()

    def _load_index(self):
        if faiss is None:
            return None
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
        if faiss is not None and self.index is not None:
            faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "index.pkl", "wb") as f:
            pickle.dump(self.metadata, f)

    async def store(self, text: str, tags: List[str] = None, source: str = "user"):
        if faiss is None or np is None or self.index is None:
            entry_id = len(self.metadata)
            self.metadata.append({
                "id": entry_id,
                "text": text,
                "tags": tags or [],
                "source": source,
                "timestamp": time.time(),
            })
            self._save()
            return

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

        if faiss is None or np is None or self.index is None:
            # Fallback simple keyword match
            q_lower = query.lower()
            matches = [m for m in self.metadata if q_lower in m.get("text", "").lower()]
            return matches[:k]

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

    def __init__(self, db_path: str = None, embedder=None):
        data_dir = os.environ.get("DATA_DIR")
        if db_path:
            self.db_path = Path(os.path.expanduser(db_path))
        elif data_dir:
            self.db_path = Path(os.path.expanduser(data_dir)) / "memory" / "episodic.db"
        else:
            self.db_path = Path(os.path.expanduser(settings.memory.episodic.db_path))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder
        self._init_db()

    def _init_db(self):
        with _open_db(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    action TEXT NOT NULL,
                    result TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    tool TEXT,
                    context TEXT,
                    tags TEXT,
                    embedding BLOB,
                    timestamp REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON episodes(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON episodes(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_success ON episodes(success)")

    async def record(self, session_id: str, action: str, result: str, success: bool,
                     tool: str = None, tags: List[str] = None, context: Dict = None):
        text = f"Action: {action}\nResult: {result}"
        embedding = self.embedder.encode([text])[0] if self.embedder is not None else np.zeros(FALLBACK_DIM, dtype=np.float32)

        with _open_db(self.db_path) as conn:
            conn.execute("""
                INSERT INTO episodes
                (session_id, action, result, success, tool, context, tags, embedding, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, action, result, success, tool,
                json.dumps(context or {}),
                json.dumps(tags or []),
                embedding.astype(np.float32).tobytes(),
                time.time()
            ))

    async def recall(self, session_id: str = None, pattern: str = None,
                     k: int = 10, success_only: bool = False) -> List[Dict[str, Any]]:
        where = []
        params: List[Any] = []
        if success_only:
            where.append("success = 1")
        if session_id:
            where.append("session_id = ?")
            params.append(session_id)
        where_clause = " AND ".join(where) if where else "1=1"

        with _open_db(self.db_path) as conn:
            rows = conn.execute(
                f"""SELECT id, session_id, action, result, success, tool, context, tags, timestamp
                    FROM episodes WHERE {where_clause}
                    ORDER BY timestamp DESC LIMIT 1000""",
                params
            ).fetchall()

        if pattern:
            pat = pattern.lower()
            rows = [r for r in rows if pat in r[2].lower() or pat in r[3].lower()]

        return [
            {
                "id": row[0], "session_id": row[1], "action": row[2],
                "result": row[3], "success": bool(row[4]), "tool": row[5],
                "context": json.loads(row[6]), "tags": json.loads(row[7]),
                "timestamp": row[8],
            }
            for row in rows[:k]
        ]


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
        embedder = get_embedder(settings.memory.long_term.embedding_model, dim=FALLBACK_DIM)

        self.short_term = ShortTermMemory(
            max_turns=settings.memory.short_term.max_turns,
            dynamic=settings.memory.short_term.dynamic
        )
        self.long_term = LongTermMemory(
            settings.memory.long_term.index_path,
            settings.memory.long_term.embedding_model
        )
        data_dir_env = os.environ.get("DATA_DIR")
        episodic_db = None if data_dir_env else settings.memory.episodic.db_path
        self.episodic = EpisodicMemory(episodic_db, embedder)
        self.project = ProjectMemory(
            settings.memory.project.watch_paths,
            settings.memory.project.marker_files
        )
        self.rag = RAGIndexer()

        # Per-session short-term buffers (test contract: session-scoped)
        self._sessions: Dict[str, ShortTermMemory] = {}

        # SQLite store for long-term KV and projects
        data_dir = os.environ.get("DATA_DIR")
        if data_dir:
            base = Path(os.path.expanduser(data_dir)) / "memory"
        else:
            base = Path(os.path.expanduser(settings.DATA_DIR)) / "memory"
        base.mkdir(parents=True, exist_ok=True)
        self._store_path = base / "manager.db"
        self._init_store()

    def _init_store(self):
        with _open_db(self._store_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term (
                    user_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    tags TEXT,
                    confidence REAL,
                    timestamp REAL NOT NULL,
                    PRIMARY KEY (user_id, key)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    files TEXT,
                    todos TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id)")

    def _session(self, session_id: str) -> ShortTermMemory:
        if session_id not in self._sessions:
            self._sessions[session_id] = ShortTermMemory(
                max_turns=settings.memory.short_term.max_turns,
                dynamic=settings.memory.short_term.dynamic
            )
        return self._sessions[session_id]

    async def short_term_add(self, session_id: str, message: Dict[str, Any]) -> None:
        self._session(session_id).add(message)

    async def short_term_get(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        messages = list(self._session(session_id).buffer)
        if limit is not None:
            messages = messages[:limit]
        return messages

    async def short_term_clear(self, session_id: str) -> None:
        self._session(session_id).clear()

    async def long_term_set(self, user_id: str, key: str, value: Any,
                            tags: List[str] = None, confidence: float = 1.0) -> None:
        with _open_db(self._store_path) as conn:
            conn.execute("""
                INSERT INTO long_term (user_id, key, value, tags, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, key) DO UPDATE SET
                    value=excluded.value, tags=excluded.tags,
                    confidence=excluded.confidence, timestamp=excluded.timestamp
            """, (
                user_id, key, json.dumps(value) if not isinstance(value, str) else value,
                json.dumps(tags or []), confidence, time.time()
            ))

    async def long_term_get(self, user_id: str, key: str) -> Any:
        with _open_db(self._store_path) as conn:
            row = conn.execute(
                "SELECT value FROM long_term WHERE user_id=? AND key=?",
                (user_id, key)
            ).fetchone()
        if row is None:
            return None
        value = row[0]
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def long_term_search(self, user_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        like = f"%{query.lower()}%"
        with _open_db(self._store_path) as conn:
            rows = conn.execute(
                "SELECT user_id, key, value, tags, confidence FROM long_term "
                "WHERE user_id=? AND LOWER(value) LIKE ? LIMIT ?",
                (user_id, like, k)
            ).fetchall()
        results = []
        for row in rows:
            value = row[2]
            try:
                parsed = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                parsed = value
            results.append({
                "user_id": row[0], "key": row[1], "value": parsed,
                "tags": json.loads(row[3] or "[]"), "confidence": row[4],
            })
        return results

    async def episodic_record(self, session_id: str, action: str, result: str,
                              success: bool, tool: str = None,
                              tags: List[str] = None) -> None:
        await self.episodic.record(session_id, action, result, success, tool=tool, tags=tags)

    async def episodic_recall(self, session_id: str, pattern: str = None,
                              limit: int = 10) -> List[Dict[str, Any]]:
        return await self.episodic.recall(session_id=session_id, pattern=pattern, k=limit)

    async def project_create(self, user_id: str, name: str,
                             description: str = None) -> str:
        project_id = f"proj_{_uuid.uuid4().hex[:12]}"
        with _open_db(self._store_path) as conn:
            conn.execute(
                "INSERT INTO projects (id, user_id, name, description, files, todos, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (project_id, user_id, name, description, json.dumps([]), json.dumps([]), time.time())
            )
        return project_id

    async def project_get(self, project_id: str) -> Optional[Dict[str, Any]]:
        with _open_db(self._store_path) as conn:
            row = conn.execute(
                "SELECT id, user_id, name, description, files, todos, timestamp FROM projects WHERE id=?",
                (project_id,)
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0], "user_id": row[1], "name": row[2],
            "description": row[3],
            "files": json.loads(row[4] or "[]"),
            "todos": json.loads(row[5] or "[]"),
            "timestamp": row[6],
        }

    async def project_update_files(self, project_id: str, files: List[str]) -> None:
        with _open_db(self._store_path) as conn:
            conn.execute(
                "UPDATE projects SET files=?, timestamp=? WHERE id=?",
                (json.dumps(files), time.time(), project_id)
            )

    async def project_update_todos(self, project_id: str, todos: List[Dict[str, Any]]) -> None:
        with _open_db(self._store_path) as conn:
            conn.execute(
                "UPDATE projects SET todos=?, timestamp=? WHERE id=?",
                (json.dumps(todos), time.time(), project_id)
            )

    async def project_list(self, user_id: str) -> List[Dict[str, Any]]:
        with _open_db(self._store_path) as conn:
            rows = conn.execute(
                "SELECT id, user_id, name, description, files, todos, timestamp FROM projects WHERE user_id=? ORDER BY timestamp",
                (user_id,)
            ).fetchall()
        return [
            {
                "id": row[0], "user_id": row[1], "name": row[2],
                "description": row[3], "files": json.loads(row[4] or "[]"),
                "todos": json.loads(row[5] or "[]"), "timestamp": row[6],
            }
            for row in rows
        ]

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
                parts.append(f"- {r.get('text', '')[:200]}")

        # Project
        if project:
            proj_ctx = self.project.get_context(project)
            if proj_ctx:
                parts.append(f"\n## Project Context\n{proj_ctx}")

        # Episodic
        episodes = await self.episodic.recall(pattern=query, k=3, success_only=True)
        if episodes:
            parts.append("\n## Lessons Learned")
            for ep in episodes:
                parts.append(f"- {ep['action']} → {ep['result']}")

        return "\n".join(parts)