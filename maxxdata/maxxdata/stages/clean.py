"""Clean stage: rules-based filtering and deduplication."""

from __future__ import annotations

import csv
import json
from typing import Any

from simhash import Simhash

from maxxdata.cleaners.rules import clean_document
from maxxdata.config import agent_settings
from maxxdata.io_utils import read_jsonl, write_jsonl
from maxxdata.paths import ensure_dirs, process_dir, raw_dir


def run_clean(agent: str, batch: str) -> dict[str, Any]:
    settings = agent_settings(agent)
    raw_path = raw_dir(agent, batch) / "raw.jsonl"
    if not raw_path.exists():
        raise FileNotFoundError(f"Run ingest first. Missing: {raw_path}")

    out = process_dir(agent, batch)
    ensure_dirs(out)

    seen_hashes: set[str] = set()
    seen_simhashes: list[Simhash] = []
    near_dup_threshold = settings.get("near_dup_threshold", 3)
    cleaned: list[dict[str, Any]] = []
    rejects: list[dict[str, str]] = []

    min_chars = settings.get("min_chars", 200)
    allowed_langs = settings.get("allowed_langs", ["en"])
    max_boilerplate = settings.get("max_boilerplate", 2)

    in_count = 0
    for doc in read_jsonl(raw_path):
        in_count += 1
        result, reason = clean_document(
            doc,
            min_chars=min_chars,
            allowed_langs=allowed_langs,
            max_boilerplate=max_boilerplate,
        )
        if result is None:
            rejects.append(
                {
                    "doc_id": doc.get("doc_id", ""),
                    "reason": reason or "unknown",
                    "source_url": doc.get("source_url", ""),
                }
            )
            continue
        h = result["content_hash"]
        if h in seen_hashes:
            rejects.append(
                {
                    "doc_id": result.get("doc_id", ""),
                    "reason": "duplicate_exact",
                    "source_url": result.get("source_url", ""),
                }
            )
            continue

        words = result["text"].split()
        sh = Simhash(words) if len(words) >= 20 else None
        if sh is not None:
            if any(sh.distance(prev) <= near_dup_threshold for prev in seen_simhashes):
                rejects.append(
                    {
                        "doc_id": result.get("doc_id", ""),
                        "reason": "duplicate_near",
                        "source_url": result.get("source_url", ""),
                    }
                )
                continue
            seen_simhashes.append(sh)

        seen_hashes.add(h)
        cleaned.append(result)

    write_jsonl(out / "cleaned.jsonl", cleaned)
    reject_path = out / "rejects.csv"
    with reject_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "reason", "source_url"])
        writer.writeheader()
        writer.writerows(rejects)

    meta = {
        "agent": agent,
        "batch": batch,
        "in_count": in_count,
        "out_count": len(cleaned),
        "reject_count": len(rejects),
    }
    (out / "clean_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta
