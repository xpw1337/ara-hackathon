from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Iterable, List
from urllib import error, parse, request

from src.models import NormalizedDeadline


def fetch_canvas_deadlines() -> List[NormalizedDeadline]:
    """
    Fetch upcoming deadlines from Canvas.
    Falls back to mock data when Canvas credentials are not configured.
    """
    if os.environ.get("CANVAS_USE_MOCK", "").lower() in {"1", "true", "yes"}:
        return _mock_deadlines()

    base_url = os.environ.get("CANVAS_BASE_URL", "").strip().rstrip("/")
    token = (
        os.environ.get("CANVAS_API_TOKEN")
        or os.environ.get("CANVAS_API_KEY")
        or ""
    ).strip()
    if not base_url or not token:
        return _mock_deadlines()

    return _fetch_live_deadlines(base_url, token)


def _fetch_live_deadlines(base_url: str, token: str) -> List[NormalizedDeadline]:
    course_map = _resolve_courses(base_url, token)
    bucket = os.environ.get("CANVAS_ASSIGNMENT_BUCKET", "upcoming").strip() or "upcoming"

    deadlines: list[NormalizedDeadline] = []
    for course_id, course_name in course_map.items():
        params = parse.urlencode(
            {
                "bucket": bucket,
                "order_by": "due_at",
                "per_page": "50",
            }
        )
        url = f"{base_url}/api/v1/courses/{course_id}/assignments?{params}"
        for assignment in _fetch_json_pages(url, token):
            due_at = _parse_canvas_datetime(assignment.get("due_at"))
            if due_at is None:
                continue
            deadlines.append(
                NormalizedDeadline(
                    title=assignment.get("name", "Untitled assignment"),
                    source="Canvas",
                    due_at=due_at,
                    url=assignment.get("html_url") or f"{base_url}/courses/{course_id}/assignments/{assignment.get('id', '')}",
                    context=course_name,
                    importance=_importance_for_due_date(due_at),
                    dedupe_key=f"canvas:{course_id}:{assignment.get('id', '')}",
                )
            )
    return deadlines


def _resolve_courses(base_url: str, token: str) -> dict[str, str]:
    configured_ids = [item.strip() for item in os.environ.get("CANVAS_COURSE_IDS", "").split(",") if item.strip()]
    if configured_ids:
        return {course_id: f"Course {course_id}" for course_id in configured_ids}

    url = f"{base_url}/api/v1/users/self/favorites/courses?per_page=25"
    courses = _fetch_json_pages(url, token)
    return {str(course.get("id", "")): course.get("name", f"Course {course.get('id', '')}") for course in courses if course.get("id")}


def _fetch_json_pages(url: str, token: str) -> list[dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    items: list[dict[str, Any]] = []
    next_url: str | None = url

    while next_url:
        req = request.Request(next_url, headers=headers)
        try:
            with request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
                link_header = response.headers.get("Link", "")
        except (OSError, ValueError, error.URLError) as exc:
            raise RuntimeError(f"Canvas live fetch failed: {exc}") from exc

        if isinstance(payload, list):
            items.extend(payload)
        elif isinstance(payload, dict):
            items.append(payload)

        next_url = _parse_next_link(link_header)

    return items


def _parse_next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        section = part.strip()
        if 'rel="next"' not in section:
            continue
        if section.startswith("<") and ">" in section:
            return section[1:section.index(">")]
    return None


def _parse_canvas_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _importance_for_due_date(due_at: datetime) -> str:
    hours_until_due = (due_at - datetime.now(due_at.tzinfo)).total_seconds() / 3600
    if hours_until_due <= 72:
        return "high"
    if hours_until_due <= 168:
        return "medium"
    return "low"


def _mock_deadlines() -> List[NormalizedDeadline]:
    now = datetime.now()
    return [
        NormalizedDeadline(
            title="CS500: Distributed Systems Project 1",
            source="Canvas",
            due_at=now + timedelta(days=1, hours=5),
            url="https://canvas.example.edu/courses/1/assignments/1",
            context="CS500",
            importance="high",
            dedupe_key="canvas_cs500_p1",
        ),
        NormalizedDeadline(
            title="CS500: Weekly Quiz",
            source="Canvas",
            due_at=now + timedelta(days=4),
            url="https://canvas.example.edu/courses/1/assignments/2",
            context="CS500",
            importance="medium",
            dedupe_key="canvas_cs500_quiz2",
        ),
    ]
