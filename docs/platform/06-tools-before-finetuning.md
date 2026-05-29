# Tools before fine-tuning (read this first)

## Why order matters

Fine-tuning on bad or premature data **locks in** wrong behavior. Tool use and retrieval must work with **base model + prompts** first.

## Required build order

```text
Phase 1 — Data (Maxxdata)          ← YOU ARE HERE
  ingest → clean → RAG chunks → FT jsonl → promote → HF

Phase 2 — Runtime skeleton
  LLM client + 2 tools + RAG retrieve + print answer

Phase 3 — Eval
  50 golden tasks per agent
  Measure: success, citations, tool accuracy, IF compliance

Phase 4 — Expand tools & data
  Fix eval failures → targeted Maxxdata batches
  Add tool_calls.jsonl from real traces

Phase 5 — Fine-tune (optional)
  Only if Phase 3 shows prompt+RAG plateau
  Train on: sft, instructions, tool_calls, trajectories
```

## What NOT to do early

| Don't | Do instead |
|-------|----------------|
| Fine-tune before tools work | Implement `search_docs` + eval |
| Scrape 100 sites before eval | 20 good docs + golden tasks |
| One mixed dataset | Separate coding / research / file types |
| Skip human review on `approve` | Check `rejects.csv` |

## Definition of "ready to fine-tune"

- [ ] RAG answers doc questions with correct `source_url` on **>70%** of golden set
- [ ] Tools execute without sandbox escapes on test suite
- [ ] Instruction-following eval **>85%** on format constraints
- [ ] You have **500+** high-quality rows you would show a colleague

## Maxxdata outputs used for fine-tuning

| File | Use |
|------|-----|
| `sft.jsonl` | Q&A style |
| `instructions.jsonl` | Constraint following |
| `tool_calls.jsonl` | Function calling |
| `trajectories.jsonl` | Multi-step |
| `multi_agent.jsonl` | Handoffs |

RAG (`chunks.parquet`) is for retrieval at inference — not usually merged into FT unless doing joint training (advanced).
