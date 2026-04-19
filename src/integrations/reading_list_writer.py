from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable

from src.models import PaperCandidate


DEFAULT_READING_LIST_PATH = "data/reading_list.md"


def write_reading_list(
    papers: Iterable[PaperCandidate],
    destination: str | None = None,
    output_path: str | None = None,
) -> dict:
    papers = list(papers)
    target = (destination or os.environ.get("READING_LIST_TARGET", "local")).lower()
    fallback_from = None

    if target not in {"local", "notion", "drive"}:
        fallback_from = target
        target = "local"
    elif target in {"notion", "drive"}:
        fallback_from = target
        target = "local"

    path = Path(output_path or DEFAULT_READING_LIST_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = _build_markdown_entry(papers)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)

    artifact = {
        "target": target,
        "path": str(path),
        "paper_count": len(papers),
    }
    if fallback_from:
        artifact["fallback_from"] = fallback_from
    return artifact


def _build_markdown_entry(papers: list[PaperCandidate]) -> str:
    timestamp = datetime.now().isoformat(timespec="seconds")
    lines = [f"## Paper Scout Run - {timestamp}", ""]
    for paper in papers:
        authors = ", ".join(paper.authors) if paper.authors else "Unknown authors"
        lines.extend(
            [
                f"- [{paper.title}]({paper.url})",
                f"  - Authors: {authors}",
                f"  - Why it matters: {paper.reason}",
                f"  - Summary: {paper.summary}",
            ]
        )
    lines.extend(["", ""])
    return "\n".join(lines)
