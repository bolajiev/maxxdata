"""Simple RAG over maxxdata chunks.parquet (keyword rank v1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from maxx_agent.paths import rag_parquet_path


class RagRetriever:
    def __init__(self, agent: str, version: str | None = None) -> None:
        path = rag_parquet_path(agent, version)
        if path is None:
            self.df: pd.DataFrame | None = None
            self.path = None
        else:
            self.df = pd.read_parquet(path)
            self.path = path

    @property
    def available(self) -> bool:
        return self.df is not None and len(self.df) > 0

    def _score(self, query: str, text: str) -> int:
        q = set(re.findall(r"\w+", query.lower()))
        t = re.findall(r"\w+", text.lower())
        return sum(1 for w in q if w in t)

    def search(self, query: str, k: int = 6) -> list[dict[str, Any]]:
        if not self.available or self.df is None:
            return []
        scores = self.df["text"].apply(lambda t: self._score(query, str(t)))
        top = self.df.assign(_score=scores).nlargest(k, "_score")
        out: list[dict[str, Any]] = []
        for _, row in top.iterrows():
            if row["_score"] <= 0:
                continue
            out.append(
                {
                    "chunk_id": row.get("chunk_id", ""),
                    "text": row["text"],
                    "source_url": row.get("source_url", ""),
                    "title": row.get("title", ""),
                }
            )
        return out[:k]

    def format_context(self, chunks: list[dict[str, Any]]) -> str:
        if not chunks:
            return "(No documents retrieved. Say you lack source context.)"
        parts = []
        for i, c in enumerate(chunks, 1):
            parts.append(
                f"[{i}] source={c.get('source_url', 'unknown')} title={c.get('title', '')}\n{c['text'][:1200]}"
            )
        return "\n\n".join(parts)
