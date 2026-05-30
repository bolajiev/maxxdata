"""Paths for maxx-agent."""

from __future__ import annotations

from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
PLATFORM_ROOT = AGENT_ROOT.parent
CONFIG_DIR = AGENT_ROOT / "config"
EVAL_DIR = AGENT_ROOT / "eval"
DATA_DIR = AGENT_ROOT / "data"
PUBLIC_DATA_DIR = DATA_DIR / "public"

# Optional: RAG from maxxdata pipeline output
MAXXDATA_SERVE = PLATFORM_ROOT / "maxxdata" / "data" / "serve"


def rag_parquet_path(agent: str, version: str | None = None) -> Path | None:
    """Find latest or specific RAG parquet from maxxdata serve/."""
    rag_root = MAXXDATA_SERVE / agent / "rag"
    if not rag_root.exists():
        return None
    if version:
        p = rag_root / version / "chunks.parquet"
        return p if p.exists() else None
    versions = sorted([d for d in rag_root.iterdir() if d.is_dir()], reverse=True)
    for ver in versions:
        p = ver / "chunks.parquet"
        if p.exists():
            return p
    return None
