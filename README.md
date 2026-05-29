# Maxxdata

**Maxxdata** is the dataset pipeline for the **Maxx** agent family. The name fits: *Maxx* = agent, *Maxxdata* = curated data that powers it (same brand, clear role).

**Maxxdata** turns web pages and local documents into **versioned, upload-ready datasets** for agentic AI: RAG chunks, instruction-following (IF), tool-calling traces, multi-turn trajectories, and multi-agent examples.

Built for two agent domains out of the box:

| Agent | Purpose |
|-------|---------|
| **coding** | Docs, APIs, code help, tools like `read_file` / `run_tests` |
| **research** | Articles, citations, “unknown if not in source” behavior |

Each agent has its own sources config, RAG output, and fine-tune (FT) files — **never mixed in one folder**.

---

## Pipeline overview

```text
  config/sources.<agent>.yaml          YOU define sites & local paths
              │
              ▼
┌─────────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐
│ ingest  │──▶│  clean  │──▶│ validate │──▶│ approve │  ◀── you review rejects
└─────────┘   └─────────┘   └──────────┘   └─────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
              ┌──────────┐            ┌─────────────┐           ┌──────────┐
              │ chunk-rag│            │ label /     │           │ seed-if  │
              │ (no LLM) │            │ seed-ft     │           │ (no API) │
              └──────────┘            └─────────────┘           └──────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                            ┌─────────┐
                            │ promote │  →  data/serve/<agent>/rag|ft/<version>/
                            └─────────┘
                                 │
                                 ▼
                            ┌──────────┐
                            │ export-hf │  →  exports/hf/  (one folder per HF dataset)
                            └──────────┘
```

**Duplicate handling:** exact hash + near-duplicate (SimHash) during `clean`. Many URLs from one site are fine; copy-paste and mirrors are dropped.

---

## Requirements

