# Dataset scraping — open tools & datasets

Maxxdata uses **trafilatura** today. You can extend with open-source crawlers and **public datasets** instead of scraping everything yourself.

## Already in Maxxdata

| Tool | Role |
|------|------|
| [trafilatura](https://github.com/adbar/trafilatura) | HTML → clean text (MIT) |
| [httpx](https://github.com/encode/httpx) | HTTP fetch |
| [simhash](https://github.com/1e0n/simhash) | Near-duplicate detection |
| **DeepSeek API** | Label SFT / IF / tool traces (not a scraper) |

## Open-source crawlers (add as ingest backends)

| Project | License | Best for |
|---------|---------|----------|
| [Scrapy](https://github.com/scrapy/scrapy) | BSD | Large crawls, sitemaps, many URLs |
| [Crawl4AI](https://github.com/unclecode/crawl4ai) | Apache-2.0 | JS pages, LLM-friendly markdown |
| [Firecrawl](https://github.com/mendableai/firecrawl) | AGPL / cloud | Structured site → markdown |
| [Playwright](https://github.com/microsoft/playwright) | Apache-2.0 | DevDocs-style JS sites |
| [unstructured](https://github.com/Unstructured-IO/unstructured) | Apache-2.0 | PDF, HTML, DOCX pipelines |
| [Docling](https://github.com/DS4SD/docling) | MIT | PDF / academic docs |

**Recommendation for Maxx v2:** add optional `ingest --backend crawl4ai` for DevDocs/MDN when trafilatura fails.

## Open datasets (no scraping needed)

Use these as `local_paths` after download — best for **Q&A at scale**.

| Dataset | Link | Use for Maxx |
|---------|------|----------------|
| **Stack Exchange dump** | [Archive.org](https://archive.org/details/stackexchange) | Coding Q&A → `sft.jsonl` |
| **The Stack / code** | [Hugging Face](https://huggingface.co/datasets) | Code (license filter!) |
| **FineWeb / Common Crawl** | HF / CC | General pretrain (heavy) |
| **OpenAssistant** | HF | Conversation format |
| **Glaive function calling** | HF | Tool-call examples |
| **Multilingual MD / docs** | Various | Expand RAG |

### Stack Overflow properly

1. Download **Creative Commons** Stack Exchange dump (not live scrape).
2. Convert `Posts.xml` → JSONL: `title + body` → `answer`.
3. Point Maxxdata: `local_paths: [stackexchange/python.jsonl]` (custom ingest script).

## Government / research (you already use)

| Source | License style | In `sources.research.yaml` |
|--------|---------------|----------------------------|
| EPA, NASA, CDC | US public domain | Yes |
| Our World in Data | CC BY | Yes |
| Wikipedia | CC BY-SA | Cite carefully |

## Sites that need special handling

| Site | Issue | Open approach |
|------|-------|----------------|
| **devdocs.io** | JavaScript | Offline export or Crawl4AI |
| **LeetCode** | ToS | Your solutions only, or licensed lists |
| **GitHub Issues** | API | `gh` CLI + `GITHUB_TOKEN` ingest |
| **Exercism** | API | [exercism.org/docs/building](https://exercism.org/docs/building) |

## Integrate with Maxxdata (roadmap)

| Priority | Feature |
|----------|---------|
| P1 | `maxxdata import-jsonl` — bulk local Q&A |
| P2 | `ingest --backend playwright` for JS docs |
| P3 | Stack Exchange dump converter script |
| P4 | GitHub Issues ingest via API |

## Hugging Face as hub

Publish Maxx datasets → use same repos for training:

```text
bolajiev/maxx-coding-rag
bolajiev/maxx-coding-ft-sft
```

Others can `load_dataset()` without re-scraping.

## Legal checklist

- [ ] Respect `robots.txt` and rate limits
- [ ] Prefer official APIs and public dumps
- [ ] Keep `source_url` + license in manifest
- [ ] Do not ship passwords or PII in JSONL
