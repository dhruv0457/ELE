# Memory & RAG Design

## Overview

Four-layer memory architecture with local-first storage:

| Layer | Storage | Retention | Purpose |
|-------|---------|-----------|---------|
| **Short-term** | In-memory (deque) | Session | Conversation buffer |
| **Long-term** | FAISS + SQLite | Forever | Facts, preferences, knowledge |
| **Episodic** | SQLite | Forever | Action outcomes, lessons |
| **Project** | JSON + File watcher | Active | Current project context |

## Storage Locations

```
~/.ele-agent/
├── memory/
│   ├── faiss/                 # Vector index
│   │   ├── index.faiss        # FAISS binary
│   │   └── index.pkl          # Metadata (id → text, tags)
│   ├── episodic.db            # SQLite for episodes
│   └── projects/              # Per-project context
│       ├── my-api.json
│       └── website-redesign.json
├── sessions/
│   ├── session_abc123.jsonl   # Conversation history
│   └── index.sqlite           # Session metadata
└── logs/
    └── memory.log
```

## 1. Short-Term Memory (Conversation Buffer)

```python
# backend/app/memory/short_term.py
from collections import deque
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Message:
    role: str  # user, assistant, system, tool
    content: str
    timestamp: float
    metadata: dict = None

class ShortTermMemory:
    def __init__(self, max_turns: int = 50, dynamic: bool = True):
        self.max_turns = max_turns
        self.dynamic = dynamic
        self.buffer: deque[Message] = deque(maxlen=max_turns)
    
    def add(self, message: Message):
        self.buffer.append(message)
    
    def get(self, max_tokens: int = None) -> List[Message]:
        if not self.dynamic or not max_tokens:
            return list(self.buffer)
        
        # Dynamic: fit in token budget
        messages = []
        token_count = 0
        for msg in reversed(self.buffer):
            tokens = estimate_tokens(msg.content)
            if token_count + tokens > max_tokens:
                break
            messages.insert(0, msg)
            token_count += tokens
        return messages
    
    def clear(self):
        self.buffer.clear()
```

### Token Budget Integration

```python
# In agent graph
async def llm_nodes_parallel(state: AgentState) -> AgentState:
    # Get model max context
    model = state["model_preference"]
    max_context = MODEL_CONTEXTS.get(model, 4096)
    
    # Reserve tokens for response + tools + system
    reserved = 2000
    available = max_context - reserved
    
    # Get short-term messages fitting budget
    short_term = memory.short_term.get(max_tokens=available)
    state["messages"] = short_term + state["messages"]  # Prepend
```

## 2. Long-Term Memory (FAISS Vector Store)

```python
# backend/app/memory/long_term.py
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

class LongTermMemory:
    def __init__(self, index_path: str, embedding_model: str = "bge-small"):
        self.index_path = index_path
        self.embedder = SentenceTransformer(embedding_model)
        self.dimension = self.embedder.get_sentence_embedding_dimension()  # 384 for bge-small
        
        # Load or create index
        self.index = self._load_index()
        self.metadata = self._load_metadata()  # List[MemoryEntry]
    
    def _load_index(self) -> faiss.Index:
        index_file = f"{self.index_path}/index.faiss"
        if os.path.exists(index_file):
            return faiss.read_index(index_file)
        return faiss.IndexFlatL2(self.dimension)
    
    def _load_metadata(self) -> List[dict]:
        meta_file = f"{self.index_path}/index.pkl"
        if os.path.exists(meta_file):
            with open(meta_file, "rb") as f:
                return pickle.load(f)
        return []
    
    def _save(self):
        faiss.write_index(self.index, f"{self.index_path}/index.faiss")
        with open(f"{self.index_path}/index.pkl", "wb") as f:
            pickle.dump(self.metadata, f)
    
    async def store(self, text: str, tags: List[str] = None, source: str = "user"):
        """Store a memory entry"""
        embedding = self.embedder.encode([text])[0].astype(np.float32)
        
        entry_id = len(self.metadata)
        self.index.add(np.array([embedding]))
        self.metadata.append({
            "id": entry_id,
            "text": text,
            "tags": tags or [],
            "source": source,
            "timestamp": time.time()
        })
        self._save()
    
    async def search(self, query: str, k: int = 5, tags: List[str] = None) -> List[dict]:
        """Semantic search with optional tag filter"""
        query_embedding = self.embedder.encode([query])[0].astype(np.float32)
        
        # Search more than k to allow filtering
        distances, indices = self.index.search(np.array([query_embedding]), k * 3)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= len(self.metadata):
                continue
            entry = self.metadata[idx]
            if tags and not any(t in entry["tags"] for t in tags):
                continue
            entry["score"] = float(1 / (1 + dist))  # Convert to similarity
            results.append(entry)
            if len(results) >= k:
                break
        
        return results
    
    async def rebuild(self, texts: List[str], tags_list: List[List[str]] = None):
        """Full rebuild (on session start)"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        self.index.add(embeddings.astype(np.float32))
        
        for i, (text, tags) in enumerate(zip(texts, tags_list or [[]] * len(texts))):
            self.metadata.append({
                "id": i,
                "text": text,
                "tags": tags,
                "source": "rebuild",
                "timestamp": time.time()
            })
        self._save()
```

