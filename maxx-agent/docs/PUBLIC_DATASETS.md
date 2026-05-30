# Public datasets for Maxx (no scraping)

Use these to **train** models. Maxx-agent **runs** the agent; this doc lists **open data** you can pull with `maxx-agent datasets pull`.

## Quick pull (Hugging Face)

```powershell
pip install -e maxx-agent
maxx-agent datasets list
maxx-agent datasets pull --hf rajpurkar/squad --limit 500
maxx-agent datasets pull --hf glaiveai/glaive-function-calling-v2 --limit 300
```

Files save to: `maxx-agent/data/public/*.jsonl`

## Recommended catalog

| ID | Hugging Face | Best for |
|----|--------------|----------|
| **glaive-function-calling-v2** | `glaiveai/glaive-function-calling-v2` | Tool calling / function JSON |
| **openassistant** | `OpenAssistant/oasst1` | Multi-turn chat (filter quality) |
| **squad** | `rajpurkar/squad` | Q&A, grounding |
| **code-feedback** | `HuggingFaceH4/Code-Feedback` | Code preferences |
| **fineweb-edu-sample** | `HuggingFaceFW/fineweb-edu` | General text (use small `--limit` only) |

## Large public dumps (download separately)

| Source | URL | Use |
|--------|-----|-----|
| **Stack Exchange** | [Archive.org stackexchange](https://archive.org/details/stackexchange) | Coding Q&A millions of rows (CC BY-SA) |
| **Common Crawl** | [commoncrawl.org](https://commoncrawl.org/) | Raw web (needs heavy cleaning) |
| **RedPajama / FineWeb** | Hugging Face | Pretraining corpora |
| **The Stack** | HF bigcode | Code (check license per language) |
| **Wiki dumps** | dumps.wikimedia.org | Encyclopedia (CC BY-SA) |

Do **not** live-scrape Stack Overflow — use the official dump.

## Training workflow

```text
1. maxx-agent datasets pull  →  JSONL in data/public/
2. (optional) maxxdata promote your own RAG for inference
3. Fine-tune with Axolotl / LLaMA-Factory / HF TRL on JSONL
4. maxx-agent chat  →  test with RAG + tools
```

## Legal

- Check each dataset **license** on Hugging Face
- Stack Exchange: **CC BY-SA** — share-alike applies
- US gov pages (EPA/NASA): public domain for US federal work

Maxxdata = your **custom** curated data. Public HF sets = **scale** for fine-tuning.
