# DevDocs offline docs (recommended)

The website https://devdocs.io/ needs JavaScript. For Maxxdata ingest, place **exported/offline** DevDocs files here (HTML or text).

1. Open DevDocs → Preferences → Offline → download languages you need  
2. Copy extracted files into this folder (e.g. `python/`, `javascript/`)  
3. Ensure `config/sources.coding.yaml` includes:

```yaml
local_paths:
  - coding/docs
  - coding/devdocs
```

Then run `python -m maxxdata ingest --agent coding --batch batch_XXX`.
