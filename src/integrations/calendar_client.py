from __future__ import annotations

import json
import os
from datetime import datetime, time, timedelta, timezone
from typing import Any, List
from urllib import error, parse, request

from src.models import NormalizedDeadline


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
DEFAULT_KEYWORDS = [
    "advisor",
    "class",
    "deadline",
    "exam",
    "lab",
    "meeting",
    "paper",
    "project",
    "proposal",
    "research",
    "seminar",
    "thesis",
]


def fetch_calendar_events() -> List[NormalizedDeadline]:
    """
    Fetch upcoming events from Google Calendar.
    Filters to academic/highly relevant events.
    Falls back to mock data when Google credentials are not configured.
    """
    if os.environ.get("CALENDAR_USE_MOCK", "").lower() in {"1", "true", "yes"}:
        return _mock_events()

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN", "").strip()
    if not client_id or not client_secret or not refresh_token:
        legacy_token = os.environ.get("CALENDAR_API_KEY", "").strip()
        if not legacy_token:
            return _mock_events()
        raise RuntimeError(
            "Google Calendar now expects GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN."
        )

    return _fetch_live_events(client_id, client_secret, refresh_token)


def _fetch_live_events(client_id: str, client_secret: str, refresh_token: str) -> List[NormalizedDeadline]:
    access_token = _refresh_google_access_token(client_id, client_secret, refresh_token)
    calendar_ids = [
        item.strip()
        for item in os.environ.get("GOOGLE_CALENDAR_IDS", "primary").split(",")
        if item.strip()
    ] or ["primary"]
    keywords = [
        item.strip().lower()
        for item in os.environ.get("GOOGLE_CALENDAR_INCLUDE_KEYWORDS", ",".join(DEFAULT_KEYWORDS)).split(",")
        if item.strip()
    ]
    now = datetime.now(timezone.utc)
    time_max = now + timedelta(days=14)

    deadlines: list[NormalizedDeadline] = []
    for calendar_id in calendar_ids:
        params = parse.urlencode(
            {
                "singleEvents": "true",
                "orderBy": "startTime",
                "timeMin": now.isoformat().replace("+00:00", "Z"),
                "timeMax": time_max.isoformat().replace("+00:00", "Z"),
                "maxResults": "50",
            }
        )
        url = GOOGLE_EVENTS_URL.format(calendar_id=parse.quote(calendar_id, safe="")) + f"?{params}"
        req = request.Request(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, ValueError, error.URLError) as exc:
            raise RuntimeError(f"Google Calendar live fetch failed: {exc}") from exc

        calendar_label = payload.get("summary", calendar_id)
        for item in payload.get("items", []):
            if item.get("status") == "cancelled":
                continue
            if not _is_relevant_event(item, keywords):
                continue
            due_at = _parse_google_event_time(item)
            if due_at is None:
                continue
            deadlines.append(
                NormalizedDeadline(
                    title=item.get("summary") or "Untitled event",
                    source="Calendar",
                    due_at=due_at,
                    url=item.get("htmlLink", ""),
                    context=calendar_label,
                    importance=_importance_for_event(item, due_at),
                    dedupe_key=f"calendar:{calendar_id}:{item.get('id', '')}",
                )
            )
    return deadlines


def _refresh_google_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    body = parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    req = request.Request(
        GOOGLE_TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, error.URLError) as exc:
        raise RuntimeError(f"Google OAuth refresh failed: {exc}") from exc

    access_token = payload.get("access_token", "").strip()
    if not access_token:
        raise RuntimeError("Google OAuth refresh did not return an access token.")
    return access_token


def _is_relevant_event(item: dict[str, Any], keywords: list[str]) -> bool:
    summary = (item.get("summary") or "").lower()
    description = (item.get("description") or "").lower()
    text = f"{summary} {description}"
    return any(keyword in text for keyword in keywords)


def _parse_google_event_time(item: dict[str, Any]) -> datetime | None:
    start = item.get("start") or {}
    if start.get("dateTime"):
        return datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
    if start.get("date"):
        return datetime.combine(datetime.fromisoformat(start["date"]).date(), time(23, 59))
    return None


def _importance_for_event(item: dict[str, Any], due_at: datetime) -> str:
    text = f"{item.get('summary', '')} {item.get('description', '')}".lower()
    if any(keyword in text for keyword in ["deadline", "exam", "proposal", "thesis"]):
        return "high"
    hours_until_due = (due_at - datetime.now(due_at.tzinfo or timezone.utc)).total_seconds() / 3600
    if hours_until_due <= 72:
        return "high"
    return "medium"


def _mock_events() -> List[NormalizedDeadline]:
    now = datetime.now()
    return [
        NormalizedDeadline(
            title="Advisor Meeting: Thesis Review",
            source="Calendar",
            due_at=now + timedelta(days=2),
            url="https://calendar.google.com/event?eid=mock",
            context="Research",
            importance="high",
            dedupe_key="cal_advisor_meeting_1",
        )
    ]
