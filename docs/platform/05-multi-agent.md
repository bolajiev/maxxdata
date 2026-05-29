# Multi-agent collaboration

## Training data vs runtime

| | Location |
|---|----------|
| **Training** | `maxxdata/data/serve/.../multi_agent.jsonl` |
| **Runtime** | `maxx-agent` orchestrator + named sub-agents |

## v1 multi-agent pattern (recommended)

```text
User
  │
  ▼
┌─────────────┐
│ Orchestrator │  "Maxx" — routes task, merges answer
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
 Coder   Researcher
 agent    agent
```

### Orchestrator responsibilities

- Classify intent: code / research / both
- Delegate with structured handoff JSON
- Enforce policies on each specialist
- Synthesize final reply

### Handoff payload

```json
{
  "from": "orchestrator",
  "to": "coder",
  "task": "Implement FastAPI health endpoint",
  "context": ["retrieved chunk ids"],
  "constraints": ["use existing project structure"]
}
```

### When to use multi-agent

| Use | Skip |
|-----|------|
| Task spans code + research | Simple single-domain question |
| Need separate tool sets | One RAG + one tool set enough |

## v2 (later)

- Parallel agents (reviewer + implementer)
- Debate / critique loop
- Shared blackboard state file

Start with **orchestrator + 2 specialists** on eval before adding complexity.
