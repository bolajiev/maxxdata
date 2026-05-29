"""Promote stage: copy serve-bound artifacts to versioned serve/."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from maxxdata.io_utils import append_catalog, read_jsonl
from maxxdata.paths import INVENTORY_DIR, ensure_dirs, serve_bound_dir, serve_dir
from maxxdata.schemas.manifest import build_manifest, write_manifest
from maxxdata.stages.approve import require_approved


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    ensure_dirs(dst)
    for item in src.iterdir():
        dest = dst / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)


def run_promote(agent: str, batch: str, version: str) -> dict[str, str]:
    require_approved(agent, batch)
    bound = serve_bound_dir(agent, batch)
    results: dict[str, str] = {}

    for product in ("rag", "ft"):
        src = bound / product
        if not src.exists():
            continue
        dst = serve_dir(agent, product, version)
        if dst.exists():
            shutil.rmtree(dst)
        _copy_tree(src, dst)

        row_count = 0
        files: list[str] = []
        if product == "rag":
            parquet = dst / "chunks.parquet"
            if parquet.exists():
                import pandas as pd

                row_count = len(pd.read_parquet(parquet))
                files = [f.name for f in dst.iterdir() if f.is_file()]
        else:
            for p in sorted(src.glob("*_draft.jsonl")):
                final = dst / p.name.replace("_draft", "")
                if final.exists():
                    final.unlink()
                shutil.copy2(p, final)
                files.append(final.name)
                row_count += sum(1 for _ in read_jsonl(final))

        manifest = build_manifest(
            agent=agent,
            product=product,
            version=version,
            schema="chunk_v1" if product == "rag" else "ft_v1",
            row_count=row_count,
            files=files or [f.name for f in dst.iterdir() if f.is_file()],
            extra={"batch": batch, "promoted_from": str(bound)},
        )
        write_manifest(dst / "manifest.json", manifest)
        results[product] = str(dst)

        append_catalog(
            INVENTORY_DIR / "catalog.csv",
            {
                "id": f"{agent}-{product}-{version}",
                "agent": agent,
                "product": product,
                "version": version,
                "batch": batch,
                "stage": "served",
                "row_count": str(row_count),
                "source_summary": batch,
                "quality_score": "",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "notes": "promoted",
            },
        )

    return results
