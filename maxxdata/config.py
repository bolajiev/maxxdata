"""Load YAML configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from maxxdata.paths import CONFIG_DIR

VALID_AGENTS = frozenset({"coding", "research"})


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_agents() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "agents.yaml")


def load_sources(agent: str) -> dict[str, Any]:
    if agent not in VALID_AGENTS:
        raise ValueError(f"Unknown agent: {agent}. Use: {', '.join(sorted(VALID_AGENTS))}")
    path = CONFIG_DIR / f"sources.{agent}.yaml"
    return load_yaml(path)


def agent_settings(agent: str) -> dict[str, Any]:
    agents = load_agents()
    settings = agents.get("agents", {}).get(agent)
    if not settings:
        raise ValueError(f"No settings for agent '{agent}' in config/agents.yaml")
    return settings
