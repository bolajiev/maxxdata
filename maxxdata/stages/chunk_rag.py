"""Chunk RAG stage: split validated docs into chunks (no LLM)."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pandas as pd

from maxxdata.config import agent_settings
from maxxdata.io_utils import read_jsonl
from maxxdata.paths import ensure_dirs, process_dir, serve_bound_dir
from maxxdata.schemas.manifest import build_manifest, write_manifest
from maxxdata.stages.approve import require_approved
from maxxdata.validators.rules import validate_chunk


def _chunk_text(
    text: str,
    chunk_size: int = 600,
    overlap: int = 100,
) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    i = 0
    while i < len(words):
        piece = " ".join(words[i : i + chunk_size])
        if len(piece.strip()) >= 50:
            chunks.append(piece)
        i += step
    return chunks


def run_chunk_rag(agent: str, batch: str) -> dict[str, Any]:
    require_approved(agent, batch)
    settings = agent_settings(agent)
    proc = process_dir(agent, batch)
    validated_path = proc / "validated.jsonl"
    if not validated_path.exists():
        raise FileNotFoundError(f"Missing: {validated_path}")

    chunk_size = settings.get("chunk_size", 600)
    overlap = settings.get("chunk_overlap", 100)

    rows: list[dict[str, Any]] = []
    for doc in read_jsonl(validated_path):
        text = doc["text"]
        for idx, chunk in enumerate(_chunk_text(text, chunk_size, overlap)):
            chunk_id = hashlib.sha256(
                f"{doc['doc_id']}:{idx}:{chunk[:80]}".encode()
            ).hexdigest()[:16]
            row = {
                "chunk_id": f"chk_{chunk_id}",
                "doc_id": doc["doc_id"],
                "agent": agent,
                "text": chunk,
                "chunk_index": idx,
                "source_url": doc.get("source_url", ""),
                "title": doc.get("title", ""),
                "lang": doc.get("lang", "unknown"),
            }
            err = validate_chunk(row, agent)
            if err:
                continue
            rows.append(row)

    bound = serve_bound_dir(agent, batch) / "rag"
    ensure_dirs(bound)
    df = pd.DataFrame(rows)
    parquet_path = bound / "chunks.parquet"
    df.to_parquet(parquet_path, index=False)

    sources = [
        {
            "doc_id": d["doc_id"],
            "source_url": d.get("source_url", ""),
            "title": d.get("title", ""),
        }
        for d in read_jsonl(validated_path)
    ]
    sources_path = bound / "sources.jsonl"
    with sources_path.open("w", encoding="utf-8") as f:
        for s in sources:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    manifest = build_manifest(
        agent=agent,
        product="rag",
        version=f"bound-{batch}",
        schema="chunk_v1",
        row_count=len(rows),
        files=["chunks.parquet", "sources.jsonl"],
        extra={"batch": batch, "chunk_size": chunk_size},
    )
    write_manifest(bound / "manifest.json", manifest)

    return {"chunk_count": len(rows), "path": str(bound)}
