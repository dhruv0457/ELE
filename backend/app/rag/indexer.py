"""FAISS RAG Indexer with BM25 Hybrid Search"""
import os
import json
import pickle
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from app.config.settings import settings
from app.rag.embedder import get_embedder, FALLBACK_DIM


class RAGIndexer:
    def __init__(self):
        data_dir = os.environ.get("DATA_DIR")
        if data_dir:
            base = Path(os.path.expanduser(data_dir)) / "memory" / "faiss"
        else:
            base = Path(os.path.expanduser(settings.memory.long_term.index_path))
        self.index_path = base
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.embedding_model_name = settings.memory.long_term.embedding_model
        self.embedder = None
        self.dimension = FALLBACK_DIM

        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []

        self.bm25: Optional[BM25Okapi] = None
        self.bm25_corpus: List[List[str]] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Async initialization: load embedder, FAISS index, metadata and BM25."""
        if self._initialized:
            return
        self.embedder = get_embedder(self.embedding_model_name, dim=FALLBACK_DIM)
        try:
            self.dimension = self.embedder.get_sentence_embedding_dimension()
        except Exception:
            self.dimension = FALLBACK_DIM

        self.index = self._load_faiss_index()
        self.metadata = self._load_metadata()
        self._build_bm25()
        self._initialized = True

    def _ensure_ready(self) -> None:
        if not self._initialized:
            # Synchronous fallback so non-async callers don't crash.
            asyncio.get_event_loop().run_until_complete(self.initialize())

    def _load_faiss_index(self) -> faiss.Index:
        index_file = self.index_path / "index.faiss"
        if index_file.exists():
            return faiss.read_index(str(index_file))
        return faiss.IndexFlatL2(self.dimension)

    def _load_metadata(self) -> List[Dict[str, Any]]:
        meta_file = self.index_path / "index.pkl"
        if meta_file.exists():
            with open(meta_file, "rb") as f:
                return pickle.load(f)
        return []

    def _save(self):
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "index.pkl", "wb") as f:
            pickle.dump(self.metadata, f)

    def _build_bm25(self):
        """Build BM25 index from metadata"""
        self.bm25_corpus = [entry["text"].split() for entry in self.metadata]
        if self.bm25_corpus:
            self.bm25 = BM25Okapi(self.bm25_corpus)

    def _chunk_text(self, text: str, max_tokens: int = 512) -> List[str]:
        """Fixed-size chunking"""
        words = text.split()
        chunks = []
        current = []
        current_len = 0

        for word in words:
            word_len = len(word) / 4  # Rough token estimate
            if current_len + word_len > max_tokens:
                chunks.append(' '.join(current))
                current = [word]
                current_len = word_len
            else:
                current.append(word)
                current_len += word_len

        if current:
            chunks.append(' '.join(current))
        return chunks

    async def index_text(self, text: str, tags: List[str] = None, source: str = "user", project: str = None):
        """Index a text document"""
        await self.initialize()
        chunks = self._chunk_text(text)
        for chunk in chunks:
            await self._add_chunk(chunk, tags, source, project)

    async def index_file(self, file_path: str, project: str = None):
        """Index a single file"""
        await self.initialize()
        path = Path(os.path.expanduser(file_path))
        if not path.exists():
            return

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        ext = path.suffix[1:] if path.suffix else "txt"
        tags = [ext]
        if project:
            tags.append(f"project:{project}")

        await self.index_text(content, tags=tags, source=str(path), project=project)

    async def _add_chunk(self, text: str, tags: List[str], source: str, project: str):
        embedding = self.embedder.encode([text])[0].astype(np.float32)

        entry_id = len(self.metadata)
        self.index.add(np.array([embedding]))

        self.metadata.append({
            "id": entry_id,
            "text": text,
            "content": text,
            "tags": tags,
            "source": source,
            "project": project,
            "hash": hashlib.md5(text.encode()).hexdigest(),
            "timestamp": asyncio.get_event_loop().time(),
        })

        # Update BM25
        self.bm25_corpus.append(text.split())
        if self.bm25_corpus:
            self.bm25 = BM25Okapi(self.bm25_corpus)

        self._save()

    async def search(self, user_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Hybrid search: FAISS + BM25 with RRF"""
        await self.initialize()
        if not self.metadata:
            return []

        # Vector search
        query_embedding = self.embedder.encode([query])[0].astype(np.float32)
        vector_distances, vector_indices = self.index.search(
            np.array([query_embedding]),
            min(k * 3, len(self.metadata))
        )

        vector_results = []
        for dist, idx in zip(vector_distances[0], vector_indices[0]):
            if idx < len(self.metadata) and idx >= 0:
                entry = self.metadata[idx].copy()
                entry["vector_score"] = float(1 / (1 + dist))
                vector_results.append(entry)

        # BM25 search
        keyword_results = []
        if self.bm25:
            query_tokens = query.split()
            bm25_scores = self.bm25.get_scores(query_tokens)
            top_indices = np.argsort(bm25_scores)[::-1][:k * 3]
            for idx in top_indices:
                if idx < len(self.metadata) and bm25_scores[idx] > 0:
                    entry = self.metadata[idx].copy()
                    entry["bm25_score"] = float(bm25_scores[idx])
                    keyword_results.append(entry)

        # Reciprocal Rank Fusion
        fused = self._rrf(vector_results, keyword_results, k=60)
        return fused[:k]

    def _rrf(self, *result_lists, k: int = 60) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion"""
        scores = {}
        all_entries = {}

        for results in result_lists:
            for rank, entry in enumerate(results):
                entry_id = entry["id"]
                all_entries[entry_id] = entry
                scores[entry_id] = scores.get(entry_id, 0) + 1 / (rank + 1 + k)

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        return [all_entries[eid] for eid in sorted_ids]

    async def remove_file(self, file_path: str) -> None:
        """Remove all indexed chunks belonging to a file."""
        await self.initialize()
        path_str = str(Path(os.path.expanduser(file_path)))
        before = len(self.metadata)

        kept_metadata = [m for m in self.metadata if m.get("source") != path_str]
        removed = before - len(kept_metadata)
        if removed == 0:
            return

        self.metadata = kept_metadata
        self._rebuild_index()
        self._save()

    def _rebuild_index(self) -> None:
        """Rebuild the FAISS and BM25 indexes from current metadata."""
        self.index = faiss.IndexFlatL2(self.dimension)
        if self.metadata:
            texts = [m["text"] for m in self.metadata]
            embeddings = self.embedder.encode(texts).astype(np.float32)
            self.index.add(embeddings)
        self.bm25_corpus = [m["text"].split() for m in self.metadata]
        self.bm25 = BM25Okapi(self.bm25_corpus) if self.bm25_corpus else None

    async def rebuild(self):
        """Full rebuild of all indexes"""
        await self.initialize()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self.bm25_corpus = []
        self.bm25 = None
        self._save()
