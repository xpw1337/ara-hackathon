from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


DATA_DIR = Path("data")
RESEARCH_LOG_STATE_PATH = DATA_DIR / "research_log_state.json"
WEEKLY_UPDATES_PATH = DATA_DIR / "weekly_updates.json"
DRAFT_ARCHIVE_PATH = DATA_DIR / "draft_archive.json"


def current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def resolve_week_window(week_start: str = "") -> tuple[date, date]:
    if week_start:
        base_date = date.fromisoformat(week_start)
    else:
        today = datetime.now().date()
        base_date = today - timedelta(days=today.weekday())
    return base_date, base_date + timedelta(days=6)


def ensure_json_file(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    DATA_DIR.mkdir(exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        path.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    return ensure_json_file(path, default)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_record(
    path: Path,
    collection_key: str,
    record: dict[str, Any],
    dedupe_key: str | None = "week_start",
) -> dict[str, Any]:
    payload = load_json(path, {collection_key: []})
    collection = payload.setdefault(collection_key, [])

    if dedupe_key and record.get(dedupe_key):
        for index, existing in enumerate(collection):
            if existing.get(dedupe_key) == record[dedupe_key]:
                collection[index] = record
                save_json(path, payload)
                return record

    collection.append(record)
    save_json(path, payload)
    return record


def _latest_entry(path: Path, collection_key: str) -> dict[str, Any] | None:
    payload = load_json(path, {collection_key: []})
    collection = payload.get(collection_key, [])
    if not collection:
        return None
    return collection[-1]


def build_dashboard_snapshot() -> dict[str, Any]:
    latest_log = _latest_entry(RESEARCH_LOG_STATE_PATH, "entries")
    latest_update = _latest_entry(WEEKLY_UPDATES_PATH, "updates")

    cards = [
        {
            "workflow": "research_log",
            "title": "Research Log",
            "status": "ready" if latest_log else "idle",
            "summary": (latest_log or {}).get(
                "summary",
                "No research log generated yet.",
            ),
            "updated_at": (latest_log or {}).get("generated_at", ""),
        },
        {
            "workflow": "advisor_update",
            "title": "Advisor Update",
            "status": "ready" if latest_update else "idle",
            "summary": (latest_update or {}).get(
                "summary",
                "No advisor update drafted yet.",
            ),
            "updated_at": (latest_update or {}).get("generated_at", ""),
        },
        {
            "workflow": "paper_scout",
            "title": "Paper Scout",
            "status": "pending",
            "summary": "Awaiting research-lane implementation.",
            "updated_at": "",
        },
        {
            "workflow": "deadline_guardian",
            "title": "Deadline Guardian",
            "status": "pending",
            "summary": "Awaiting planning-lane implementation.",
            "updated_at": "",
        },
        {
            "workflow": "week_planner",
            "title": "Week Planner",
            "status": "pending",
            "summary": "Awaiting planning-lane implementation.",
            "updated_at": "",
        },
    ]

    recent_artifacts: list[dict[str, Any]] = []
    for latest in [latest_log, latest_update]:
        if not latest:
            continue
        for artifact in latest.get("artifacts", [])[:1]:
            recent_artifacts.append(artifact)

    return {
        "generated_at": current_timestamp(),
        "workflow_cards": cards,
        "recent_artifacts": recent_artifacts,
    }