- **Python 3.10+**
- **pip**
- Optional: **[DeepSeek API key](https://platform.deepseek.com/)** for `label` (generates SFT, IF, tool traces from your docs)
- Optional: **Hugging Face CLI** for uploading `exports/hf/` folders

---

## Installation

### Windows (PowerShell)

```powershell
git clone https://github.com/bolajiev/maxxdata.git
cd maxxdata

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .

copy .env.example .env
# Edit .env and set DEEPSEEK_API_KEY=sk-...  (only needed for `label`)
```

### macOS / Linux

```bash
git clone https://github.com/bolajiev/maxxdata.git
cd maxxdata

python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
```

---

## Configuration

| File | Purpose |
|------|---------|
| `config/sources.coding.yaml` | Local folders + URLs for **coding** agent |
| `config/sources.research.yaml` | Sources for **research** agent |
| `config/agents.yaml` | Min text length, language, chunk size, `label_types` |
| `.env` | `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL` (default: `deepseek-v4-flash`) |

### Adding scrape targets

Edit `config/sources.coding.yaml` (or research):

```yaml
fetch_urls: true
local_paths:
  - coding/docs
urls:
  - https://docs.python.org/3/tutorial/introduction.html
allowed_domains:
  - docs.python.org
```

You control every source. Nothing is scraped until `fetch_urls: true` and URLs are listed.

More detail: [config/AGENTS.md](config/AGENTS.md).

**Coding V1 sources:** Python, JS/TS, Node, Next.js, Docker, FastAPI, Git, MDN (+ more in v2) — `config/sources.coding.yaml`.  
**Research V1 sources:** EPA, NASA, CDC, WHO, Our World in Data, methods — `config/sources.research.yaml`.  
**Roadmap** (LeetCode, Exercism, GitHub, Stack Overflow dump): [config/SOURCES_ROADMAP.md](config/SOURCES_ROADMAP.md).

---

## How to run

Use a **batch id** per run (e.g. `batch_001`). Replace `coding` with `research` for the research agent.

### Full pipeline (RAG only, no API key)

```powershell
python -m maxxdata pipeline --agent coding --batch batch_001 --skip-label --version 2026.05.30.1
```

### Step-by-step (recommended for production)

```powershell
# 1. Collect raw documents
python -m maxxdata ingest --agent coding --batch batch_001

# 2. Clean + dedupe — check rejects
python -m maxxdata clean --agent coding --batch batch_001
python -m maxxdata validate --agent coding --batch batch_001
# Review: data/process/coding/batch_001/rejects.csv

# 3. Human gate
python -m maxxdata approve --agent coding --batch batch_001

# 4. RAG chunks (for vector DB / retrieval)
python -m maxxdata chunk-rag --agent coding --batch batch_001

# 5a. Instruction following WITHOUT API (seed examples)
python -m maxxdata seed-if --agent coding --batch batch_001

# 5b. OR generate all FT types WITH DeepSeek
python -m maxxdata label --agent coding --batch batch_001 --max-docs 5

# 6. Publish versioned datasets
python -m maxxdata promote --agent coding --batch batch_001 --version 2026.05.30.1

# 7. Catalog + HF export folders
python -m maxxdata inventory status
python -m maxxdata export-hf --agent coding --version 2026.05.30.1
```

---

## Output layout

```text
data/serve/
  coding/
    rag/<version>/
      chunks.parquet
      manifest.json
      sources.jsonl
    ft/<version>/
      instructions.jsonl      # instruction following
      sft.jsonl                 # Q&A SFT
      tool_calls.jsonl          # tool / function calling
      trajectories.jsonl        # multi-turn
      multi_agent.jsonl         # multi-agent collaboration
  research/
    rag/<version>/...
    ft/<version>/...
```

Dataset type reference: [docs/DATASETS.md](docs/DATASETS.md).

---

## CLI commands

| Command | Description |
|---------|-------------|
| `ingest` | Load `local_paths` + optional URLs → raw JSONL |
| `clean` | Filter language, length, boilerplate; dedupe |
| `validate` | Schema checks |
| `approve` | Required gate before RAG / label / promote |
| `chunk-rag` | Build parquet chunks |
| `seed-if` | Load built-in IF examples (no API) |
| `label` | DeepSeek generates FT JSONL drafts |
| `promote` | Copy to `data/serve/.../<version>/` |
| `export-hf` | One folder per file for Hugging Face upload |
| `pipeline` | Run all stages (use `--skip-label` without API key) |
| `inventory status` | Show catalog |

```powershell
python -m maxxdata --help
```

---

## Instruction following vs agents

**Coding** and **research** are **agents** (who the model is).

**Instruction following** is a **dataset type** (`instructions.jsonl`) — rules like “3 bullets only”, “JSON only”. It lives under each agent’s `ft/` folder, not as a third `sources.*` file.

| Build IF | Command |
|----------|---------|
| Seeds (no API) | `seed-if` → `promote` |
| From your docs | `label --types instructions` → `promote` |

---

## Hugging Face upload

Each output type gets its own export folder (separate HF dataset repos):

```powershell
python -m maxxdata export-hf --agent coding --version 2026.05.30.1
pip install huggingface_hub
huggingface-cli login
huggingface-cli upload bolajiev/coding-rag exports/hf/coding-rag-2026.05.30.1 . --repo-type dataset
huggingface-cli upload bolajiev/coding-ft-instructions exports/hf/coding-ft-instructions-2026.05.30.1 . --repo-type dataset
```

Full guide: [docs/HUGGINGFACE.md](docs/HUGGINGFACE.md).

---

## Project structure

```text
maxxdata/
  cli.py                 # CLI entrypoint
  stages/                # ingest, clean, validate, label, promote, ...
  cleaners/              # rule-based cleaning
  validators/            # row validation (incl. IF constraints)
config/
  agents.yaml
  sources.coding.yaml
  sources.research.yaml
samples/                 # starter docs + IF seeds
docs/
  DATASETS.md
  HUGGINGFACE.md
```

Generated at runtime (gitignored): `data/`, `exports/`, `.venv`, `.env`.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

**bolajiev** — [GitHub](https://github.com/bolajiev)
