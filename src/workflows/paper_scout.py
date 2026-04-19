from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.integrations.reading_list_writer import write_reading_list
from src.integrations.research_sources import fetch_paper_candidates
from src.models import PaperCandidate
from src.state.papers_seen import PapersSeenStore
from src.state.store import PAPER_SCOUT_RUNS_PATH, append_record, current_timestamp


DEFAULT_KEYWORDS = [
    "pitch tipping",
    "hci",
    "behavior modeling",
]


def run_paper_scout(
    keywords: Iterable[str] | str | None = None,
    max_results: int = 12,
    top_k: int = 3,
    state_path: str = "data/papers_seen.json",
    reading_list_path: str = "data/reading_list.md",
    reading_list_target: str | None = None,
    runs_path: str | Path = PAPER_SCOUT_RUNS_PATH,
) -> dict:
    try:
        resolved_keywords = _resolve_keywords(keywords)
        candidates = fetch_paper_candidates(resolved_keywords, max_results=max_results)

        seen_store = PapersSeenStore(state_path)
        seen_before = seen_store.load_seen_ids()
        unseen_candidates = [
            candidate for candidate in candidates if not seen_store.has_seen(candidate.paper_id)
        ]
        recommendations = unseen_candidates[:top_k]
        generated_at = current_timestamp()

        artifacts = [
            {
                "keywords": resolved_keywords,
                "recommendations": [_serialize_paper(candidate) for candidate in recommendations],
            }
        ]
        data = {
            "keywords": resolved_keywords,
            "candidate_count": len(candidates),
            "recommendation_count": len(recommendations),
            "seen_count": len(seen_before),
        }

        if not recommendations:
            result = {
                "ok": True,
                "workflow": "paper_scout",
                "summary": "No new papers found for the configured keywords.",
                "artifacts": artifacts,
                "errors": [],
                "data": data,
                "generated_at": generated_at,
            }
            append_record(Path(runs_path), "runs", result, dedupe_key=None)
            return result

        reading_list_artifact = write_reading_list(
            recommendations,
            destination=reading_list_target,
            output_path=reading_list_path,
        )
        seen_ids = seen_store.mark_seen(candidate.paper_id for candidate in recommendations)
        artifacts.append(reading_list_artifact)
        artifacts.append({"state_path": state_path, "seen_count": len(seen_ids)})
        data["seen_count"] = len(seen_ids)

        result = {
            "ok": True,
            "workflow": "paper_scout",
            "summary": f"Ranked {len(candidates)} papers and saved {len(recommendations)} new recommendations.",
            "artifacts": artifacts,
            "errors": [],
            "data": data,
            "generated_at": generated_at,
        }
        append_record(Path(runs_path), "runs", result, dedupe_key=None)
        return result
    except Exception as exc:
        result = {
            "ok": False,
            "workflow": "paper_scout",
            "summary": "Failed to run paper scout.",
            "artifacts": [],
            "errors": [str(exc)],
            "data": {
                "keywords": _resolve_keywords(keywords),
                "candidate_count": 0,
                "recommendation_count": 0,
                "seen_count": 0,
            },
            "generated_at": current_timestamp(),
        }
        append_record(Path(runs_path), "runs", result, dedupe_key=None)
        return result


def _resolve_keywords(keywords: Iterable[str] | str | None) -> list[str]:
    if keywords is None:
        return list(DEFAULT_KEYWORDS)
    if isinstance(keywords, str):
        return [item.strip() for item in keywords.split(",") if item.strip()]
    return [str(item).strip() for item in keywords if str(item).strip()]


def _serialize_paper(candidate: PaperCandidate) -> dict:
    return {
        "paper_id": candidate.paper_id,
        "title": candidate.title,
        "authors": candidate.authors,
        "url": candidate.url,
        "published_at": candidate.published_at.isoformat(),
        "keywords_matched": candidate.keywords_matched,
        "score": candidate.score,
        "reason": candidate.reason,
        "summary": candidate.summary,
    }


if __name__ == "__main__":
    import pprint

    pprint.pprint(run_paper_scout())
