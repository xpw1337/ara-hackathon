import os
import json
from datetime import datetime
from src.integrations.canvas_client import fetch_canvas_deadlines
from src.integrations.calendar_client import fetch_calendar_events
from src.integrations.todoist_client import fetch_todoist_tasks
from src.models import PlanItem
import dataclasses

STATE_FILE = "data/week_plan_history.json"

def save_plan_history(plan_details: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    history = []
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            history = json.load(f)
    history.append(plan_details)
    with open(STATE_FILE, "w") as f:
        json.dump(history, f)

def run_week_planner() -> dict:
    """
    Scans for the week's tasks across Canvas, Calendar, and Todoist.
    Ranks them into a Sunday planner.
    """
    try:
        # Fetch data
        todoist_tasks = fetch_todoist_tasks()
        canvas_deadlines = fetch_canvas_deadlines()
        cal_events = fetch_calendar_events()
        
        # Convert deadlines to PlanItems
        plan_items = list(todoist_tasks)
        for d in canvas_deadlines:
            plan_items.append(PlanItem(
                title=f"[Canvas] {d.title}",
                priority=1 if d.importance == "high" else 2,
                why_now=f"Academic Deadline",
                due_at=d.due_at,
                source_refs=["Canvas", d.url]
            ))
            
        for e in cal_events:
            plan_items.append(PlanItem(
                title=f"[Cal] {e.title}",
                priority=1 if e.importance == "high" else 3,
                why_now="Scheduled Academic Event",
                due_at=e.due_at,
                source_refs=["Calendar", e.url]
            ))
            
        # Sort items by priority, then by due date
        # due_at can be None for Todoist, so sort gracefully
        def sort_key(item: PlanItem):
            due = item.due_at.timestamp() if item.due_at else float('inf')
            return (item.priority, due)
            
        plan_items.sort(key=sort_key)
        
        # Format the output artifact
        artifacts = [{
            "timestamp": datetime.now().isoformat(),
            "items": [
                {
                    "title": item.title,
                    "priority": item.priority,
                    "due_at": item.due_at.isoformat() if item.due_at else None,
                    "source_refs": item.source_refs
                } for item in plan_items
            ]
        }]
        
        save_plan_history(artifacts[0])
        
        return {
            "ok": True,
            "workflow": "week_planner",
            "summary": f"Generated weekly plan with {len(plan_items)} total items aligned.",
            "artifacts": artifacts,
            "errors": []
        }
    except Exception as e:
        return {
            "ok": False,
            "workflow": "week_planner",
            "summary": "Failed to run week planner.",
            "artifacts": [],
            "errors": [str(e)]
        }

if __name__ == "__main__":
    import pprint
    pprint.pprint(run_week_planner())
