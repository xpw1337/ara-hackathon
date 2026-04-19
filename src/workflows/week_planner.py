import json
import os

from src.integrations.calendar_client import fetch_calendar_events
from src.integrations.canvas_client import fetch_canvas_deadlines
from src.integrations.todoist_client import fetch_todoist_tasks
from src.models import PlanItem
from src.state.store import current_timestamp


STATE_FILE = "data/week_plan_history.json"


def load_plan_history() -> list[dict]:
    if not os.path.exists(STATE_FILE):
        return []

    with open(STATE_FILE, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return payload

    return payload.get("plans", [])


def save_plan_history(plan_details: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    history = load_plan_history()
    history.append(plan_details)
    with open(STATE_FILE, "w", encoding="utf-8") as handle:
        json.dump({"plans": history[-10:]}, handle, indent=2)


def _serialize_plan_item(item: PlanItem) -> dict:
    return {
        "title": item.title,
        "priority": item.priority,
        "why_now": item.why_now,
        "due_at": item.due_at.isoformat() if item.due_at else None,
        "source_refs": item.source_refs,
    }


def run_week_planner() -> dict:
    """
    Scans for the week's tasks across Canvas, Calendar, and Todoist.
    Ranks them into a Sunday planner.
    """
    try:
        todoist_tasks = fetch_todoist_tasks()
        canvas_deadlines = fetch_canvas_deadlines()
        cal_events = fetch_calendar_events()

        plan_items = list(todoist_tasks)
        for deadline in canvas_deadlines:
            plan_items.append(
                PlanItem(
                    title=f"[Canvas] {deadline.title}",
                    priority=1 if deadline.importance == "high" else 2,
                    why_now="Academic Deadline",
                    due_at=deadline.due_at,
                    source_refs=["Canvas", deadline.url],
                )
            )

        for event in cal_events:
            plan_items.append(
                PlanItem(
                    title=f"[Cal] {event.title}",
                    priority=1 if event.importance == "high" else 3,
                    why_now="Scheduled Academic Event",
                    due_at=event.due_at,
                    source_refs=["Calendar", event.url],
                )
            )

        def sort_key(item: PlanItem):
            due = item.due_at.timestamp() if item.due_at else float("inf")
            return (item.priority, due)

        plan_items.sort(key=sort_key)
        generated_at = current_timestamp()
        top_priorities = plan_items[:3]
        overloaded_day = next(
            (item.due_at.date().isoformat() for item in plan_items if item.due_at is not None),
            None,
        )

        artifacts = [
            {
                "timestamp": generated_at,
                "items": [_serialize_plan_item(item) for item in plan_items],
            }
        ]
        result = {
            "ok": True,
            "workflow": "week_planner",
            "summary": f"Generated weekly plan with {len(plan_items)} total items aligned.",
            "artifacts": artifacts,
            "errors": [],
            "data": {
                "total_items": len(plan_items),
                "todoist_count": len(todoist_tasks),
                "deadline_count": len(canvas_deadlines) + len(cal_events),
                "top_priority_count": len(top_priorities),
                "top_priorities": [item.title for item in top_priorities],
                "overloaded_day": overloaded_day,
            },
            "generated_at": generated_at,
        }
        save_plan_history(result)
        return result
    except Exception as exc:
        return {
            "ok": False,
            "workflow": "week_planner",
            "summary": "Failed to run week planner.",
            "artifacts": [],
            "errors": [str(exc)],
            "data": {
                "total_items": 0,
                "todoist_count": 0,
                "deadline_count": 0,
                "top_priority_count": 0,
                "top_priorities": [],
                "overloaded_day": None,
            },
            "generated_at": current_timestamp(),
        }


if __name__ == "__main__":
    import pprint

    pprint.pprint(run_week_planner())
