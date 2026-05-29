"""Ingest stage: load local files and optional URLs into raw store."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import trafilatura

from maxxdata.config import agent_settings, load_sources
from maxxdata.io_utils import write_jsonl
from maxxdata.paths import SAMPLES_DIR, ensure_dirs, raw_dir


def _doc_id(source: str, suffix: str = "") -> str:
    h = hashlib.sha256(f"{source}{suffix}".encode()).hexdigest()[:12]
    return f"doc_{h}"


def _read_local_file(path: Path, agent: str) -> dict[str, Any] | None:
    if path.suffix.lower() not in (".md", ".txt", ".html", ".htm"):
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in (".html", ".htm"):
        extracted = trafilatura.extract(text, include_comments=False, include_tables=True)
        text = extracted or text
    return {
        "doc_id": _doc_id(str(path)),
        "source_url": path.as_uri(),
        "source_type": "local",
        "title": path.stem,
        "text": text,
        "agent": agent,
    }


def _fetch_url(url: str, agent: str, timeout: float = 30.0) -> dict[str, Any] | None:
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=timeout)
        resp.raise_for_status()
    except httpx.HTTPError:
        return None
    extracted = trafilatura.extract(
        resp.text,
        url=url,
        include_comments=False,
        include_tables=True,
    )
    if not extracted or len(extracted) < 100:
        return None
    if "requires javascript" in extracted.lower()[:500]:
        return None
    title = urlparse(url).path.rstrip("/").split("/")[-1] or url
    return {
        "doc_id": _doc_id(url),
        "source_url": url,
        "source_type": "url",
        "title": title,
        "text": extracted,
        "agent": agent,
    }


def run_ingest(agent: str, batch: str) -> dict[str, Any]:
    settings = agent_settings(agent)
    sources_cfg = load_sources(agent)
    out = raw_dir(agent, batch)
    ensure_dirs(out)

    docs: list[dict[str, Any]] = []
    errors: list[str] = []

    # Local sample paths (relative to project root)
    local_paths = sources_cfg.get("local_paths", [])
    for rel in local_paths:
        base = SAMPLES_DIR / rel if not Path(rel).is_absolute() else Path(rel)
        if base.is_file():
            doc = _read_local_file(base, agent)
            if doc:
                docs.append(doc)
        elif base.is_dir():
            for fp in sorted(base.rglob("*")):
                if fp.is_file():
                    doc = _read_local_file(fp, agent)
                    if doc:
                        docs.append(doc)
        else:
            errors.append(f"local_not_found:{rel}")

    # Optional URLs (respect rate limits in production)
    if sources_cfg.get("fetch_urls", False):
        allowed = sources_cfg.get("allowed_domains") or []
        for url in sources_cfg.get("urls", []):
            domain = urlparse(url).netloc.lower().removeprefix("www.")
            if allowed and not any(domain == d or domain.endswith("." + d) for d in allowed):
                errors.append(f"domain_blocked:{url}")
                continue
            doc = _fetch_url(url, agent)
            if doc:
                docs.append(doc)
            else:
                errors.append(f"url_failed:{url}")

    raw_jsonl = out / "raw.jsonl"
    count = write_jsonl(raw_jsonl, docs)
    meta = {
        "agent": agent,
        "batch": batch,
        "doc_count": count,
        "errors": errors,
        "min_chars_hint": settings.get("min_chars", 200),
    }
    (out / "ingest_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta
