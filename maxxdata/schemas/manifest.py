"""Manifest schema for served datasets."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_manifest(
    *,
    agent: str,
    product: str,
    version: str,
    schema: str,
    row_count: int,
    files: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "agent": agent,
        "product": product,
        "version": version,
        "schema": schema,
        "row_count": row_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    if extra:
        manifest.update(extra)
    return manifest


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
