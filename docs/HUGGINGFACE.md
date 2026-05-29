# Upload to Hugging Face (separate dataset per file)

Maxxdata keeps **one file type = one folder** so you can upload each as its own HF dataset.

## 1. Build and promote locally

```powershell
python -m maxxdata ingest --agent coding --batch batch_002
python -m maxxdata clean --agent coding --batch batch_002
python -m maxxdata validate --agent coding --batch batch_002
python -m maxxdata approve --agent coding --batch batch_002
python -m maxxdata chunk-rag --agent coding --batch batch_002
python -m maxxdata label --agent coding --batch batch_002 --max-docs 5
python -m maxxdata promote --agent coding --batch batch_002 --version 2026.05.30.1
```

## 2. Export HF folders

```powershell
python -m maxxdata export-hf --agent coding --version 2026.05.30.1
```

Creates:

```text
exports/hf/
  coding-rag-2026.05.30.1/           ← upload as repo "yourname/coding-rag"
  coding-ft-sft-2026.05.30.1/        ← repo "yourname/coding-ft-sft"
  coding-ft-instructions-2026.05.30.1/
  coding-ft-tool_calls-2026.05.30.1/
  ...
```

Repeat for `research` with its version.

## 3. Upload (CLI)

```powershell
pip install huggingface_hub
huggingface-cli login

huggingface-cli upload yourname/coding-rag exports/hf/coding-rag-2026.05.30.1 . --repo-type dataset
huggingface-cli upload yourname/coding-ft-sft exports/hf/coding-ft-sft-2026.05.30.1 . --repo-type dataset
```

One repo per folder — never mix RAG + FT in one upload.

## Agents vs HF repos

| Agent | Config file | Example HF repos |
|-------|-------------|------------------|
| coding | `sources.coding.yaml` | `coding-rag`, `coding-ft-instructions`, … |
| research | `sources.research.yaml` | `research-rag`, `research-ft-trajectories`, … |
| cybersec (later) | `sources.cybersec.yaml` | `cybersec-rag`, … |

You only need configs for agents you actually run.
