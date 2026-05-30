"""DeepSeek LLM client (OpenAI-compatible, tools supported)."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from maxx_agent.paths import PLATFORM_ROOT

load_dotenv(PLATFORM_ROOT / ".env")


def get_client() -> OpenAI:
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("Set DEEPSEEK_API_KEY in .env at repo root")
    return OpenAI(api_key=key, base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))


def get_model() -> str:
    return os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    temperature: float = 0.4,
) -> Any:
    client = get_client()
    kwargs: dict[str, Any] = {
        "model": get_model(),
        "messages": messages,
        "temperature": temperature,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    return client.chat.completions.create(**kwargs)


def message_to_dict(msg: Any) -> dict[str, Any]:
    """Convert API message to serializable dict for memory."""
    d: dict[str, Any] = {"role": msg.role, "content": msg.content}
    if msg.tool_calls:
        d["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ]
    return d


def parse_tool_args(arguments: str) -> dict[str, Any]:
    try:
        return json.loads(arguments) if arguments else {}
    except json.JSONDecodeError:
        return {"raw": arguments}
