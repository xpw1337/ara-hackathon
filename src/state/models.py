from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class WorkLogEntry:
    week_start: str
    date: str
    source: str
    hours: float
    project: str
    summary: str
    commit_refs: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommitActivity:
    sha: str
    message: str
    author: str
    committed_at: str
    url: str
    repository: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowArtifact:
    type: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdvisorUpdateDraft:
    week_start: str
    repo: str
    progress_points: list[str]
    blockers: list[str]
    next_steps: list[str]
    subject: str
    body: str
    draft_id: str
    created_at: str
    source_mode: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def workflow_result(
    workflow: str,
    summary: str,
    artifacts: list[WorkflowArtifact],
    errors: list[str] | None = None,
    data: dict[str, Any] | None = None,
    ok: bool = True,
    generated_at: str = "",
) -> dict[str, Any]:
    return {
        "ok": ok,
        "workflow": workflow,
        "summary": summary,
        "artifacts": [artifact.to_dict() for artifact in artifacts],
        "errors": errors or [],
        "data": data or {},
        "generated_at": generated_at,
    }
