import os
from datetime import datetime, timedelta
from typing import List
from src.models import NormalizedDeadline

def fetch_canvas_deadlines() -> List[NormalizedDeadline]:
    """
    Fetch upcoming deadlines from Canvas. 
    Falls back to mock data if CANVAS_API_KEY is not present.
    """
    api_key = os.environ.get("CANVAS_API_KEY")
    if not api_key:
        # Mock mode
        now = datetime.now()
        return [
            NormalizedDeadline(
                title="CS500: Distributed Systems Project 1",
                source="Canvas",
                due_at=now + timedelta(days=1, hours=5),
                url="https://canvas.example.edu/courses/1/assignments/1",
                context="CS500",
                importance="high",
                dedupe_key="canvas_cs500_p1"
            ),
            NormalizedDeadline(
                title="CS500: Weekly Quiz",
                source="Canvas",
                due_at=now + timedelta(days=4),
                url="https://canvas.example.edu/courses/1/assignments/2",
                context="CS500",
                importance="medium",
                dedupe_key="canvas_cs500_quiz2"
            )
        ]
    
    # Live integration placeholder
    # TODO: implement real Canvas API call here
    return []
