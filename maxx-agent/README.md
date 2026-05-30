# Maxx-agent (runtime)

Runs **Maxx** — agent loop with **RAG**, **tools**, and **memory**.  
Uses **DeepSeek** API. Training data can come from **public Hugging Face datasets** (no scraping required).

Maxxdata (sibling folder) = custom datasets. **Pause maxxdata** and use this for agent work.

## Install

```powershell
cd "c:\Users\user\Desktop\maxxdata guru"
.\.venv\Scripts\Activate.ps1
pip install -e maxx-agent

# .env at repo root:
# DEEPSEEK_API_KEY=sk-...
```

## Chat (needs RAG from maxxdata once)

```powershell
# Optional: promote batch_v1 first in maxxdata/
maxx-agent status --agent coding
maxx-agent chat --agent coding "How does FastAPI dependency injection work?"
maxx-agent chat --agent research "What does EPA say about heat islands? Cite sources."
```

## Public datasets for training

```powershell
maxx-agent datasets list
maxx-agent datasets pull --hf glaiveai/glaive-function-calling-v2 --limit 200
maxx-agent datasets pull --hf rajpurkar/squad --limit 500
```

Output: `maxx-agent/data/public/*.jsonl`  
Guide: [docs/PUBLIC_DATASETS.md](docs/PUBLIC_DATASETS.md)

## Architecture

| Module | Role |
|--------|------|
| `orchestrator.py` | Plan → tool calls → answer |
| `rag/retriever.py` | Search `maxxdata/data/serve/.../chunks.parquet` |
| `tools/registry.py` | `search_docs`, `read_file`, `cite_source` |
| `memory/session.py` | Chat history |
| `public_datasets.py` | HF `datasets` pull |

Platform docs: [../docs/platform/](../docs/platform/)

## Build order

1. **maxx-agent chat** works with RAG  
2. **Pull public JSONL** for fine-tune  
3. Fine-tune (optional)  
4. Return to maxxdata only when you need more **custom** docs
