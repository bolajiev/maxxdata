"""Path helpers for pipeline data directories."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
INVENTORY_DIR = ROOT / "inventory"
SAMPLES_DIR = ROOT / "samples"
DATA_DIR = ROOT / "data"


def batch_dir(stage: str, agent: str, batch: str) -> Path:
    """Return path under data/<stage>/<agent>/<batch>."""
    return DATA_DIR / stage / agent / batch


def raw_dir(agent: str, batch: str) -> Path:
    return batch_dir("corpus/raw", agent, batch)


def process_dir(agent: str, batch: str) -> Path:
    return batch_dir("process", agent, batch)


def serve_bound_dir(agent: str, batch: str) -> Path:
    """Staging area before promote to serve/."""
    return batch_dir("serve-bound", agent, batch)


def serve_dir(agent: str, product: str, version: str) -> Path:
    """Final served dataset: data/serve/<agent>/<product>/<version>/."""
    return DATA_DIR / "serve" / agent / product / version


def approved_flag(agent: str, batch: str) -> Path:
    return process_dir(agent, batch) / "approved.flag"


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)
