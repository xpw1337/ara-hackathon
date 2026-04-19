import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from src.models import PaperCandidate
from src.workflows.paper_scout import DEFAULT_KEYWORDS, run_paper_scout


def _candidate(paper_id: str, title: str, score: float) -> PaperCandidate:
    return PaperCandidate(
        paper_id=paper_id,
        title=title,
        authors=["Test Author"],
        url=f"https://arxiv.org/abs/{paper_id}",
        published_at=datetime(2024, 4, 1, tzinfo=timezone.utc),
        keywords_matched=["hci"],
        score=score,
        reason="Matches hci; published 2024-04-01.",
        summary="Test summary",
    )


class PaperScoutWorkflowTests(unittest.TestCase):
    def test_run_paper_scout_filters_seen_and_writes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            state_path = temp_path / "papers_seen.json"
            reading_list_path = temp_path / "reading_list.md"
            state_path.write_text(
                json.dumps({"seen_ids": ["paper-1"], "updated_at": "2026-04-19T12:00:00"}),
                encoding="utf-8",
            )

            candidates = [
                _candidate("paper-1", "Seen Paper", 9.5),
                _candidate("paper-2", "Fresh Paper A", 9.0),
                _candidate("paper-3", "Fresh Paper B", 8.5),
                _candidate("paper-4", "Fresh Paper C", 8.0),
            ]

            with patch("src.workflows.paper_scout.fetch_paper_candidates", return_value=candidates):
                result = run_paper_scout(
                    keywords=["hci", "behavior modeling"],
                    state_path=str(state_path),
                    reading_list_path=str(reading_list_path),
                )

            self.assertTrue(result["ok"])
            self.assertEqual(result["workflow"], "paper_scout")
            self.assertEqual(len(result["artifacts"][0]["recommendations"]), 3)
            self.assertTrue(reading_list_path.exists())
            markdown = reading_list_path.read_text(encoding="utf-8")
            self.assertIn("Fresh Paper A", markdown)
            self.assertNotIn("Seen Paper", markdown)

            saved_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(
                saved_state["seen_ids"],
                ["paper-1", "paper-2", "paper-3", "paper-4"],
            )

    def test_run_paper_scout_uses_default_keywords(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            state_path = temp_path / "papers_seen.json"
            reading_list_path = temp_path / "reading_list.md"
            candidates = [_candidate("paper-2", "Fresh Paper A", 9.0)]

            with patch("src.workflows.paper_scout.fetch_paper_candidates", return_value=candidates) as fetch_mock:
                result = run_paper_scout(
                    state_path=str(state_path),
                    reading_list_path=str(reading_list_path),
                )

            self.assertTrue(result["ok"])
            self.assertEqual(fetch_mock.call_args.args[0], DEFAULT_KEYWORDS)


if __name__ == "__main__":
    unittest.main()