### Embedding Model: BGE-Small
- **Model**: `BAAI/bge-small-en-v1.5`
- **Dimension**: 384
- **Speed**: ~1000 texts/sec on CPU
- **Quality**: Excellent for code + text
- **Local**: Runs entirely offline

## 3. Episodic Memory (Action Outcomes)

```python
# backend/app/memory/episodic.py
import sqlite3
import json
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Episode:
    id: int
    action: str
    result: str
    success: bool
    context: dict
    tags: List[str]
    timestamp: float
    embedding: Optional[np.ndarray] = None

class EpisodicMemory:
    def __init__(self, db_path: str, embedder: SentenceTransformer):
        self.db_path = db_path
        self.embedder = embedder
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    result TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    context TEXT,  -- JSON
                    tags TEXT,     -- JSON array
                    embedding BLOB, -- FAISS-compatible
                    timestamp REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON episodes(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_success ON episodes(success)")
    
    async def record(self, action: str, result: str, success: bool, 
                     context: dict = None, tags: List[str] = None):
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
    
    async def recall(self, pattern: str, k: int = 10, success_only: bool = False) -> List[Episode]:
        """Semantic search for similar episodes"""
        query_embedding = self.embedder.encode([pattern])[0]
        
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT id, action, result, success, context, tags, embedding, timestamp
                FROM episodes
                WHERE success = ? OR ? = 1
                ORDER BY timestamp DESC
                LIMIT 1000
            """, (success_only, success_only)).fetchall()
        
        # Compute similarities
        episodes = []
        for row in rows:
            ep_embedding = np.frombuffer(row[6], dtype=np.float32)
            sim = np.dot(query_embedding, ep_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(ep_embedding)
            )
            episodes.append((sim, Episode(
                id=row[0], action=row[1], result=row[2], success=row[3],
                context=json.loads(row[4]), tags=json.loads(row[5]),
                timestamp=row[7], embedding=ep_embedding
            )))
        
        episodes.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in episodes[:k]]
    
    async def deduplicate(self, threshold: float = 0.95):
        """Cluster similar episodes, keep best"""
        # Get all episodes
        all_eps = await self.recall("", k=10000)
        if len(all_eps) < 2:
            return
        
        # Simple clustering by embedding similarity
        clusters = []
        for ep in all_eps:
            placed = False
            for cluster in clusters:
                if np.dot(ep.embedding, cluster[0].embedding) > threshold:
                    cluster.append(ep)
                    placed = True
                    break
            if not placed:
                clusters.append([ep])
        
        # Keep best from each cluster (successful, recent)
        to_keep = []
        for cluster in clusters:
            best = max(cluster, key=lambda e: (e.success, e.timestamp))
            to_keep.append(best.id)
        
        # Delete others
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ",".join("?" * (len(all_eps) - len(to_keep)))
            conn.execute(f"DELETE FROM episodes WHERE id NOT IN ({placeholders})", to_keep)
```

## 4. Project Memory (Active Context)

