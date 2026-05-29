"""Validate stage: schema checks on cleaned documents."""

from __future__ import annotations

import csv
import json

from maxxdata.io_utils import read_jsonl, write_jsonl
from maxxdata.paths import ensure_dirs, process_dir
from maxxdata.validators.rules import validate_document


def run_validate(agent: str, batch: str) -> dict[str, Any]:
    proc = process_dir(agent, batch)
    cleaned_path = proc / "cleaned.jsonl"
    if not cleaned_path.exists():
        raise FileNotFoundError(f"Run clean first. Missing: {cleaned_path}")

    ensure_dirs(proc)
    validated: list[dict] = []
    rejects: list[dict[str, str]] = []

    for doc in read_jsonl(cleaned_path):
        err = validate_document(doc, agent)
        if err:
            rejects.append(
                {
                    "doc_id": doc.get("doc_id", ""),
                    "reason": err,
                    "source_url": doc.get("source_url", ""),
                }
            )
        else:
            validated.append(doc)

    write_jsonl(proc / "validated.jsonl", validated)
    with (proc / "validation_rejects.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "reason", "source_url"])
        writer.writeheader()
        writer.writerows(rejects)

    meta = {
        "agent": agent,
        "batch": batch,
        "validated_count": len(validated),
        "reject_count": len(rejects),
    }
    (proc / "validate_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta
