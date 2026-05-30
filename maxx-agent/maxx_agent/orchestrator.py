"""Agent orchestration loop."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from maxx_agent.config import load_agent_config
from maxx_agent.llm import chat, message_to_dict, parse_tool_args
from maxx_agent.memory.session import SessionMemory
from maxx_agent.paths import PLATFORM_ROOT
from maxx_agent.rag.retriever import RagRetriever
from maxx_agent.tools.registry import ToolContext, run_tool, schemas


class MaxxAgent:
    def __init__(
        self,
        agent: str = "coding",
        rag_version: str | None = None,
        workspace: Path | None = None,
        max_tool_calls: int = 8,
    ) -> None:
        self.cfg = load_agent_config(agent)
        self.agent = self.cfg["agent_key"]
        self.memory = SessionMemory(max_turns=self.cfg.get("max_turns", 20))
        self.rag = RagRetriever(self.agent, rag_version)
        self.workspace = workspace or PLATFORM_ROOT
        self.max_tool_calls = max_tool_calls
        self.memory.set_system(self.cfg.get("system_prompt", "You are Maxx, a helpful assistant."))

    def run(self, user_message: str) -> str:
        ctx = ToolContext(self.agent, self.workspace, self.rag)
        self.memory.add({"role": "user", "content": user_message})

        tool_calls_used = 0
        while tool_calls_used < self.max_tool_calls:
            response = chat(self.memory.get(), tools=schemas(self.agent))
            msg = response.choices[0].message
            self.memory.add(message_to_dict(msg))

            if not msg.tool_calls:
                return (msg.content or "").strip()

            for tc in msg.tool_calls:
                tool_calls_used += 1
                name = tc.function.name
                args = parse_tool_args(tc.function.arguments)
                result = run_tool(name, args, ctx)
                self.memory.add(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )

        return "Stopped: max tool calls reached. Try a simpler question."
