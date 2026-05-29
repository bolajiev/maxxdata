"""Validation rules before promotion."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse


def validate_document(doc: dict[str, Any], agent: str) -> str | None:
    """Return error string or None if valid."""
    if not doc.get("text") or len(doc["text"]) < 100:
        return "text_too_short"
    if not doc.get("doc_id"):
        return "missing_doc_id"
    if agent == "research" and not doc.get("source_url"):
        return "missing_source_url"
    if doc.get("source_url"):
        parsed = urlparse(doc["source_url"])
        if parsed.scheme not in ("http", "https", "file"):
            return "invalid_source_url"
    return None


def validate_chunk(chunk: dict[str, Any], agent: str) -> str | None:
    if not chunk.get("chunk_id") or not chunk.get("text"):
        return "missing_chunk_fields"
    if len(chunk["text"]) < 50:
        return "chunk_too_short"
    if agent == "research" and not chunk.get("source_url"):
        return "missing_source_url"
    return None


def validate_instruction_row(row: dict[str, Any]) -> str | None:
    """Script-check instruction-following rows."""
    constraints = row.get("constraints") or []
    messages = row.get("messages") or []
    if len(messages) < 2:
        return "messages_too_short"

    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    if not assistant_msgs:
        return "no_assistant_message"
    content = assistant_msgs[-1].get("content") or ""

    for c in constraints:
        if c == "no_code" and re.search(r"```|`[^`]+`", content):
            return "constraint_no_code_violated"
        if c.startswith("max_bullets:"):
            try:
                n = int(c.split(":")[1])
            except ValueError:
                continue
            bullets = [ln for ln in content.splitlines() if ln.strip().startswith(("•", "-", "*"))]
            if len(bullets) > n:
                return f"constraint_max_bullets_{n}_violated"
        if c == "json_only":
            try:
                json.loads(content.strip())
            except json.JSONDecodeError:
                return "constraint_json_only_violated"
    return None


def validate_tool_calling_row(row: dict[str, Any]) -> str | None:
    messages = row.get("messages") or []
    if len(messages) < 2:
        return "messages_too_short"
    has_tool = any(m.get("role") == "tool" for m in messages) or any(
        m.get("tool_calls") for m in messages if m.get("role") == "assistant"
    )
    if not has_tool:
        return "missing_tool_call_or_tool_response"
    return None


def validate_trajectory_row(row: dict[str, Any]) -> str | None:
    messages = row.get("messages") or []
    if len(messages) < 3:
        return "trajectory_too_short"
    roles = [m.get("role") for m in messages]
    if "user" not in roles or "assistant" not in roles:
        return "missing_user_or_assistant"
    return None


def validate_multi_agent_row(row: dict[str, Any]) -> str | None:
    messages = row.get("messages") or []
    if len(messages) < 3:
        return "multi_agent_too_short"
    names = {m.get("name") for m in messages if m.get("role") == "assistant" and m.get("name")}
    if len(names) < 2 and len(row.get("agents_involved") or []) < 2:
        return "need_multiple_agent_identities"
    return None
