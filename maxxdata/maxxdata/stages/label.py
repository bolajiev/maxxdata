"""Label stage: DeepSeek generates FT datasets (separate files per type)."""

from __future__ import annotations

import json
from typing import Any

from maxxdata.config import agent_settings
from maxxdata.io_utils import read_jsonl, write_jsonl
from maxxdata.llm import chat_json, chat_text, extract_json_array
from maxxdata.paths import ensure_dirs, process_dir, serve_bound_dir
from maxxdata.schemas.ft_types import FT_DRAFT_FILES, LABEL_TYPE_ALIASES
from maxxdata.stages.approve import require_approved
from maxxdata.stages.label_agentic import (
    label_multi_agent,
    label_tool_calling,
    label_trajectory,
)
from maxxdata.validators.rules import (
    validate_instruction_row,
    validate_multi_agent_row,
    validate_tool_calling_row,
    validate_trajectory_row,
)

SYSTEM_CODING = """You create training data for a coding assistant.
Output valid JSON only. Ground answers in the provided document text.
Do not invent APIs or facts not present in the source."""

SYSTEM_RESEARCH = """You create training data for a research assistant.
Answers must cite the source document. If evidence is insufficient, use "unknown".
Output valid JSON only."""

SYSTEM_IF = """You create instruction-following examples.
Each example must include constraints the assistant visibly follows.
Output a JSON object with key "items" containing an array of examples."""


def _normalize_label_types(types: list[str]) -> list[str]:
    out: list[str] = []
    for t in types:
        key = LABEL_TYPE_ALIASES.get(t.strip().lower())
        if key and key not in out:
            out.append(key)
    return out or ["sft", "instructions"]


def _sft_prompt(agent: str, doc: dict[str, Any]) -> str:
    text = doc["text"][:4000]
    if agent == "coding":
        return f"""From this document, create ONE Q&A training example as JSON:
{{"messages": [{{"role":"user","content":"..."}}, {{"role":"assistant","content":"..."}}],
  "task_type": "sft", "source_doc_id": "{doc['doc_id']}"}}

Document title: {doc.get('title', '')}
---
{text}
"""
    return f"""From this document, create ONE research Q&A with citation as JSON:
{{"messages": [{{"role":"user","content":"..."}}, {{"role":"assistant","content":"..."}}],
  "task_type": "sft", "source_doc_id": "{doc['doc_id']}", "citations": ["{doc.get('source_url', '')}"]}}

Document:
---
{text}
"""


def _if_prompt(agent: str, doc: dict[str, Any]) -> str:
    text = doc["text"][:2500]
    return f"""Create 2 instruction-following examples for agent "{agent}" grounded in this text.
Return JSON: {{"items": [
  {{"messages": [...], "constraints": ["max_bullets:3", "no_code"], "task_type": "instruction_following", "agent": "{agent}"}},
  {{"messages": [...], "constraints": ["json_only"], "task_type": "instruction_following", "agent": "{agent}"}}
]}}

Use realistic user requests. Assistant must obey constraints.

Document excerpt:
---
{text}
"""


def _normalize_sft(item: dict[str, Any], agent: str, doc_id: str) -> dict[str, Any] | None:
    messages = item.get("messages")
    if not messages or len(messages) < 2:
        return None
    return {
        "messages": messages,
        "task_type": "sft",
        "agent": agent,
        "source_doc_id": item.get("source_doc_id", doc_id),
        "citations": item.get("citations", []),
    }


def _write_draft(bound_ft: Any, key: str, rows: list[dict[str, Any]]) -> int:
    path = bound_ft / FT_DRAFT_FILES[key]
    clean = [r for r in rows if not r.get("_error") and not str(r.get("task_type", "")).endswith("_failed")]
    return write_jsonl(path, clean)


def run_label(
    agent: str,
    batch: str,
    types: list[str] | None = None,
    max_docs: int | None = None,
) -> dict[str, Any]:
    require_approved(agent, batch)
    settings = agent_settings(agent)
    types = _normalize_label_types(types or settings.get("label_types", ["sft", "instructions"]))
    max_docs = max_docs or settings.get("label_max_docs", 5)

    proc = process_dir(agent, batch)
    validated_path = proc / "validated.jsonl"
    if not validated_path.exists():
        raise FileNotFoundError(f"Missing: {validated_path}")

    bound_ft = serve_bound_dir(agent, batch) / "ft"
    ensure_dirs(bound_ft)

    system = SYSTEM_CODING if agent == "coding" else SYSTEM_RESEARCH
    buckets: dict[str, list[dict[str, Any]]] = {k: [] for k in FT_DRAFT_FILES}
    error_count = 0

    docs = list(read_jsonl(validated_path))[:max_docs]
    for doc in docs:
        if "sft" in types:
            try:
                item = chat_json(system, _sft_prompt(agent, doc))
                row = _normalize_sft(item, agent, doc["doc_id"])
                if row:
                    buckets["sft"].append(row)
            except Exception as exc:
                error_count += 1
                buckets["sft"].append({"_error": str(exc), "doc_id": doc["doc_id"]})

        if "instructions" in types:
            try:
                raw = chat_text(SYSTEM_IF, _if_prompt(agent, doc))
                for item in extract_json_array(raw):
                    item.setdefault("agent", agent)
                    item.setdefault("task_type", "instruction_following")
                    err = validate_instruction_row(item)
                    if err is None:
                        buckets["instructions"].append(item)
                    else:
                        buckets["instructions"].append({**item, "_validation_warning": err})
            except Exception as exc:
                error_count += 1

        if "tool_calling" in types:
            try:
                row = label_tool_calling(agent, doc)
                if row and validate_tool_calling_row(row) is None:
                    buckets["tool_calling"].append(row)
            except Exception:
                error_count += 1

        if "trajectories" in types:
            try:
                row = label_trajectory(agent, doc)
                if row and validate_trajectory_row(row) is None:
                    buckets["trajectories"].append(row)
            except Exception:
                error_count += 1

        if "multi_agent" in types:
            try:
                row = label_multi_agent(agent, doc)
                if row and validate_multi_agent_row(row) is None:
                    buckets["multi_agent"].append(row)
            except Exception:
                error_count += 1

    counts: dict[str, int] = {}
    for key in FT_DRAFT_FILES:
        counts[key] = _write_draft(bound_ft, key, buckets.get(key, []))

    meta = {
        "agent": agent,
        "batch": batch,
        "types": types,
        "docs_labeled": len(docs),
        "errors": error_count,
        **{f"{k}_count": v for k, v in counts.items()},
        "sft_count": counts.get("sft", 0),
        "instructions_count": counts.get("instructions", 0),
        "tool_calling_count": counts.get("tool_calling", 0),
        "trajectories_count": counts.get("trajectories", 0),
        "multi_agent_count": counts.get("multi_agent", 0),
    }
    (bound_ft / "label_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta
