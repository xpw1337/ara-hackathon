from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from backend.services.settings import get_settings, update_settings
from src.state.store import build_dashboard_snapshot
from src.workflows.advisor_update import run_advisor_update
from src.workflows.research_log import run_research_log

router = APIRouter()


@router.get("/dashboard")
def dashboard() -> dict[str, Any]:
    settings = get_settings()
    snapshot = build_dashboard_snapshot()

    workflow_id_map = {
        "research_log": "research-log",
        "advisor_update": "advisor-update",
        "paper_scout": "paper-scout",
        "deadline_guardian": "deadline-guardian",
        "week_planner": "week-planner",
    }
    workflows: dict[str, Any] = {}
    total_hours = 0.0
    total_commits = 0
    total_deadlines = 0
    total_papers = 0

    for card in snapshot.get("workflow_cards", []):
        wf_key = card.get("workflow", "")
        frontend_id = workflow_id_map.get(wf_key, wf_key)
        status = card.get("status", "idle")
        if status == "ready":
            status = "success"
        workflows[frontend_id] = {
            "ok": status not in ("error", "pending"),
            "workflow": wf_key,
            "status": status,
            "lastRun": card.get("updated_at") or None,
            "summary": card.get("summary"),
            "artifacts": [],
            "errors": [],
        }

    for artifact in snapshot.get("recent_artifacts", []):
        wf_key = artifact.get("metadata", {}).get("week_start", "")
        art_type = artifact.get("type", "")
        if art_type == "markdown" and "research-log" in workflows:
            workflows["research-log"]["artifacts"].append(artifact)
            total_hours = artifact.get("metadata", {}).get("total_hours", 0)
            total_commits = len(artifact.get("metadata", {}).get("commit_refs", []))
        elif art_type == "email_draft" and "advisor-update" in workflows:
            workflows["advisor-update"]["artifacts"].append(artifact)
        elif art_type == "paper" and "paper-scout" in workflows:
            workflows["paper-scout"]["artifacts"].append(artifact)
            total_papers += 1

    details = {}
    for card in snapshot.get("workflow_cards", []):
        if card.get("workflow") == "paper_scout":
            details = card.get("details", {})
            total_papers = max(total_papers, details.get("seen_paper_count", 0))

    return {
        "stats": {
            "codingHours": total_hours,
            "commits": total_commits,
            "upcomingDeadlines": total_deadlines,
            "papersFound": total_papers,
        },
        "workflows": workflows,
        "settings": settings,
    }


@router.post("/workflows/research-log/run")
def run_research_log_endpoint(
    body: dict[str, Any] = Body(default={}),
) -> dict[str, Any]:
    settings = get_settings()
    return run_research_log(
        project_name=body.get("projectName", settings.get("projectName", "pitch-tipping")),
        repo_full_name=body.get("repoName", settings.get("repoName", "")),
        week_start=body.get("weekStart", ""),
        use_mock=body.get("useMock", settings.get("useMock", True)),
    )


@router.post("/workflows/advisor-update/run")
def run_advisor_update_endpoint(
    body: dict[str, Any] = Body(default={}),
) -> dict[str, Any]:
    settings = get_settings()
    return run_advisor_update(
        project_name=body.get("projectName", settings.get("projectName", "pitch-tipping")),
        repo_full_name=body.get("repoName", settings.get("repoName", "")),
        advisor_email=body.get("advisorEmail", settings.get("advisorEmail", "")),
        week_start=body.get("weekStart", ""),
        use_mock=body.get("useMock", settings.get("useMock", True)),
    )


@router.post("/workflows/paper-scout/run")
def run_paper_scout_endpoint(
    body: dict[str, Any] = Body(default={}),
) -> dict[str, Any]:
    try:
        from src.workflows.paper_scout import run_paper_scout
    except ImportError:
        return {
            "ok": False,
            "workflow": "paper_scout",
            "summary": "Paper scout workflow not available yet.",
            "artifacts": [],
            "errors": ["paper_scout module not found"],
        }
    settings = get_settings()
    keywords = body.get("keywords", settings.get("keywords", ""))
    return run_paper_scout(
        keywords=keywords.strip() or None,
        max_results=body.get("maxResults", 12),
        top_k=body.get("topK", 3),
        reading_list_target=body.get("readingListTarget", settings.get("writeDestination", "local")),
    )


@router.post("/workflows/deadline-guardian/run")
def run_deadline_guardian_endpoint(
    body: dict[str, Any] = Body(default={}),
) -> dict[str, Any]:
    try:
        from src.workflows.deadline_guardian import run_deadline_guardian
        return run_deadline_guardian()
    except (ImportError, AttributeError):
        return {
            "ok": False,
            "workflow": "deadline_guardian",
            "summary": "Deadline guardian workflow not available yet.",
            "artifacts": [],
            "errors": ["deadline_guardian not implemented"],
        }


@router.post("/workflows/week-planner/run")
def run_week_planner_endpoint(
    body: dict[str, Any] = Body(default={}),
) -> dict[str, Any]:
    try:
        from src.workflows.week_planner import run_week_planner
        return run_week_planner()
    except (ImportError, AttributeError):
        return {
            "ok": False,
            "workflow": "week_planner",
            "summary": "Week planner workflow not available yet.",
            "artifacts": [],
            "errors": ["week_planner not implemented"],
        }


@router.get("/settings")
def get_settings_endpoint() -> dict[str, Any]:
    return get_settings()


@router.post("/settings")
def save_settings_endpoint(
    body: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    return update_settings(body)
