from __future__ import annotations

from typing import Any

import ara_sdk as ara

from src.state.store import build_dashboard_snapshot
from src.workflows.advisor_update import run_advisor_update
from src.workflows.paper_scout import run_paper_scout
from src.workflows.research_log import run_research_log


@ara.tool
def get_dashboard_snapshot() -> dict[str, Any]:
    """Return the latest workflow summaries for the frontend/dashboard."""
    return build_dashboard_snapshot()


@ara.tool
def run_research_log_workflow(
    project_name: str = "pitch-tipping",
    repo_full_name: str = "",
    week_start: str = "",
    use_mock: bool = True,
) -> dict[str, Any]:
    """Generate a weekly research log entry from coding activity."""
    return run_research_log(
        project_name=project_name,
        repo_full_name=repo_full_name,
        week_start=week_start,
        use_mock=use_mock,
    )


@ara.tool
def run_advisor_update_workflow(
    project_name: str = "pitch-tipping",
    repo_full_name: str = "",
    advisor_email: str = "",
    week_start: str = "",
    use_mock: bool = True,
) -> dict[str, Any]:
    """Draft a weekly advisor update using GitHub and WakaTime progress."""
    return run_advisor_update(
        project_name=project_name,
        repo_full_name=repo_full_name,
        advisor_email=advisor_email,
        week_start=week_start,
        use_mock=use_mock,
    )


@ara.tool
def run_paper_scout_workflow(
    keywords: str = "",
    max_results: int = 12,
    top_k: int = 3,
    reading_list_target: str = "local",
) -> dict[str, Any]:
    """Search, rank, dedupe, and persist weekly paper recommendations."""
    return run_paper_scout(
        keywords=keywords.strip() or None,
        max_results=max_results,
        top_k=top_k,
        reading_list_target=reading_list_target,
    )


ara.Automation(
    "grad-student-survival-agent",
    system_instructions=(
        "You are the Grad Student Survival Agent backend runtime. Prefer the "
        "workflow tools over ad-hoc reasoning. When asked to run a workflow, "
        "return concise, structured outputs that clearly distinguish live data "
        "from mocked fallback data. Never claim a real external action happened "
        "unless the tool result says it was live and successful."
    ),
    tools=[
        get_dashboard_snapshot,
        run_research_log_workflow,
        run_advisor_update_workflow,
        run_paper_scout_workflow,
    ],
)
