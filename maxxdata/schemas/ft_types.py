"""Fine-tune dataset types and file layout (one file per type, never mixed).

| task_type                    | serve file              | Common name              |
|------------------------------|-------------------------|--------------------------|
| sft                          | sft.jsonl               | SFT / Q&A                |
| instruction_following        | instructions.jsonl      | IF / constraint following|
| tool_calling                 | tool_calls.jsonl        | function/tool calling    |
| multi_turn_trajectory        | trajectories.jsonl      | agent trajectories       |
| multi_agent_collaboration    | multi_agent.jsonl       | multi-agent workflows    |
"""

FT_DRAFT_FILES = {
    "sft": "sft_draft.jsonl",
    "instructions": "instructions_draft.jsonl",
    "tool_calling": "tool_calls_draft.jsonl",
    "trajectories": "trajectories_draft.jsonl",
    "multi_agent": "multi_agent_draft.jsonl",
}

# CLI shorthand -> internal type key
LABEL_TYPE_ALIASES = {
    "sft": "sft",
    "instructions": "instructions",
    "if": "instructions",
    "tool_calling": "tool_calling",
    "tool_calls": "tool_calling",
    "tools": "tool_calling",
    "trajectories": "trajectories",
    "trajectory": "trajectories",
    "multi_turn": "trajectories",
    "multi_agent": "multi_agent",
    "agents": "multi_agent",
}
