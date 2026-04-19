import os
from datetime import datetime, timedelta
from typing import List
from src.models import NormalizedDeadline

def fetch_calendar_events() -> List[NormalizedDeadline]:
    """
    Fetch upcoming events from Google Calendar.
    Filters to academic/highly relevant events.
    Falls back to mock data if CALENDAR_API_KEY is missing.
    """
    api_key = os.environ.get("CALENDAR_API_KEY")
    if not api_key:
        # Mock mode
        now = datetime.now()
        return [
            NormalizedDeadline(
                title="Advisor Meeting: Thesis Review",
                source="Calendar",
                due_at=now + timedelta(days=2),
                url="https://calendar.google.com/event?eid=mock",
                context="Research",
                importance="high",
                dedupe_key="cal_advisor_meeting_1"
            )
        ]
    
    # Live integration placeholder
    # TODO: implement real Google Calendar API call here
    return []
