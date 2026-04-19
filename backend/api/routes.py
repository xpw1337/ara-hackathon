from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from backend.api.dashboard import build_frontend_dashboard
from backend.services.settings import get_settings, update_settings
from src.workflows.advisor_update import run_advisor_update
from src.workflows.deadline_guardian import run_deadline_guardian
from src.workflows.paper_scout import run_paper_scout
from src.workflows.research_log import run_research_log
from src.workflows.week_planner import run_week_planner

router = APIRouter()


@router.get("/dashboard")
def dashboard() -> dict[str, Any]:
    return build_frontend_dashboard()


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
    return run_deadline_guardian()


@router.post("/workflows/week-planner/run")
def run_week_planner_endpoint(
    body: dict[str, Any] = Body(default={}),
) -> dict[str, Any]:
    return run_week_planner()


@router.get("/settings")
def get_settings_endpoint() -> dict[str, Any]:
    return get_settings()


@router.post("/settings")
def save_settings_endpoint(
    body: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    return update_settings(body)