```python
# backend/app/memory/project.py
import json
import os
from watchfiles import watch
from dataclasses import dataclass, asdict
from typing import Dict, List, Set

@dataclass
class ProjectContext:
    name: str
    path: str
    files: Dict[str, dict]  # path -> {hash, size, mtime, summary}
    todos: List[dict]
    specs: List[str]
    last_updated: float

class ProjectMemory:
    def __init__(self, watch_paths: List[str], marker_files: List[str]):
        self.watch_paths = [os.path.expanduser(p) for p in watch_paths]
        self.marker_files = marker_files
        self.projects: Dict[str, ProjectContext] = {}
        self._load_projects()
    
    def _load_projects(self):
        for watch_path in self.watch_paths:
            for root, dirs, files in os.walk(watch_path):
                # Check for marker files
                if any(m in files for m in self.marker_files):
                    rel_path = os.path.relpath(root, watch_path)
                    self.projects[rel_path] = self._scan_project(root)
    
    def _scan_project(self, path: str) -> ProjectContext:
        files = {}
        for root, _, filenames in os.walk(path):
            for f in filenames:
                if self._should_index(f):
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, path)
                    stat = os.stat(full)
                    with open(full, 'r', errors='ignore') as fp:
                        content = fp.read(5000)  # First 5KB for summary
                    files[rel] = {
                        "hash": hash(content),
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                        "summary": self._summarize(content, f)
                    }
        return ProjectContext(
            name=os.path.basename(path),
            path=path,
            files=files,
            todos=[],
            specs=[],
            last_updated=time.time()
        )
    
    def _should_index(self, filename: str) -> bool:
        ext = os.path.splitext(filename)[1]
        return ext in {'.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.rs', '.go', '.java', '.cpp', '.c', '.h'}
    
    def _summarize(self, content: str, filename: str) -> str:
        # Quick summary: first few lines + key definitions
        lines = content.split('\n')[:20]
        return '\n'.join(lines)
    
    async def start_watching(self):
        """Start file watcher for real-time updates"""
        async for changes in watch(*self.watch_paths):
            for change_type, path in changes:
                await self._handle_change(change_type, path)
    
    async def _handle_change(self, change_type: str, path: str):
        # Find which project
        for project in self.projects.values():
            if path.startswith(project.path):
                rel = os.path.relpath(path, project.path)
                if change_type == "deleted":
                    project.files.pop(rel, None)
                elif self._should_index(os.path.basename(path)):
                    # Re-read and update
                    with open(path, 'r', errors='ignore') as f:
                        content = f.read()
                    stat = os.stat(path)
                    project.files[rel] = {
                        "hash": hash(content),
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                        "summary": self._summarize(content, path)
                    }
                project.last_updated = time.time()
                self._save_project(project)
                break
    
    def get_context(self, project_name: str, max_files: int = 20) -> str:
        """Get formatted context for agent"""
        project = self.projects.get(project_name)
        if not project:
            return ""
        
        # Sort by recent modification
        sorted_files = sorted(project.files.items(), key=lambda x: x[1]["mtime"], reverse=True)
        
        context = f"# Project: {project.name}\n\n"
        for rel, info in sorted_files[:max_files]:
            context += f"## {rel}\n{info['summary']}\n\n"
        
        if project.todos:
            context += "## TODOs\n"
            for todo in project.todos:
                context += f"- {todo}\n"
        
        return context
```

## RAG Indexer (Document Retrieval)

