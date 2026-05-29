# Which agent uses which config?

| Agent | Sources file | Hugging Face prefix (export) |
|-------|--------------|------------------------------|
| **coding** | `sources.coding.yaml` | `coding-rag`, `coding-ft-sft`, … |
| **research** | `sources.research.yaml` | `research-rag`, `research-ft-sft`, … |
v1 ships **coding + research only**. No cybersec config needed.

## Instruction following (IF)

| Method | Command | Needs API? |
|--------|---------|------------|
| **Seed (built-in examples)** | `python -m maxxdata seed-if --agent coding --batch batch_002` | No |
| **Generated from your docs** | `python -m maxxdata label --types instructions` | Yes (DeepSeek) |

Output file: `data/serve/<agent>/ft/<version>/instructions.jsonl` — upload separately to Hugging Face.
