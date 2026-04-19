from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable


class PapersSeenStore:
    def __init__(self, path: str = "data/papers_seen.json") -> None:
        self.path = Path(path)

    def load_seen_ids(self) -> set[str]:
        if not self.path.exists():
            return set()

        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return {str(item) for item in payload}

        seen_ids = payload.get("seen_ids", [])
        return {str(item) for item in seen_ids}

    def has_seen(self, paper_id: str) -> bool:
        return paper_id in self.load_seen_ids()

    def mark_seen(self, paper_ids: Iterable[str]) -> list[str]:
        seen_ids = self.load_seen_ids()
        seen_ids.update(str(paper_id) for paper_id in paper_ids)
        self._save_seen_ids(seen_ids)
        return sorted(seen_ids)

    def _save_seen_ids(self, seen_ids: set[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "seen_ids": sorted(seen_ids),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
