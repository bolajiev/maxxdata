"""Short-term session memory."""

from __future__ import annotations

from typing import Any


class SessionMemory:
    def __init__(self, max_turns: int = 20) -> None:
        self.max_turns = max_turns
        self.messages: list[dict[str, Any]] = []

    def add(self, message: dict[str, Any]) -> None:
        self.messages.append(message)
        # Rough trim: keep system + last N non-system
        system = [m for m in self.messages if m.get("role") == "system"]
        rest = [m for m in self.messages if m.get("role") != "system"]
        if len(rest) > self.max_turns * 3:
            rest = rest[-(self.max_turns * 3) :]
        self.messages = system[:1] + rest

    def get(self) -> list[dict[str, Any]]:
        return list(self.messages)

    def set_system(self, content: str) -> None:
        self.messages = [m for m in self.messages if m.get("role") != "system"]
        self.messages.insert(0, {"role": "system", "content": content})
