from __future__ import annotations

from typing import Any

from src.integrations.github_client import get_weekly_commits
from src.integrations.wakatime import get_weekly_wakatime_activity
from src.state.models import WorkflowArtifact, workflow_result
from src.state.store import (
    RESEARCH_LOG_STATE_PATH,
    append_record,
    current_timestamp,
    resolve_week_window,
)


def run_research_log(
    project_name: str = "pitch-tipping",
    repo_full_name: str = "",
    week_start: str = "",
    use_mock: bool = True,
) -> dict[str, Any]:
    week_start_date, _ = resolve_week_window(week_start)
    week_start_iso = week_start_date.isoformat()

    wakatime_data = get_weekly_wakatime_activity(
        project_name=project_name,
        week_start=week_start_iso,
        use_mock=use_mock,
    )
    github_data = get_weekly_commits(
        repo_full_name=repo_full_name,
        week_start=week_start_iso,
        use_mock=use_mock,
    )

    themes = _top_themes(wakatime_data, github_data)
    commit_refs = [commit["sha"] for commit in github_data.get("commits", [])[:3]]
    summary = (
        f"Logged {wakatime_data['total_hours']:.1f} hours for the week of "
        f"{week_start_iso} with focus on {', '.join(themes[:3])}."
    )
    content = _render_research_log(
        project_name=project_name,
        week_start=week_start_iso,
        total_hours=wakatime_data["total_hours"],
        themes=themes,
        commits=github_data.get("commits", []),
    )

    artifact = WorkflowArtifact(
        type="markdown",
        title=f"Research log for {week_start_iso}",
        content=content,
        metadata={
            "week_start": week_start_iso,
            "project_name": project_name,
            "total_hours": wakatime_data["total_hours"],
            "source_mode": wakatime_data["source_mode"],
            "commit_refs": commit_refs,
        },
    )

    result = workflow_result(
        workflow="research_log",
        summary=summary,
        artifacts=[artifact],
        errors=[],
        data={
            "project_name": project_name,
            "week_start": week_start_iso,
            "wakatime": wakatime_data,
            "github": github_data,
        },
        generated_at=current_timestamp(),
    )
    append_record(RESEARCH_LOG_STATE_PATH, "entries", result)
    return result


def _top_themes(
    wakatime_data: dict[str, Any],
    github_data: dict[str, Any],
) -> list[str]:
    themes = list(wakatime_data.get("themes", []))
    for commit in github_data.get("commits", []):
        message = commit.get("message", "").lower()
        if "workflow" in message and "workflow orchestration" not in themes:
            themes.append("workflow orchestration")
        elif "summary" in message and "weekly summaries" not in themes:
            themes.append("weekly summaries")
        elif "endpoint" in message and "API design" not in themes:
            themes.append("API design")
        elif "scaffold" in message and "backend scaffolding" not in themes:
            themes.append("backend scaffolding")
    return themes[:4] or ["backend delivery"]


def _render_research_log(
    project_name: str,
    week_start: str,
    total_hours: float,
    themes: list[str],
    commits: list[dict[str, Any]],
) -> str:
    commit_lines = commits[:3] or [{"message": "No commits captured for this week."}]
    body_lines = [
        f"# Weekly Research Log",
        f"",
        f"- Week of: {week_start}",
        f"- Project: {project_name}",
        f"- Coding hours captured: {total_hours:.1f}",
        f"- Main themes: {', '.join(themes[:3])}",
        f"",
        "## What moved forward",
        f"This week focused on {', '.join(themes[:3])} across the active project work.",
        f"",
        "## Supporting commit signals",
    ]
    body_lines.extend(f"- {item['message']}" for item in commit_lines)
    return "\n".join(body_lines)
