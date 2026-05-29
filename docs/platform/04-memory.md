# Memory (short vs long)

## Three layers

| Layer | Lifetime | Storage | Maxx component |
|-------|----------|---------|----------------|
| **Short (session)** | One chat | RAM / Redis | Last N messages + tool traces |
| **Working (task)** | One goal | Session state | Current plan, open files, pending tools |
| **Long (optional)** | Weeks+ | DB / files | User prefs, past project summaries |

RAG is **not** memory — it is **external knowledge** (docs you ingested).

## Short-term session memory

Store:

```json
{"role": "user", "content": "..."}
{"role": "assistant", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

Trim when over token budget: keep system + last K turns + summary of older turns.

## Working memory (coding)

- Current repo path
- Files touched this session
- Last test output

## Long-term (v2)

- Embed past successful Q&A
- User style prefs ("always 3 bullets")
- Only store after user approval (privacy)

## Implementation order

1. Session buffer (list of messages)
2. Token counter + trim
3. Optional SQLite for long-term later
