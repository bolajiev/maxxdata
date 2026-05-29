# Agent runtime (Maxx-agent)

## What to add (not in Maxxdata)

Maxxdata only **produces files**. Maxx-agent **runs** the agent.

### Components to build

| Module | Responsibility |
|--------|----------------|
| `orchestrator` | Plan → act → observe loop; stop conditions |
| `llm_client` | DeepSeek V4-Flash / Pro; thinking mode for hard tasks |
| `tool_registry` | Register tools + JSON schemas |
| `tool_executor` | Run tools in sandbox; return observations |
| `rag_retriever` | Embed query → search `chunks.parquet` or vector DB |
| `prompt_builder` | System prompt + tools + RAG context + memory |
| `session_store` | Short-term chat history |
| `policy_engine` | Refusals, allowed domains, max tool calls |

### Agent loop (pseudocode)

```text
while not done:
  context = memory.get() + rag.retrieve(user_query) + tool_results
  response = llm.chat(context, tools=registry.schemas())
  if response.tool_calls:
    for call in response.tool_calls:
      result = executor.run(call)
      memory.append_observation(result)
  else:
    return response.text
```

### Agents (personalities)

| Agent | System prompt focus | Tools |
|-------|---------------------|-------|
| **Maxx Coder** | Code, docs, tests | `read_file`, `search_docs`, `run_tests` |
| **Maxx Research** | Citations, uncertainty | `search_corpus`, `cite`, `summarize` |

Same runtime, different config YAML per agent.

### Folder layout (planned)

```text
maxx-agent/
  maxx_agent/
    orchestrator.py
    llm.py
    tools/
    rag/
    memory/
    policies/
  config/
    coder.yaml
    research.yaml
  eval/
    golden_tasks.jsonl
```
