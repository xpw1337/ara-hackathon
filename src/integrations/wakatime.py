from __future__ import annotations

import base64
import json
import os
from datetime import timedelta
from typing import Any
from urllib import error, parse, request

from src.state.models import WorkLogEntry
from src.state.store import current_timestamp, resolve_week_window


def get_weekly_wakatime_activity(
    project_name: str = "pitch-tipping",
    week_start: str = "",
    use_mock: bool = True,
) -> dict[str, Any]:
    start_date, end_date = resolve_week_window(week_start)

    if use_mock:
        return _mock_weekly_activity(project_name, start_date.isoformat())

    api_key = os.getenv("WAKATIME_API_KEY", "").strip()
    if not api_key:
        fallback = _mock_weekly_activity(project_name, start_date.isoformat())
        fallback["warnings"].append("WAKATIME_API_KEY not set; used mock activity.")
        return fallback

    try:
        return _fetch_live_activity(
            api_key=api_key,
            project_name=project_name,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
    except (OSError, ValueError, error.URLError) as exc:
        fallback = _mock_weekly_activity(project_name, start_date.isoformat())
        fallback["warnings"].append(f"Live WakaTime fetch failed: {exc}")
        return fallback


def _fetch_live_activity(
    api_key: str,
    project_name: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    query = parse.urlencode({"start": start_date, "end": end_date})
    url = f"https://wakatime.com/api/v1/users/current/summaries?{query}"
    token = base64.b64encode(f"{api_key}:".encode("utf-8")).decode("utf-8")
    req = request.Request(
        url,
        headers={
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
        },
    )

    with request.urlopen(req, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    entries: list[dict[str, Any]] = []
    total_seconds = 0.0
    themes: list[str] = []

    for day_summary in payload.get("data", []):
        grand_total = day_summary.get("grand_total", {})
        total_seconds += float(grand_total.get("total_seconds", 0.0))
        entry_date = day_summary.get("range", {}).get("date") or start_date
        project_summaries = day_summary.get("projects") or []

        day_project = project_name
        day_summary_text = grand_total.get("text") or "Coding activity captured."
        if project_summaries:
            best_project = max(
                project_summaries,
                key=lambda item: float(item.get("total_seconds", 0.0)),
            )
            day_project = best_project.get("name") or project_name
            day_summary_text = (
                f"{best_project.get('text', 'Worked on project tasks')} "
                f"in {day_project}."
            )
            if day_project not in themes:
                themes.append(day_project)

        entries.append(
            WorkLogEntry(
                week_start=start_date,
                date=entry_date,
                source="wakatime",
                hours=round(float(grand_total.get("total_seconds", 0.0)) / 3600, 2),
                project=day_project,
                summary=day_summary_text,
                commit_refs=[],
            ).to_dict()
        )

    return {
        "source_mode": "live",
        "project_name": project_name,
        "week_start": start_date,
        "week_end": end_date,
        "total_hours": round(total_seconds / 3600, 2),
        "entries": entries,
        "themes": themes[:3] or [project_name],
        "warnings": [],
        "generated_at": current_timestamp(),
    }


def _mock_weekly_activity(project_name: str, week_start: str) -> dict[str, Any]:
    start_date, _ = resolve_week_window(week_start)
    sample_days = [
        ("Model training experiments and cleanup", 3.4),
        ("Evaluation notebook pass and metrics review", 2.8),
        ("Dashboard integration planning and endpoint sketching", 2.1),
        ("Refactor for workflow boundaries and demo stability", 2.7),
    ]
    entries = []
    total_hours = 0.0

    for offset, (summary, hours) in enumerate(sample_days):
        total_hours += hours
        entries.append(
            WorkLogEntry(
                week_start=start_date.isoformat(),
                date=(start_date + timedelta(days=offset)).isoformat(),
                source="wakatime",
                hours=hours,
                project=project_name,
                summary=summary,
                commit_refs=[],
            ).to_dict()
        )

    return {
        "source_mode": "mock",
        "project_name": project_name,
        "week_start": start_date.isoformat(),
        "week_end": (start_date + timedelta(days=6)).isoformat(),
        "total_hours": round(total_hours, 2),
        "entries": entries,
        "themes": [
            "model training",
            "evaluation",
            "backend scaffolding",
        ],
        "warnings": [],
        "generated_at": current_timestamp(),
    }