```python
# backend/app/rag/indexer.py
class RAGIndexer:
    def __init__(self, long_term: LongTermMemory, project_memory: ProjectMemory):
        self.long_term = long_term
        self.project_memory = project_memory
    
    async def index_file(self, path: str, project: str = None):
        """Index a single file"""
        with open(path, 'r', errors='ignore') as f:
            content = f.read()
        
        # Chunk into 512-token pieces
        chunks = self._chunk_text(content, max_tokens=512)
        
        for i, chunk in enumerate(chunks):
            tags = [project] if project else []
            tags.append(os.path.splitext(path)[1][1:])  # extension as tag
            await self.long_term.store(chunk, tags=tags, source="file")
    
    async def index_project(self, project_name: str):
        """Index entire project"""
        project = self.project_memory.projects.get(project_name)
        if not project:
            return
        
        for rel_path, info in project.files.items():
            full_path = os.path.join(project.path, rel_path)
            await self.index_file(full_path, project_name)
    
    def _chunk_text(self, text: str, max_tokens: int = 512) -> List[str]:
        """Fixed-size chunking (512 tokens)"""
        words = text.split()
        chunks = []
        current = []
        current_tokens = 0
        
        for word in words:
            word_tokens = len(word) / 4  # Rough estimate
            if current_tokens + word_tokens > max_tokens:
                chunks.append(' '.join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens
        
        if current:
            chunks.append(' '.join(current))
        
        return chunks
    
    async def search(self, user_id: str, query: str, k: int = 5) -> List[dict]:
        """Hybrid search: FAISS + BM25"""
        # Vector search
        vector_results = await self.long_term.search(query, k=k*2)
        
        # BM25 keyword search (on SQLite FTS)
        keyword_results = await self._bm25_search(query, k=k*2)
        
        # Combine and rerank
        combined = self._merge_results(vector_results, keyword_results)
        return combined[:k]
    
    async def _bm25_search(self, query: str, k: int) -> List[dict]:
        # SQLite FTS5 on memory metadata
        pass
    
    def _merge_results(self, vector: List[dict], keyword: List[dict]) -> List[dict]:
        # Reciprocal rank fusion
        scores = {}
        for i, r in enumerate(vector):
            scores[r["id"]] = scores.get(r["id"], 0) + 1 / (i + 1 + 60)
        for i, r in enumerate(keyword):
            scores[r["id"]] = scores.get(r["id"], 0) + 1 / (i + 1 + 60)
        
        # Sort by combined score
        merged = sorted(vector + keyword, key=lambda r: scores.get(r["id"], 0), reverse=True)
        # Deduplicate
        seen = set()
        unique = []
        for r in merged:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique.append(r)
        return unique
```

## Cross-File References (Code Graph)

```python
# backend/app/rag/cross_ref.py
import ast
import re

class CrossReferenceExtractor:
    def __init__(self):
        self.imports = {}  # file -> set(imports)
        self.symbols = {}  # symbol -> file
    
    def extract_python(self, path: str, content: str) -> dict:
        """Extract imports, classes, functions from Python"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"imports": [], "symbols": []}
        
        imports = []
        symbols = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append({
                    "name": node.name,
                    "type": "class" if isinstance(node, ast.ClassDef) else "function",
                    "line": node.lineno
                })
        
        return {"imports": imports, "symbols": symbols}
    
    def extract_javascript(self, path: str, content: str) -> dict:
        """Extract imports/exports from JS/TS"""
        imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
        imports += re.findall(r'require\([\'"]([^\'"]+)[\'"]\)', content)
        
        exports = re.findall(r'export\s+(?:class|function|const|let|var)\s+(\w+)', content)
        
        return {"imports": imports, "symbols": [{"name": e, "type": "export"} for e in exports]}
```

## Hybrid Search (FAISS + BM25)

```python
# Combined in RAGIndexer.search()
async def search(self, user_id: str, query: str, k: int = 5) -> List[dict]:
    # 1. Vector search (semantic)
    vector_results = await self.long_term.search(query, k=k*2)
    
    # 2. BM25 search (keyword/exact)
    keyword_results = await self._bm25_search(query, k=k*2)
    
    # 3. Cross-reference boost
    for r in vector_results:
        if "symbols" in r.get("tags", []):
            r["score"] *= 1.2  # Boost code symbols
    
    # 4. Reciprocal Rank Fusion
    fused = self._rrf(vector_results, keyword_results)
    
    return fused[:k]

def _rrf(self, *result_lists, k: int = 60) -> List[dict]:
    scores = {}
    for results in result_lists:
        for rank, r in enumerate(results):
            scores[r["id"]] = scores.get(r["id"], 0) + 1 / (rank + 1 + k)
    
    # Get full entries
    all_entries = {r["id"]: r for results in result_lists for r in results}
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    
    return [all_entries[id] for id in sorted_ids]
```

## Memory Manager (Unified Interface)

