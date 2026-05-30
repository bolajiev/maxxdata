"""Tool registry and execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from maxx_agent.rag.retriever import RagRetriever

ToolFn = Callable[[dict[str, Any], "ToolContext"], str]


class ToolContext:
    def __init__(self, agent: str, workspace: Path, rag: RagRetriever) -> None:
        self.agent = agent
        self.workspace = workspace.resolve()
        self.rag = rag


def _safe_path(workspace: Path, rel: str) -> Path | None:
    target = (workspace / rel).resolve()
    try:
        target.relative_to(workspace)
    except ValueError:
        return None
    return target if target.exists() else None


def tool_search_docs(args: dict[str, Any], ctx: ToolContext) -> str:
    query = args.get("query", "")
    if not query:
        return "Error: query required"
    chunks = ctx.rag.search(query, k=int(args.get("k", 6)))
    if not chunks:
        return "No matching documentation chunks found."
    return ctx.rag.format_context(chunks)


def tool_read_file(args: dict[str, Any], ctx: ToolContext) -> str:
    rel = args.get("path", "")
    p = _safe_path(ctx.workspace, rel)
    if p is None:
        return f"Error: cannot read path outside workspace or missing: {rel}"
    if p.is_dir():
        names = sorted(x.name for x in p.iterdir())[:50]
        return "Directory:\n" + "\n".join(names)
    text = p.read_text(encoding="utf-8", errors="replace")
    limit = int(args.get("max_chars", 8000))
    return text[:limit]


def tool_cite(args: dict[str, Any], ctx: ToolContext) -> str:
    url = args.get("source_url", "")
    title = args.get("title", "Source")
    return json.dumps({"citation": f"{title} — {url}"})


CODER_TOOLS: dict[str, tuple[dict[str, Any], ToolFn]] = {
    "search_docs": (
        {
            "type": "function",
            "function": {
                "name": "search_docs",
                "description": "Search coding documentation corpus (RAG).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "k": {"type": "integer", "default": 6},
                    },
                    "required": ["query"],
                },
            },
        },
        tool_search_docs,
    ),
    "read_file": (
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file under the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "max_chars": {"type": "integer"},
                    },
                    "required": ["path"],
                },
            },
        },
        tool_read_file,
    ),
}

RESEARCH_TOOLS: dict[str, tuple[dict[str, Any], ToolFn]] = {
    "search_corpus": (
        {
            "type": "function",
            "function": {
                "name": "search_corpus",
                "description": "Search research corpus (RAG). Cite sources in final answer.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}, "k": {"type": "integer"}},
                    "required": ["query"],
                },
            },
        },
        tool_search_docs,
    ),
    "cite_source": (
        {
            "type": "function",
            "function": {
                "name": "cite_source",
                "description": "Format a citation for a source URL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_url": {"type": "string"},
                        "title": {"type": "string"},
                    },
                    "required": ["source_url"],
                },
            },
        },
        tool_cite,
    ),
}


def get_tools(agent: str) -> dict[str, tuple[dict[str, Any], ToolFn]]:
    if agent == "research":
        return RESEARCH_TOOLS
    return CODER_TOOLS


def schemas(agent: str) -> list[dict[str, Any]]:
    return [spec for spec, _ in get_tools(agent).values()]


def run_tool(name: str, args: dict[str, Any], ctx: ToolContext) -> str:
    tools = get_tools(ctx.agent)
    if name not in tools:
        return f"Error: unknown tool {name}"
    _, fn = tools[name]
    try:
        return fn(args, ctx)[:12000]
    except Exception as exc:  # noqa: BLE001
        return f"Tool error: {exc}"
