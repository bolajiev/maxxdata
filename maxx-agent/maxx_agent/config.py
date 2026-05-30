"""Load agent YAML config."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from maxx_agent.paths import CONFIG_DIR

ALIASES = {"coder": "coding", "coding": "coding", "research": "research", "researcher": "research"}


def load_agent_config(agent: str) -> dict[str, Any]:
    key = ALIASES.get(agent, agent)
    path = CONFIG_DIR / f"{key}.yaml"
    if not path.exists():
        path = CONFIG_DIR / "coder.yaml"
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg["agent_key"] = key
    return cfg
