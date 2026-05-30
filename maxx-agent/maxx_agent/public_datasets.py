"""Public Hugging Face datasets for training (no scraping)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from maxx_agent.paths import PUBLIC_DATA_DIR

# Curated list — expand as needed. See docs/PUBLIC_DATASETS.md
CATALOG: list[dict[str, str]] = [
    {
        "id": "glaive-function-calling-v2",
        "hf": "glaiveai/glaive-function-calling-v2",
        "use": "Tool / function calling traces",
    },
    {
        "id": "openassistant",
        "hf": "OpenAssistant/oasst1",
        "use": "Multi-turn conversations (filter English)",
    },
    {
        "id": "squad",
        "hf": "rajpurkar/squad",
        "use": "Reading comprehension Q&A",
    },
    {
        "id": "code-feedback",
        "hf": "HuggingFaceH4/Code-Feedback",
        "use": "Code preference / feedback",
    },
    {
        "id": "fineweb-edu-sample",
        "hf": "HuggingFaceFW/fineweb-edu",
        "use": "General text (sample only — huge full set)",
    },
]


def list_catalog() -> list[dict[str, str]]:
    return CATALOG


def export_hf_dataset(
    hf_name: str,
    out_path: Path,
    *,
    split: str = "train",
    limit: int = 500,
    message_columns: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """
    Download a slice from Hugging Face and save as JSONL for training.
    Requires: pip install datasets huggingface_hub
    """
    from datasets import load_dataset

    PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ds = load_dataset(hf_name, split=split, streaming=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for row in ds:
            if count >= limit:
                break
            record = _normalize_row(dict(row), message_columns)
            if record:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1

    return {"hf": hf_name, "out": str(out_path), "rows": count}


def _normalize_row(row: dict[str, Any], message_columns: tuple[str, str] | None) -> dict[str, Any] | None:
    """Best-effort convert HF row to messages format."""
    if "messages" in row and isinstance(row["messages"], list):
        return {"messages": row["messages"], "source": "hf"}

    if "conversation" in row:
        return {"messages": row["conversation"], "source": "hf"}

    if message_columns:
        u, a = message_columns
        if u in row and a in row:
            return {
                "messages": [
                    {"role": "user", "content": str(row[u])[:4000]},
                    {"role": "assistant", "content": str(row[a])[:4000]},
                ],
                "source": "hf",
            }

    if "question" in row and "answer" in row:
        return {
            "messages": [
                {"role": "user", "content": str(row["question"])},
                {"role": "assistant", "content": str(row["answer"])},
            ],
            "source": "hf",
        }

    if "instruction" in row and "output" in row:
        return {
            "messages": [
                {"role": "user", "content": str(row["instruction"])},
                {"role": "assistant", "content": str(row["output"])},
            ],
            "source": "hf",
        }

    # Glaive-style
    if "system" in row and "chat" in row:
        return {"system": row["system"], "chat": row["chat"], "source": "hf-glaive"}

    return None
