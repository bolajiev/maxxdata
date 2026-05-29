# Maxx-agent (runtime) — planned

Runs the **Maxx** agent loop: RAG + tools + memory + multi-agent routing.

**Not built yet.** Datasets come from [../maxxdata/](../maxxdata/).

## Depends on

1. Promoted RAG: `maxxdata/data/serve/<agent>/rag/<version>/chunks.parquet`
2. FT optional: `maxxdata/data/serve/<agent>/ft/<version>/*.jsonl`
3. [Platform docs](../docs/platform/) — especially [tools before fine-tuning](../docs/platform/06-tools-before-finetuning.md)

## Planned modules

| Module | Doc |
|--------|-----|
| Agent loop | [01-agent-runtime.md](../docs/platform/01-agent-runtime.md) |
| RAG wire-up | [02-rag-integration.md](../docs/platform/02-rag-integration.md) |
| Tools + policies | [03-tools-and-policies.md](../docs/platform/03-tools-and-policies.md) |
| Memory | [04-memory.md](../docs/platform/04-memory.md) |
| Multi-agent | [05-multi-agent.md](../docs/platform/05-multi-agent.md) |

## Status

- [ ] Phase 1: DeepSeek + `search_docs` + one coding golden eval
- [ ] Phase 2: Research agent + citations
- [ ] Phase 3: Orchestrator (coder + researcher)
- [ ] Phase 4: Session memory + logging

Switch to **Agent mode** in Cursor to scaffold `maxx-agent/` code when ready.
