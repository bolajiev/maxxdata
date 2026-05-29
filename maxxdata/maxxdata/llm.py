"""DeepSeek API client (OpenAI-compatible)."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_client() -> OpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY not set. Copy .env.example to .env and add your key."
        )
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    return OpenAI(api_key=api_key, base_url=base_url)


def get_model() -> str:
    return os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")


def chat_json(system: str, user: str, temperature: float = 0.3) -> dict[str, Any]:
    """Request JSON object response from the model."""
    client = get_client()
    model = get_model()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def chat_text(system: str, user: str, temperature: float = 0.5) -> str:
    client = get_client()
    model = get_model()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return (response.choices[0].message.content or "").strip()


def extract_json_array(text: str) -> list[dict[str, Any]]:
    """Parse JSON array from model output (with or without markdown fence)."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    if text.startswith("["):
        return json.loads(text)
    parsed = json.loads(text)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict) and "items" in parsed:
        return parsed["items"]
    return [parsed]
