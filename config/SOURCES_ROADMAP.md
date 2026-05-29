# Coding sources roadmap (Maxx / Maxxdata)

## Live URL ingest (today)

Configured in `sources.coding.yaml`:

| Source | Role |
|--------|------|
| [DevDocs](https://devdocs.io/) | V1 hubs (no php/cpp/csharp) — **see DevDocs note below** |
| **Node.js, Next.js, Docker, FastAPI, Git** | Official docs + DevDocs where listed |
| [MDN](https://developer.mozilla.org/) | Web JS / Fetch API |
| [Python docs](https://docs.python.org/3/) | Official tutorials & stdlib |
| **Research V1** | EPA, NASA, CDC, WHO, Our World in Data, methods (see `sources.research.yaml`) |

Run: `python -m maxxdata ingest --agent coding --batch batch_XXX`

### DevDocs important note

`devdocs.io` pages need **JavaScript** — plain HTTP + trafilatura often returns empty/boilerplate. Use one of:

1. **Offline doc packs** — export from DevDocs app → unzip under `samples/coding/devdocs/` → add to `local_paths`
2. **Playwright ingest** (future stage) for live site
3. **MDN + python.org** in config (work today without JS)

---


## Planned — needs extra ingest (not URL scrape)

### LeetCode / Exercism

| Source | Why not plain `urls` | Approach |
|--------|----------------------|----------|
| LeetCode | Site ToS restricts scraping | Your own solution writeups in `local_paths`, or licensed exports only |
| Exercism | Dynamic app | [Exercism API](https://exercism.org/docs/building) — add `ingest_exercism` stage + token |

**FT goal:** problem statement → approach → code → complexity (tool-calling friendly).

### GitHub Issues / PRs

| Need | Approach |
|------|----------|
| Real issue → fix traces | GitHub REST/GraphQL with `GITHUB_TOKEN` |
| Config (future) | `github_repos: [owner/repo, ...]` in YAML |

**FT goal:** issue body → tool calls (`read_file`, `search`) → patch summary.

### Stack Overflow → base Q&A pairs

| Need | Approach |
|------|----------|
| Bulk Q&A | [Stack Exchange Data Dump](https://archive.org/details/stackexchange) (CC BY-SA) — download XML/7z |
| Ingest | Extract to JSONL → point `local_paths` at extracted folder |

Do **not** scrape stackoverflow.com live (rate limits + ToS).

**FT goal:** `task_type: sft` rows — question → accepted answer (+ tags).

---

## Suggested Hugging Face split (Maxx datasets)

| Repo name example | Contents |
|-------------------|----------|
| `maxx-coding-rag` | DevDocs + MDN + Python chunks |
| `maxx-coding-sft` | Q&A from docs + SO dump |
| `maxx-coding-if` | `instructions.jsonl` |
| `maxx-coding-tools` | `tool_calls.jsonl` |

Use `python -m maxxdata export-hf` after each promote.
