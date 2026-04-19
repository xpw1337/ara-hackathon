import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from src.models import NormalizedDeadline, PlanItem
from src.workflows import deadline_guardian, week_planner


def _deadline(title: str, due_in_hours: int, dedupe_key: str, source: str = "Canvas") -> NormalizedDeadline:
    return NormalizedDeadline(
        title=title,
        source=source,
        due_at=datetime.now() + timedelta(hours=due_in_hours),
        url=f"https://example.com/{dedupe_key}",
        context="Course",
        importance="high",
        dedupe_key=dedupe_key,
    )


class DeadlineGuardianTests(unittest.TestCase):
    def test_deadline_guardian_returns_counts_and_persists_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "deadline_alerts.json"

            with patch.object(deadline_guardian, "STATE_FILE", str(state_path)):
                with patch("src.workflows.deadline_guardian.fetch_canvas_deadlines", return_value=[_deadline("HW", 24, "canvas-hw")]):
                    with patch("src.workflows.deadline_guardian.fetch_calendar_events", return_value=[_deadline("Meeting", 72, "cal-meeting", source="Calendar")]):
                        with patch("src.workflows.deadline_guardian.send_message", return_value=True):
                            result = deadline_guardian.run_deadline_guardian()

            self.assertTrue(result["ok"])
            self.assertEqual(result["data"]["urgent_count"], 1)
            self.assertEqual(result["data"]["sent_count"], 1)
            saved_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(saved_state["alerted_keys"], ["canvas-hw"])
            self.assertEqual(saved_state["runs"][-1]["data"]["urgent_count"], 1)


class WeekPlannerTests(unittest.TestCase):
    def test_week_planner_returns_plan_counts_and_persists_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "week_plan_history.json"
            todoist_items = [
                PlanItem(
                    title="Write intro",
                    priority=1,
                    why_now="High leverage",
                    due_at=None,
                    source_refs=["Todoist"],
                )
            ]
            canvas_deadlines = [_deadline("Project", 30, "canvas-project")]
            calendar_events = [_deadline("Advisor meeting", 40, "cal-advisor", source="Calendar")]

            with patch.object(week_planner, "STATE_FILE", str(state_path)):
                with patch("src.workflows.week_planner.fetch_todoist_tasks", return_value=todoist_items):
                    with patch("src.workflows.week_planner.fetch_canvas_deadlines", return_value=canvas_deadlines):
                        with patch("src.workflows.week_planner.fetch_calendar_events", return_value=calendar_events):
                            result = week_planner.run_week_planner()

            self.assertTrue(result["ok"])
            self.assertEqual(result["data"]["todoist_count"], 1)
            self.assertEqual(result["data"]["deadline_count"], 2)
            self.assertEqual(result["data"]["top_priority_count"], 3)
            saved_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(saved_state["plans"][-1]["data"]["total_items"], 3)


if __name__ == "__main__":
    unittest.main()
