# Wire RAG to the agent

## Inputs from Maxxdata

After `promote`:

```text
maxxdata/data/serve/coding/rag/1.0.0/chunks.parquet
maxxdata/data/serve/coding/rag/1.0.0/sources.jsonl
```

Each chunk row: `chunk_id`, `text`, `source_url`, `title`, `doc_id`.

## Steps to wire

### 1. Index chunks

| Option | When to use |
|--------|-------------|
| **Chroma** (local) | Fastest v1 |
| **LanceDB** | Simple file-based |
| **Qdrant / pgvector** | Production |

```text
for each chunk in parquet:
  embedding = embed_model(chunk.text)
  store(chunk_id, embedding, metadata)
```

Use same embedding model at query time (e.g. `text-embedding-3-small` or open source `bge-small`).

### 2. Retrieve at query time

```text
query_embedding = embed(user_message)
top_k = search(query_embedding, k=8)
context = format_chunks(top_k)  # include source_url for citations
```

### 3. Inject into prompt

```text
System: Answer using ONLY the context below. Cite source_url. If missing, say unknown.

<context>
[1] source: https://fastapi.tiangolo.com/ ...
{chunk text}
</context>

User: {question}
```

### 4. Log retrieval for eval

Store `chunk_ids` used per answer → measure hit rate on golden questions.

## Per-agent collections

| Collection | Parquet source |
|------------|----------------|
| `maxx-coding-rag` | `serve/coding/rag/<version>/` |
| `maxx-research-rag` | `serve/research/rag/<version>/` |

Never mix coding + research in one index.
