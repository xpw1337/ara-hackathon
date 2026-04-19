from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any
from urllib import error, parse, request

from src.state.models import CommitActivity
from src.state.store import current_timestamp, resolve_week_window


def get_weekly_commits(
    repo_full_name: str = "",
    week_start: str = "",
    use_mock: bool = True,
) -> dict[str, Any]:
    start_date, end_date = resolve_week_window(week_start)
    repo_full_name = repo_full_name.strip() or os.getenv(
        "GITHUB_REPO_FULL_NAME",
        "arijit/pitch-tipping",
    )

    if use_mock:
        return _mock_weekly_commits(repo_full_name, start_date.isoformat())

    try:
        return _fetch_live_commits(
            repo_full_name=repo_full_name,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
    except (OSError, ValueError, error.URLError) as exc:
        fallback = _mock_weekly_commits(repo_full_name, start_date.isoformat())
        fallback["warnings"].append(f"Live GitHub fetch failed: {exc}")
        return fallback


def _fetch_live_commits(
    repo_full_name: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    query = parse.urlencode(
        {
            "since": f"{start_date}T00:00:00Z",
            "until": f"{end_date}T23:59:59Z",
            "per_page": "50",
        }
    )
    url = f"https://api.github.com/repos/{repo_full_name}/commits?{query}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "grad-student-survival-agent",
    }
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(url, headers=headers)
    with request.urlopen(req, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    commits: list[dict[str, Any]] = []
    for item in payload:
        commit_data = item.get("commit", {})
        author_data = commit_data.get("author", {})
        commits.append(
            CommitActivity(
                sha=item.get("sha", "")[:7],
                message=(commit_data.get("message", "").splitlines() or [""])[0],
                author=author_data.get("name", "unknown"),
                committed_at=author_data.get("date", ""),
                url=item.get("html_url", ""),
                repository=repo_full_name,
            ).to_dict()
        )

    return {
        "source_mode": "live",
        "repo_full_name": repo_full_name,
        "week_start": start_date,
        "week_end": end_date,
        "commit_count": len(commits),
        "commits": commits,
        "warnings": [],
        "generated_at": current_timestamp(),
    }


def _mock_weekly_commits(repo_full_name: str, week_start: str) -> dict[str, Any]:
    commits = [
        CommitActivity(
            sha="2f8a4d1",
            message="Add workflow result contract for advisor update",
            author="Arijit",
            committed_at=f"{week_start}T13:10:00",
            url="https://github.com/example/example/commit/2f8a4d1",
            repository=repo_full_name,
        ).to_dict(),
        CommitActivity(
            sha="71d2c08",
            message="Normalize WakaTime activity into weekly summary records",
            author="Arijit",
            committed_at=f"{week_start}T18:45:00",
            url="https://github.com/example/example/commit/71d2c08",
            repository=repo_full_name,
        ).to_dict(),
        CommitActivity(
            sha="91e14bc",
            message="Scaffold Ara workflow entrypoints for research log generation",
            author="Arijit",
            committed_at=f"{week_start}T20:05:00",
            url="https://github.com/example/example/commit/91e14bc",
            repository=repo_full_name,
        ).to_dict(),
    ]
    return {
        "source_mode": "mock",
        "repo_full_name": repo_full_name,
        "week_start": week_start,
        "week_end": week_start,
        "commit_count": len(commits),
        "commits": commits,
        "warnings": [],
        "generated_at": current_timestamp(),
    }
