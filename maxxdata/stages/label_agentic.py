"""LLM prompts for tool-calling, trajectories, and multi-agent datasets."""

from __future__ import annotations

from typing import Any

from maxxdata.llm import chat_json

SYSTEM_AGENTIC = """You create training data for agentic AI systems.
Output valid JSON only. Ground scenarios in the provided document.
Use OpenAI-style message roles: system, user, assistant, tool.
For tool calls use assistant messages with tool_calls and follow-up tool role messages."""


def _doc_excerpt(doc: dict[str, Any], limit: int = 3000) -> str:
    return f"Title: {doc.get('title', '')}\nSource: {doc.get('source_url', '')}\n---\n{doc['text'][:limit]}"


def label_tool_calling(agent: str, doc: dict[str, Any]) -> dict[str, Any] | None:
    """Function/tool calling trace grounded in document."""
    tools = (
        '[{"name":"read_file","description":"Read a file path"},{"name":"search_docs",'
        '"description":"Search documentation"},{"name":"run_tests","description":"Run test suite"}]'
        if agent == "coding"
        else '[{"name":"search_sources","description":"Search corpus"},{"name":"fetch_url",'
        '"description":"Fetch URL"},{"name":"cite_source","description":"Return citation"}]'
    )
    prompt = f"""From this document, create ONE tool-calling training example as JSON:
{{
  "messages": [
    {{"role":"user","content":"..."}},
    {{"role":"assistant","content":null,"tool_calls":[{{"id":"call_1","type":"function","function":{{"name":"...","arguments":"{{}}"}}}}]}},
    {{"role":"tool","tool_call_id":"call_1","content":"..."}},
    {{"role":"assistant","content":"final answer grounded in doc"}}
  ],
  "tools": {tools},
  "task_type": "tool_calling",
  "agent": "{agent}",
  "source_doc_id": "{doc['doc_id']}"
}}

Document:
{_doc_excerpt(doc)}
"""
    item = chat_json(SYSTEM_AGENTIC, prompt)
    item.setdefault("task_type", "tool_calling")
    item.setdefault("agent", agent)
    item.setdefault("source_doc_id", doc["doc_id"])
    return item if item.get("messages") else None


def label_trajectory(agent: str, doc: dict[str, Any]) -> dict[str, Any] | None:
    """Multi-turn trajectory (plan -> act -> observe -> finish)."""
    prompt = f"""From this document, create ONE multi-turn trajectory (3-6 turns) as JSON:
{{
  "messages": [
    {{"role":"user","content":"complex task"}},
    {{"role":"assistant","content":"step 1 plan"}},
    {{"role":"user","content":"observation or follow-up"}},
    {{"role":"assistant","content":"step 2"}},
    {{"role":"assistant","content":"final grounded answer"}}
  ],
  "task_type": "multi_turn_trajectory",
  "agent": "{agent}",
  "source_doc_id": "{doc['doc_id']}",
  "turn_count": 5
}}

Document:
{_doc_excerpt(doc)}
"""
    item = chat_json(SYSTEM_AGENTIC, prompt)
    item.setdefault("task_type", "multi_turn_trajectory")
    item.setdefault("agent", agent)
    item.setdefault("source_doc_id", doc["doc_id"])
    return item if len(item.get("messages", [])) >= 3 else None


def label_multi_agent(agent: str, doc: dict[str, Any]) -> dict[str, Any] | None:
    """Multi-agent collaboration (orchestrator + specialist handoff)."""
    prompt = f"""From this document, create ONE multi-agent collaboration example as JSON:
{{
  "messages": [
    {{"role":"user","content":"task requiring multiple roles"}},
    {{"role":"assistant","content":"[Orchestrator] delegating to specialist...", "name":"orchestrator"}},
    {{"role":"assistant","content":"[Specialist] work product grounded in doc...", "name":"specialist"}},
    {{"role":"assistant","content":"[Orchestrator] synthesis and final answer", "name":"orchestrator"}}
  ],
  "agents_involved": ["orchestrator","specialist"],
  "task_type": "multi_agent_collaboration",
  "agent": "{agent}",
  "source_doc_id": "{doc['doc_id']}"
}}

Use name field on assistant messages to distinguish agents.

Document:
{_doc_excerpt(doc)}
"""
    item = chat_json(SYSTEM_AGENTIC, prompt)
    item.setdefault("task_type", "multi_agent_collaboration")
    item.setdefault("agent", agent)
    item.setdefault("source_doc_id", doc["doc_id"])
    return item if item.get("messages") else None
