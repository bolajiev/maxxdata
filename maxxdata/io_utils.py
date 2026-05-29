"""JSONL and catalog I/O."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterator


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return iter(())
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(rows)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


CATALOG_FIELDS = [
    "id",
    "agent",
    "product",
    "version",
    "batch",
    "stage",
    "row_count",
    "source_summary",
    "quality_score",
    "created_at",
    "notes",
]


def append_catalog(catalog_path: Path, row: dict[str, str]) -> None:
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    exists = catalog_path.exists()
    with catalog_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CATALOG_FIELDS, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in CATALOG_FIELDS})
