"""Load seed FT files (instruction-following, etc.) without LLM."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from maxxdata.io_utils import read_jsonl, write_jsonl
from maxxdata.paths import SAMPLES_DIR, ensure_dirs, serve_bound_dir
from maxxdata.stages.approve import require_approved
from maxxdata.validators.rules import validate_instruction_row

SEED_MAP = {
    "instructions": "instructions.seed.jsonl",
}


def _seed_path(agent: str, ft_type: str) -> Path:
    filename = SEED_MAP.get(ft_type, f"{ft_type}.seed.jsonl")
    # instructions -> coding_instructions.seed.jsonl
    if ft_type == "instructions":
        filename = f"{agent}_instructions.seed.jsonl"
    path = SAMPLES_DIR / "ft" / filename
    if not path.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")
    return path


def run_seed_ft(agent: str, batch: str, types: list[str] | None = None) -> dict[str, int]:
    require_approved(agent, batch)
    types = types or ["instructions"]
    bound = serve_bound_dir(agent, batch) / "ft"
    ensure_dirs(bound)
    counts: dict[str, int] = {}

    for ft_type in types:
        if ft_type != "instructions":
            continue
        src = _seed_path(agent, ft_type)
        rows = list(read_jsonl(src))
        valid = []
        for row in rows:
            row.setdefault("agent", agent)
            row.setdefault("task_type", "instruction_following")
            if validate_instruction_row(row) is None:
                valid.append(row)
        out = bound / "instructions_draft.jsonl"
        counts["instructions"] = write_jsonl(out, valid)

    meta_path = bound / "seed_meta.json"
    meta_path.write_text(json.dumps({"agent": agent, "batch": batch, "counts": counts}, indent=2), encoding="utf-8")
    return counts