```python
# backend/app/memory/manager.py
class MemoryManager:
    def __init__(self, config: MemoryConfig):
        embedder = SentenceTransformer(config.long_term.embedding_model)
        
        self.short_term = ShortTermMemory(
            max_turns=config.short_term.max_turns,
            dynamic=config.short_term.dynamic
        )
        self.long_term = LongTermMemory(
            config.long_term.index_path,
            embedder
        )
        self.episodic = EpisodicMemory(
            config.episodic.db_path,
            embedder
        )
        self.project = ProjectMemory(
            config.project.watch_paths,
            config.project.marker_files
        )
        self.rag = RAGIndexer(self.long_term, self.project)
    
    async def get_context(self, query: str, project: str = None) -> str:
        """Get combined context for agent"""
        parts = []
        
        # Short-term conversation
        recent = self.short_term.get(max_tokens=2000)
        if recent:
            parts.append("## Recent Conversation")
            for msg in recent[-10:]:
                parts.append(f"{msg.role}: {msg.content}")
        
        # Long-term relevant memories
        ltm_results = await self.long_term.search(query, k=5)
        if ltm_results:
            parts.append("\n## Relevant Memories")
            for r in ltm_results:
                parts.append(f"- {r['text'][:200]}")
        
        # Project context
        if project:
            proj_ctx = self.project.get_context(project)
            if proj_ctx:
                parts.append(f"\n## Project Context\n{proj_ctx}")
        
        # Episodic lessons
        episodes = await self.episodic.recall(query, k=3, success_only=True)
        if episodes:
            parts.append("\n## Lessons Learned")
            for ep in episodes:
                parts.append(f"- {ep.action} → {ep.result}")
        
        return "\n".join(parts)
```

## Session Persistence

```python
# backend/app/memory/sessions.py
import jsonlines

class SessionManager:
    def __init__(self, sessions_dir: str):
        self.sessions_dir = sessions_dir
        self.index_db = sqlite3.connect(f"{sessions_dir}/index.sqlite")
        self._init_index()
    
    def _init_index(self):
        self.index_db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                project TEXT,
                created_at REAL,
                updated_at REAL,
                message_count INTEGER
            )
        """)
    
    async def save_session(self, session_id: str, messages: List[Message], 
                           project: str = None, title: str = None):
        # Save messages as JSONL
        path = f"{self.sessions_dir}/session_{session_id}.jsonl"
        with jsonlines.open(path, 'w') as writer:
            for msg in messages:
                writer.write(asdict(msg))
        
        # Update index
        self.index_db.execute("""
            INSERT OR REPLACE INTO sessions (id, title, project, created_at, updated_at, message_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, title, project, time.time(), time.time(), len(messages)))
        self.index_db.commit()
    
    async def load_session(self, session_id: str) -> List[Message]:
        path = f"{self.sessions_dir}/session_{session_id}.jsonl"
        messages = []
        with jsonlines.open(path) as reader:
            for obj in reader:
                messages.append(Message(**obj))
        return messages
    
    async def export_markdown(self, session_id: str) -> str:
        """Export session as Markdown"""
        messages = await self.load_session(session_id)
        
        md = f"# Session {session_id}\n\n"
        for msg in messages:
            role = "🤖" if msg.role == "assistant" else "👤"
            md += f"## {role} {msg.role.title()}\n\n{msg.content}\n\n"
            
            if msg.metadata and msg.metadata.get("thoughts"):
                md += "### Thoughts\n"
                for t in msg.metadata["thoughts"]:
                    md += f"- {t}\n"
                md += "\n"
        
        return md
```

## Rebuild Triggers

| Trigger | Action |
|---------|--------|
| Session start | Full FAISS rebuild from all sources |
| File save (editor) | Debounced (2s) → incremental update |
| Manual (Space+r) | Full rebuild |
| Project switch | Rebuild project context only |

## Configuration

```toml
[memory]
short_term = { dynamic = true, max_turns = 50 }
long_term = { enabled = true, index_path = "~/.ele-agent/memory/faiss", embedding_model = "bge-small" }
episodic = { enabled = true, db_path = "~/.ele-agent/memory/episodic.db", retention = "forever", dedup = true }
project = { enabled = true, watch_paths = ["~/projects"], marker_files = ["pyproject.toml", "package.json", "Cargo.toml", "go.mod", ".git"] }
```