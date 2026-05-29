# Maxx platform overview

```text
┌─────────────────────────────────────────────────────────────┐
│                     MAXX (user-facing)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
  ┌───────────┐      ┌─────────────┐     ┌──────────────┐
  │ Maxxdata  │      │ Maxx-agent  │     │ Maxx-eval    │
  │ (datasets)│ ───▶ │ (runtime)   │ ◀── │ (quality)    │
  └───────────┘      └─────────────┘     └──────────────┘
        │                   │
        │ RAG parquet       │ tools, memory, multi-agent
        │ FT jsonl          │
        └───────────────────┘
```

| Repo folder | Status | Role |
|-------------|--------|------|
| `maxxdata/` | **Built** | Ingest, clean, label, promote, HF export |
| `maxx-agent/` | **Planned** | Agent loop, tools, RAG query, memory |
| `docs/platform/` | **Docs** | What to build and in what order |

**Rule:** Tools + RAG + eval **before** fine-tuning. See [06-tools-before-finetuning.md](06-tools-before-finetuning.md).
