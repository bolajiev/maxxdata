"""Export serve/ datasets into separate folders for Hugging Face upload."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from maxxdata.paths import DATA_DIR, ROOT

EXPORT_ROOT = ROOT / "exports" / "hf"

# Each key = one HF dataset repo (upload folder separately)
FT_FILES = {
    "sft": "sft.jsonl",
    "instructions": "instructions.jsonl",
    "tool_calls": "tool_calls.jsonl",
    "trajectories": "trajectories.jsonl",
    "multi_agent": "multi_agent.jsonl",
}


def _write_readme(path: Path, title: str, body: str) -> None:
    path.write_text(f"---\nlicense: mit\ntask_categories:\n- text-generation\n---\n\n# {title}\n\n{body}\n", encoding="utf-8")


def run_export_hf(agent: str, version: str) -> list[str]:
    """
    Create exports/hf/<agent>-<product>-<version>/ per file for separate HF uploads.
    Returns list of created folder paths.
    """
    created: list[str] = []
    serve = DATA_DIR / "serve" / agent

    rag_src = serve / "rag" / version
    if rag_src.exists():
        name = f"{agent}-rag-{version}"
        dst = EXPORT_ROOT / name
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        for f in rag_src.iterdir():
            if f.is_file():
                shutil.copy2(f, dst / f.name)
        _write_readme(
            dst / "README.md",
            f"{agent} RAG chunks v{version}",
            "Parquet chunks + manifest for retrieval. Upload this folder as its own HF dataset.",
        )
        created.append(str(dst))

    ft_src = serve / "ft" / version
    if ft_src.exists():
        for key, filename in FT_FILES.items():
            src_file = ft_src / filename
            if not src_file.exists():
                continue
            name = f"{agent}-ft-{key}-{version}"
            dst = EXPORT_ROOT / name
            if dst.exists():
                shutil.rmtree(dst)
            dst.mkdir(parents=True)
            shutil.copy2(src_file, dst / filename)
            manifest = ft_src / "manifest.json"
            if manifest.exists():
                shutil.copy2(manifest, dst / "manifest.json")
            _write_readme(
                dst / "README.md",
                f"{agent} FT {key} v{version}",
                f"Fine-tune data: `{filename}`. Upload as a **separate** Hugging Face dataset repo.",
            )
            created.append(str(dst))

    index = {"agent": agent, "version": version, "folders": created}
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    (EXPORT_ROOT / f"{agent}-{version}-index.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )
    return created
