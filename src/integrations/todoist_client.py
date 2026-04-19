from __future__ import annotations

import json
import os
from datetime import datetime, time, timedelta
from typing import Any, List
from urllib import error, parse, request

from src.models import PlanItem


TODOIST_TASKS_URL = "https://api.todoist.com/rest/v2/tasks"


def fetch_todoist_tasks() -> List[PlanItem]:
    """
    Fetch outstanding tasks from Todoist.
    Falls back to mock data when no token is configured.
    """
    if os.environ.get("TODOIST_USE_MOCK", "").lower() in {"1", "true", "yes"}:
        return _mock_tasks()

    token = (
        os.environ.get("TODOIST_API_TOKEN")
        or os.environ.get("TODOIST_API_KEY")
        or ""
    ).strip()
    if not token:
        return _mock_tasks()

    return _fetch_live_tasks(token)


def _fetch_live_tasks(token: str) -> List[PlanItem]:
    params = {}
    project_id = os.environ.get("TODOIST_PROJECT_ID", "").strip()
    if project_id:
        params["project_id"] = project_id

    task_filter = os.environ.get("TODOIST_FILTER", "").strip()
    if task_filter:
        params["filter"] = task_filter

    url = TODOIST_TASKS_URL
    if params:
        url = f"{url}?{parse.urlencode(params)}"

    req = request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, error.URLError) as exc:
        raise RuntimeError(f"Todoist live fetch failed: {exc}") from exc

    tasks: List[PlanItem] = []
    for item in payload:
        tasks.append(
            PlanItem(
                title=item.get("content", "Untitled task"),
                priority=_normalize_priority(item.get("priority", 1)),
                why_now=_build_why_now(item),
                due_at=_parse_todoist_due(item.get("due") or {}),
                source_refs=["Todoist", str(item.get("id", ""))],
            )
        )
    return tasks


def _normalize_priority(todoist_priority: Any) -> int:
    try:
        value = int(todoist_priority)
    except (TypeError, ValueError):
        value = 1
    value = max(1, min(4, value))
    return 5 - value


def _parse_todoist_due(due: dict[str, Any]) -> datetime | None:
    due_datetime = (due.get("datetime") or "").strip()
    if due_datetime:
        return datetime.fromisoformat(due_datetime.replace("Z", "+00:00"))

    due_date = (due.get("date") or "").strip()
    if due_date:
        return datetime.combine(datetime.fromisoformat(due_date).date(), time(23, 59))

    return None


def _build_why_now(item: dict[str, Any]) -> str:
    description = (item.get("description") or "").strip()
    labels = item.get("labels") or []
    if description:
        return description
    if labels:
        return f"Labeled: {', '.join(labels[:3])}"
    return "Open Todoist task"


def _mock_tasks() -> List[PlanItem]:
    now = datetime.now()
    return [
        PlanItem(
            title="Read paper regarding Paxos consensus",
            priority=1,
            why_now="Foundational for upcoming project",
            due_at=now + timedelta(days=3),
            source_refs=["Todoist"],
        ),
        PlanItem(
            title="Draft intro for thesis proposal",
            priority=2,
            why_now="Due end of month",
            due_at=None,
            source_refs=["Todoist"],
        ),
    ]
