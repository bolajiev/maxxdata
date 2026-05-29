"""Approve stage: human gate before label/promote."""

from __future__ import annotations

from datetime import datetime, timezone

from maxxdata.paths import approved_flag, process_dir


def run_approve(agent: str, batch: str, note: str = "") -> dict[str, str]:
    proc = process_dir(agent, batch)
    validated = proc / "validated.jsonl"
    if not validated.exists():
        raise FileNotFoundError(f"Run validate first. Missing: {validated}")

    flag = approved_flag(agent, batch)
    flag.write_text(
        f"approved_at={datetime.now(timezone.utc).isoformat()}\n"
        f"agent={agent}\n"
        f"batch={batch}\n"
        f"note={note}\n",
        encoding="utf-8",
    )
    return {"status": "approved", "flag": str(flag)}


def require_approved(agent: str, batch: str) -> None:
    flag = approved_flag(agent, batch)
    if not flag.exists():
        raise RuntimeError(
            f"Batch not approved. Run: python -m maxxdata approve --agent {agent} --batch {batch}"
        )
