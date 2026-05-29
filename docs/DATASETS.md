# Dataset types (separate files — never mixed)

| What you call it | `task_type` | File after promote |
|------------------|-------------|-------------------|
| Instruction following | `instruction_following` | `instructions.jsonl` |
| Simple Q&A SFT | `sft` | `sft.jsonl` |
| Tool / function calling | `tool_calling` | `tool_calls.jsonl` |
| Multi-turn trajectory | `multi_turn_trajectory` | `trajectories.jsonl` |
| Multi-agent collaboration | `multi_agent_collaboration` | `multi_agent.jsonl` |
| RAG chunks (retrieval) | — | `chunks.parquet` (under `rag/`) |

## Instruction following

Generated in the **label** stage from your cleaned docs. Each row has:

- `messages` — user request + assistant reply
- `constraints` — e.g. `max_bullets:3`, `no_code`, `json_only`
- Script validation in `validators/rules.py` before save

Run:

```powershell
python -m maxxdata label --agent coding --batch batch_001 --types instructions --max-docs 3
```

## Tool calling (function calling)

OpenAI-style traces: `assistant` with `tool_calls`, then `tool` role with result, then final `assistant`.

```powershell
python -m maxxdata label --agent coding --batch batch_001 --types tool_calling --max-docs 3
```

## Multi-turn trajectories

Full episodic dialogs (plan → act → observe → answer), 3+ turns.

```powershell
python -m maxxdata label --agent coding --batch batch_001 --types trajectories --max-docs 3
```

## Multi-agent collaboration

Multiple named assistants (e.g. `orchestrator`, `specialist`) in one episode.

```powershell
python -m maxxdata label --agent coding --batch batch_001 --types multi_agent --max-docs 3
```

## All FT types at once

```powershell
python -m maxxdata label --agent coding --batch batch_001 --max-docs 5
python -m maxxdata promote --agent coding --batch batch_001 --version 2026.05.29.3
```

Output: `data/serve/coding/ft/<version>/` with one JSONL per type.
