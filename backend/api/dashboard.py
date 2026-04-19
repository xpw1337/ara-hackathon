from __future__ import annotations

from typing import Any

from src.state.store import (
    PAPER_SCOUT_RUNS_PATH,
    RESEARCH_LOG_STATE_PATH,
    WEEKLY_UPDATES_PATH,
    current_timestamp,
    load_json,
)

WORKFLOW_IDS = [
    "research-log",
    "advisor-update",
    "paper-scout",
    "deadline-guardian",
    "week-planner",
]

_WORKFLOW_KEY_TO_ID = {
    "research_log": "research-log",
    "advisor_update": "advisor-update",
    "paper_scout": "paper-scout",
    "deadline_guardian": "deadline-guardian",
    "week_planner": "week-planner",
}

_DEADLINE_RUNS_PATH = "data/deadline_guardian_runs.json"
_WEEK_PLANNER_RUNS_PATH = "data/week_planner_runs.json"


def _idle_workflow() -> dict[str, Any]:
    return {
        "status": "idle",
        "lastRun": "",
        "summary": "",
        "artifacts": [],
        "errors": [],
    }


def _workflow_card_from_result(result: dict[str, Any] | None) -> dict[str, Any]:
    if not result:
        return _idle_workflow()
    ok = result.get("ok", False)
    return {
        "status": "success" if ok else "error",
        "lastRun": result.get("generated_at", "") or result.get("created_at", ""),
        "summary": result.get("summary", ""),
        "artifacts": result.get("artifacts", []),
        "errors": result.get("errors", []),
    }


def _latest_entry(path: str | Any, collection_key: str) -> dict[str, Any] | None:
    from pathlib import Path

    p = Path(path) if not isinstance(path, Path) else path
    payload = load_json(p, {collection_key: []})
    collection = payload.get(collection_key, [])
    return collection[-1] if collection else None


def _derive_stats(
    latest_log: dict[str, Any] | None,
    latest_update: dict[str, Any] | None,
    latest_guardian: dict[str, Any] | None,
    latest_scout: dict[str, Any] | None,
) -> dict[str, Any]:
    coding_hours = 0.0
    if latest_log:
        coding_hours = (
            latest_log.get("data", {}).get("wakatime", {}).get("total_hours", 0.0)
        )

    commits = 0
    if latest_update:
        commits = (
            latest_update.get("data", {}).get("github", {}).get("commit_count", 0)
        )

    upcoming_deadlines = 0
    if latest_guardian:
        upcoming_deadlines = latest_guardian.get("data", {}).get("urgent_count", 0)

    papers_found = 0
    if latest_scout:
        papers_found = latest_scout.get("data", {}).get("recommendation_count", 0)

    return {
        "codingHours": coding_hours,
        "commits": commits,
        "upcomingDeadlines": upcoming_deadlines,
        "papersFound": papers_found,
    }


def build_frontend_dashboard() -> dict[str, Any]:
    latest_log = _latest_entry(RESEARCH_LOG_STATE_PATH, "entries")
    latest_update = _latest_entry(WEEKLY_UPDATES_PATH, "updates")
    latest_scout = _latest_entry(PAPER_SCOUT_RUNS_PATH, "runs")
    latest_guardian = _latest_entry(_DEADLINE_RUNS_PATH, "runs")
    latest_planner = _latest_entry(_WEEK_PLANNER_RUNS_PATH, "runs")

    workflows: dict[str, Any] = {}
    for wf_id in WORKFLOW_IDS:
        workflows[wf_id] = _idle_workflow()

    workflows["research-log"] = _workflow_card_from_result(latest_log)
    workflows["advisor-update"] = _workflow_card_from_result(latest_update)
    workflows["paper-scout"] = _workflow_card_from_result(latest_scout)
    workflows["deadline-guardian"] = _workflow_card_from_result(latest_guardian)
    workflows["week-planner"] = _workflow_card_from_result(latest_planner)

    recent_artifacts: list[dict[str, Any]] = []
    for latest in [latest_log, latest_update, latest_scout]:
        if not latest:
            continue
        for artifact in latest.get("artifacts", [])[:1]:
            recent_artifacts.append(artifact)

    return {
        "generatedAt": current_timestamp(),
        "stats": _derive_stats(latest_log, latest_update, latest_guardian, latest_scout),
        "workflows": workflows,
        "recentArtifacts": recent_artifacts,
    }
