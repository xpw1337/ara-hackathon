from __future__ import annotations

from typing import Any

from src.state.store import append_record, current_timestamp, DRAFT_ARCHIVE_PATH


def create_gmail_draft(
    subject: str,
    body: str,
    to_email: str = "",
    use_mock: bool = True,
) -> dict[str, Any]:
    """
    Mock-first Gmail draft creation.

    Live Gmail draft creation is intentionally not faked here. Until OAuth flow
    support is added, the workflow persists a local draft artifact that the UI
    can preview safely.
    """
    draft_id = f"mock-draft-{current_timestamp().replace(':', '').replace('-', '')}"
    record = {
        "draft_id": draft_id,
        "subject": subject,
        "body": body,
        "to_email": to_email,
        "source_mode": "mock" if use_mock else "mock-fallback",
        "created_at": current_timestamp(),
    }
    append_record(DRAFT_ARCHIVE_PATH, "drafts", record, dedupe_key=None)
    return {
        "ok": True,
        "draft_id": draft_id,
        "subject": subject,
        "to_email": to_email,
        "source_mode": record["source_mode"],
        "created_at": record["created_at"],
        "warnings": []
        if use_mock
        else ["Live Gmail draft creation is not implemented yet; saved mock draft."],
    }
