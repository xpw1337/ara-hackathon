from __future__ import annotations

import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Iterable

from src.models import PaperCandidate


ARXIV_API_URL = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
DEFAULT_MAX_RESULTS = 12
MOCK_PAPERS = [
    {
        "paper_id": "2404.10001",
        "title": "Modeling Conversational Repair Signals in Human-Computer Interaction",
        "authors": ["A. Singh", "M. Chen"],
        "url": "https://arxiv.org/abs/2404.10001",
        "published_at": "2024-04-10T00:00:00+00:00",
        "summary": "Studies repair signals, hesitation, and behavior patterns in interactive systems.",
    },
    {
        "paper_id": "2403.20002",
        "title": "Pitch Tipping Detection From Multimodal Dialogue Behavior",
        "authors": ["R. Patel", "J. Kim"],
        "url": "https://arxiv.org/abs/2403.20002",
        "published_at": "2024-03-22T00:00:00+00:00",
        "summary": "Explores pitch tipping, speech prosody, and interaction dynamics for behavior modeling.",
    },
    {
        "paper_id": "2312.30003",
        "title": "Ranking Literature Recommendations With Lightweight Keyword Signals",
        "authors": ["L. Gomez"],
        "url": "https://arxiv.org/abs/2312.30003",
        "published_at": "2023-12-05T00:00:00+00:00",
        "summary": "Presents a simple ranking approach for surfacing relevant papers from keyword sets.",
    },
    {
        "paper_id": "2402.40004",
        "title": "Behavior Modeling for Adaptive Research Assistants",
        "authors": ["S. Davis", "N. Rao"],
        "url": "https://arxiv.org/abs/2402.40004",
        "published_at": "2024-02-18T00:00:00+00:00",
        "summary": "Covers behavior modeling, adaptive assistants, and HCI evaluation loops.",
    },
    {
        "paper_id": "2401.50005",
        "title": "Human-Centered Weekly Planning Agents for Knowledge Work",
        "authors": ["T. Brooks", "E. Wang"],
        "url": "https://arxiv.org/abs/2401.50005",
        "published_at": "2024-01-11T00:00:00+00:00",
        "summary": "Looks at planners that synthesize tasks, deadlines, and context for weekly prioritization.",
    },
]


def fetch_paper_candidates(
    keywords: list[str],
    max_results: int = DEFAULT_MAX_RESULTS,
) -> list[PaperCandidate]:
    normalized_keywords = _normalize_keywords(keywords)
    if not normalized_keywords:
        return []

    use_mock = os.environ.get("ARXIV_USE_MOCK", "").lower() in {"1", "true", "yes"}
    if use_mock:
        return _rank_mock_candidates(normalized_keywords, max_results)

    try:
        live_candidates = _fetch_from_arxiv(normalized_keywords, max_results)
        if live_candidates:
            return live_candidates
    except Exception:
        pass

    return _rank_mock_candidates(normalized_keywords, max_results)


def _fetch_from_arxiv(keywords: list[str], max_results: int) -> list[PaperCandidate]:
    params = {
        "search_query": " OR ".join(f'all:"{keyword}"' for keyword in keywords),
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=5) as response:
        payload = response.read()

    root = ET.fromstring(payload)
    candidates: list[PaperCandidate] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        title = _clean_text(entry.findtext("atom:title", default="", namespaces=ATOM_NS))
        summary = _clean_text(entry.findtext("atom:summary", default="", namespaces=ATOM_NS))
        published_raw = entry.findtext("atom:published", default="", namespaces=ATOM_NS)
        paper_url = entry.findtext("atom:id", default="", namespaces=ATOM_NS)
        authors = [
            _clean_text(author.findtext("atom:name", default="", namespaces=ATOM_NS))
            for author in entry.findall("atom:author", ATOM_NS)
        ]
        paper_id = paper_url.rsplit("/", 1)[-1] if paper_url else title.lower().replace(" ", "-")
        published_at = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
        candidate = _build_candidate(
            paper_id=paper_id,
            title=title,
            authors=authors,
            url=paper_url,
            published_at=published_at,
            summary=summary,
            keywords=keywords,
        )
        if candidate.keywords_matched:
            candidates.append(candidate)

    return sorted(candidates, key=lambda item: item.score, reverse=True)[:max_results]


def _rank_mock_candidates(keywords: list[str], max_results: int) -> list[PaperCandidate]:
    candidates = [
        _build_candidate(
            paper_id=paper["paper_id"],
            title=paper["title"],
            authors=paper["authors"],
            url=paper["url"],
            published_at=datetime.fromisoformat(paper["published_at"]),
            summary=paper["summary"],
            keywords=keywords,
        )
        for paper in MOCK_PAPERS
    ]
    matched = [candidate for candidate in candidates if candidate.keywords_matched]
    return sorted(matched, key=lambda item: item.score, reverse=True)[:max_results]


def _build_candidate(
    paper_id: str,
    title: str,
    authors: list[str],
    url: str,
    published_at: datetime,
    summary: str,
    keywords: list[str],
) -> PaperCandidate:
    keywords_matched = _match_keywords(f"{title} {summary}", keywords)
    score = _score_candidate(title=title, summary=summary, keywords=keywords_matched, published_at=published_at)
    reason = _build_reason(keywords_matched, published_at)
    return PaperCandidate(
        paper_id=paper_id,
        title=title,
        authors=authors,
        url=url,
        published_at=published_at,
        keywords_matched=keywords_matched,
        score=score,
        reason=reason,
        summary=summary,
    )


def _normalize_keywords(keywords: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    for keyword in keywords:
        cleaned = _clean_text(str(keyword)).lower()
        if cleaned and cleaned not in normalized:
            normalized.append(cleaned)
    return normalized


def _match_keywords(text: str, keywords: list[str]) -> list[str]:
    lowered_text = text.lower()
    text_tokens = set(re.findall(r"[a-z0-9]+", lowered_text))
    matched: list[str] = []
    for keyword in keywords:
        keyword_tokens = set(re.findall(r"[a-z0-9]+", keyword))
        if keyword in lowered_text or (keyword_tokens and keyword_tokens.issubset(text_tokens)):
            matched.append(keyword)
    return matched


def _score_candidate(
    title: str,
    summary: str,
    keywords: list[str],
    published_at: datetime,
) -> float:
    title_text = title.lower()
    summary_text = summary.lower()
    title_hits = sum(1 for keyword in keywords if keyword in title_text)
    summary_hits = sum(1 for keyword in keywords if keyword in summary_text)

    now = datetime.now(timezone.utc)
    age_days = max((now - published_at.astimezone(timezone.utc)).days, 0)
    recency_bonus = max(0.0, 1.5 - min(age_days, 365) / 365)

    return round((title_hits * 2.5) + (summary_hits * 1.5) + (len(keywords) * 1.2) + recency_bonus, 2)


def _build_reason(keywords_matched: list[str], published_at: datetime) -> str:
    keyword_text = ", ".join(keywords_matched[:3]) if keywords_matched else "broad relevance"
    return f"Matches {keyword_text}; published {published_at.date().isoformat()}."


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
