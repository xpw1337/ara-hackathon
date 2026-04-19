from __future__ import annotations

from typing import Any

from src.integrations.github_client import get_weekly_commits
from src.integrations.gmail_client import create_gmail_draft
from src.integrations.wakatime import get_weekly_wakatime_activity
from src.state.models import AdvisorUpdateDraft, WorkflowArtifact, workflow_result
from src.state.store import (
    WEEKLY_UPDATES_PATH,
    append_record,
    current_timestamp,
    resolve_week_window,
)


def run_advisor_update(
    project_name: str = "pitch-tipping",
    repo_full_name: str = "",
    advisor_email: str = "",
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

    progress_points = _build_progress_points(wakatime_data, github_data)
    blockers = [
        "Need final frontend contract alignment once Archit's dashboard shell lands.",
        "Real Gmail draft creation still needs OAuth-backed implementation.",
    ]
    next_steps = [
        "Wire stable workflow outputs into the dashboard cards.",
        "Swap mocked Gmail drafting for live draft creation when credentials are ready.",
        "Connect research-log persistence to the final write-back destination.",
    ]

    subject = f"Weekly update for {project_name} ({week_start_iso})"
    body = _render_advisor_email(
        project_name=project_name,
        week_start=week_start_iso,
        progress_points=progress_points,
        blockers=blockers,
        next_steps=next_steps,
    )
    draft = create_gmail_draft(
        subject=subject,
        body=body,
        to_email=advisor_email,
        use_mock=use_mock,
    )
    draft_model = AdvisorUpdateDraft(
        week_start=week_start_iso,
        repo=github_data["repo_full_name"],
        progress_points=progress_points,
        blockers=blockers,
        next_steps=next_steps,
        subject=subject,
        body=body,
        draft_id=draft["draft_id"],
        created_at=draft["created_at"],
        source_mode=draft["source_mode"],
    )

    artifact = WorkflowArtifact(
        type="email_draft",
        title=subject,
        content=body,
        metadata={
            "draft_id": draft["draft_id"],
            "repo_full_name": github_data["repo_full_name"],
            "source_mode": draft["source_mode"],
            "to_email": advisor_email,
        },
    )
    summary = (
        f"Prepared advisor update draft with {len(progress_points)} progress points "
        f"for the week of {week_start_iso}."
    )

    result = workflow_result(
        workflow="advisor_update",
        summary=summary,
        artifacts=[artifact],
        errors=[],
        data={
            "week_start": week_start_iso,
            "project_name": project_name,
            "wakatime": wakatime_data,
            "github": github_data,
            "draft": draft_model.to_dict(),
        },
        generated_at=current_timestamp(),
    )
    append_record(WEEKLY_UPDATES_PATH, "updates", result)
    return result


def _build_progress_points(
    wakatime_data: dict[str, Any],
    github_data: dict[str, Any],
) -> list[str]:
    commit_messages = [item["message"] for item in github_data.get("commits", [])[:3]]
    total_hours = wakatime_data.get("total_hours", 0.0)
    return [
        (
            f"Captured {total_hours:.1f} hours of coding activity, with the strongest "
            f"focus areas around {', '.join(wakatime_data.get('themes', [])[:3])}."
        ),
        (
            f"Shaped backend workflow contracts and scaffolding through "
            f"{github_data.get('commit_count', 0)} tracked commits."
        ),
        (
            f"Notable code changes this week: {'; '.join(commit_messages) or 'no commit summary available'}."
        ),
    ]


def _render_advisor_email(
    project_name: str,
    week_start: str,
    progress_points: list[str],
    blockers: list[str],
    next_steps: list[str],
) -> str:
    lines = [
        f"Hi,",
        "",
        f"Here is my weekly update for {project_name} for the week of {week_start}.",
        "",
        "Progress this week:",
    ]
    lines.extend(f"- {point}" for point in progress_points)
    lines.append("")
    lines.append("Current blockers:")
    lines.extend(f"- {item}" for item in blockers)
    lines.append("")
    lines.append("Plan for next week:")
    lines.extend(f"- {item}" for item in next_steps)
    lines.append("")
    lines.append("Best,")
    lines.append("Arijit")
    return "\n".join(lines)
