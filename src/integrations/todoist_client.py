import os
from datetime import datetime, timedelta
from typing import List
from src.models import PlanItem

def fetch_todoist_tasks() -> List[PlanItem]:
    """
    Fetch outstanding tasks from Todoist.
    Falls back to mock data if TODOIST_API_KEY is not present.
    """
    api_key = os.environ.get("TODOIST_API_KEY")
    if not api_key:
        # Mock mode
        now = datetime.now()
        return [
            PlanItem(
                title="Read paper regarding Paxos consensus",
                priority=1,
                why_now="Foundational for upcoming project",
                due_at=now + timedelta(days=3),
                source_refs=["Todoist"]
            ),
            PlanItem(
                title="Draft intro for thesis proposal",
                priority=2,
                why_now="Due end of month",
                due_at=None,
                source_refs=["Todoist"]
            )
        ]
    
    # Live integration placeholder
    # TODO: implement real Todoist API call
    return []
