"""Rule-based document cleaning (no ML)."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0

BOILERPLATE_PATTERNS = [
    re.compile(r"cookie(s)?\s+policy", re.I),
    re.compile(r"subscribe\s+to\s+our\s+newsletter", re.I),
    re.compile(r"all\s+rights\s+reserved", re.I),
    re.compile(r"click\s+here\s+to", re.I),
]


def content_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def detect_language(text: str) -> str | None:
    sample = text[:5000]
    if len(sample) < 50:
        return None
    try:
        return detect(sample)
    except LangDetectException:
        return None


def boilerplate_score(text: str) -> int:
    return sum(1 for p in BOILERPLATE_PATTERNS if p.search(text))


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def clean_document(
    doc: dict[str, Any],
    *,
    min_chars: int = 200,
    allowed_langs: list[str] | None = None,
    max_boilerplate: int = 2,
) -> tuple[dict[str, Any] | None, str | None]:
    """
    Clean a raw document dict. Returns (cleaned_doc, None) or (None, reject_reason).
    """
    text = doc.get("text") or ""
    text = clean_text(text)
    if len(text) < min_chars:
        return None, "thin"

    if allowed_langs:
        lang = detect_language(text)
        if lang and lang not in allowed_langs:
            return None, "wrong_lang"

    if boilerplate_score(text) > max_boilerplate:
        return None, "boilerplate"

    cleaned = {**doc, "text": text, "content_hash": content_hash(text)}
    if "lang" not in cleaned:
        cleaned["lang"] = detect_language(text) or "unknown"
    return cleaned, None
