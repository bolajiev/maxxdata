# Maxxdata (dataset pipeline)

Part of the **Maxx** platform. Builds versioned datasets for **coding** and **research** agents.

## Install

```powershell
cd maxxdata
pip install -e .
copy .env.example .env
# DEEPSEEK_API_KEY for label stage
```

From repo root with shared venv:

```powershell
pip install -e maxxdata
```

## Where data lives on your PC

```text
maxxdata/data/
  corpus/raw/<agent>/<batch>/raw.jsonl     ← open in Cursor (readable)
  process/<agent>/<batch>/validated.jsonl
  serve-bound/<agent>/<batch>/rag/chunks.parquet
  serve/<agent>/rag/<version>/             ← after promote
  serve/<agent>/ft/<version>/instructions.jsonl
```

## Commands

```powershell
python -m maxxdata ingest --agent coding --batch batch_v1
python -m maxxdata clean --agent coding --batch batch_v1
python -m maxxdata validate --agent coding --batch batch_v1
python -m maxxdata approve --agent coding --batch batch_v1
python -m maxxdata chunk-rag --agent coding --batch batch_v1
python -m maxxdata seed-if --agent coding --batch batch_v1
python -m maxxdata label --agent coding --batch batch_v1 --max-docs 5
python -m maxxdata promote --agent coding --batch batch_v1 --version 1.0.0
python -m maxxdata export-hf --agent coding --version 1.0.0
```

## Config

- `config/sources.coding.yaml` — DevDocs, MDN, Node, Next.js, Docker, FastAPI, Git, Python
- `config/sources.research.yaml` — EPA, NASA, CDC, WHO, Our World in Data
- `config/agents.yaml` — clean/label settings

## Docs

- [docs/DATASETS.md](docs/DATASETS.md)
- [docs/HUGGINGFACE.md](docs/HUGGINGFACE.md)
- [config/SOURCES_ROADMAP.md](config/SOURCES_ROADMAP.md)

Platform architecture: [../docs/platform/](../docs/platform/)
