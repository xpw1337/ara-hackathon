import unittest
from datetime import datetime, timezone

from src.integrations import calendar_client, canvas_client, todoist_client


class TodoistClientTests(unittest.TestCase):
    def test_parse_due_datetime_returns_aware_datetime(self) -> None:
        due = todoist_client._parse_todoist_due({"datetime": "2026-04-21T15:30:00Z"})

        self.assertEqual(due, datetime(2026, 4, 21, 15, 30, tzinfo=timezone.utc))

    def test_parse_due_date_defaults_to_end_of_day(self) -> None:
        due = todoist_client._parse_todoist_due({"date": "2026-04-21"})

        self.assertEqual(due, datetime(2026, 4, 21, 23, 59))


class CanvasClientTests(unittest.TestCase):
    def test_parse_next_link_returns_next_page(self) -> None:
        header = '<https://canvas.example/api/v1/courses?page=2>; rel="next", <https://canvas.example/api/v1/courses?page=5>; rel="last"'

        self.assertEqual(
            canvas_client._parse_next_link(header),
            "https://canvas.example/api/v1/courses?page=2",
        )

    def test_parse_canvas_datetime_returns_aware_datetime(self) -> None:
        due_at = canvas_client._parse_canvas_datetime("2026-04-21T12:00:00Z")

        self.assertEqual(due_at, datetime(2026, 4, 21, 12, 0, tzinfo=timezone.utc))


class CalendarClientTests(unittest.TestCase):
    def test_parse_google_event_time_supports_datetime_and_date(self) -> None:
        timed = calendar_client._parse_google_event_time(
            {"start": {"dateTime": "2026-04-22T10:00:00Z"}}
        )
        all_day = calendar_client._parse_google_event_time(
            {"start": {"date": "2026-04-23"}}
        )

        self.assertEqual(timed, datetime(2026, 4, 22, 10, 0, tzinfo=timezone.utc))
        self.assertEqual(all_day, datetime(2026, 4, 23, 23, 59))

    def test_is_relevant_event_filters_non_academic_entries(self) -> None:
        self.assertTrue(
            calendar_client._is_relevant_event(
                {"summary": "Advisor Meeting", "description": ""},
                ["advisor", "deadline"],
            )
        )
        self.assertFalse(
            calendar_client._is_relevant_event(
                {"summary": "Dinner with friends", "description": ""},
                ["advisor", "deadline"],
            )
        )


if __name__ == "__main__":
    unittest.main()
