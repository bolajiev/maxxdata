# Tools + policies (agentic actions)

## Build tools before fine-tuning

The model must **call real tools** in dev/eval before you trust fine-tuned weights.

### Coding agent tools (v1)

| Tool | Args | Policy |
|------|------|--------|
| `search_docs` | `query`, `agent=coding` | RAG only; no web unless allowed |
| `read_file` | `path` | Path must be under workspace root |
| `run_tests` | `command` | Allowlist: `pytest`, `npm test` |
| `list_dir` | `path` | No `..` escape |

### Research agent tools (v1)

| Tool | Args | Policy |
|------|------|--------|
| `search_corpus` | `query` | Research RAG index only |
| `format_citation` | `source_url`, `title` | Required on factual claims |
| `refuse` | `reason` | When evidence missing |

### Policy engine checks

- Max **10** tool calls per user turn
- Block paths outside workspace
- Block destructive shell (`rm -rf`, format, etc.)
- Research: if no chunk above score threshold → force `refuse` or "insufficient evidence"

### Match training data

Maxxdata produces `tool_calls.jsonl` — runtime tool schemas must **match** those names and argument shapes.

### Config example (future)

```yaml
# maxx-agent/config/coder.yaml
tools:
  - search_docs
  - read_file
  - run_tests
policies:
  max_tool_calls: 10
  workspace_root: "."
```
