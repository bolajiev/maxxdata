# Maxx Platform

Monorepo for the **Maxx** agentic AI family.

| Folder | Purpose |
|--------|---------|
| **[maxxdata/](maxxdata/)** | Dataset pipeline — scrape, clean, RAG, FT, Hugging Face export |
| **[maxx-agent/](maxx-agent/)** | Agent runtime (planned) — tools, RAG retrieval, memory, multi-agent |
| **[docs/platform/](docs/platform/)** | Architecture & build order (read before fine-tuning) |

## Quick start (data pipeline)

```powershell
cd maxxdata
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install -e .
copy .env.example ..\.env
python -m maxxdata ingest --agent coding --batch batch_v1
```

Full guide: [maxxdata/README.md](maxxdata/README.md)

## Build order (important)

1. **Maxxdata** — datasets (you are here)
2. **Tools + RAG + eval** — before fine-tuning
3. **Maxx-agent runtime** — orchestration loop
4. **Fine-tune** (optional) — only if eval proves it helps

See [docs/platform/06-tools-before-finetuning.md](docs/platform/06-tools-before-finetuning.md).

## Author

[bolajiev](https://github.com/bolajiev) — pipeline repo: [maxxdata](https://github.com/bolajiev/maxxdata)
