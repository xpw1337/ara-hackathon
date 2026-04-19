from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class NormalizedDeadline:
    title: str
    source: str
    due_at: datetime
    url: str
    context: str
    importance: str
    dedupe_key: str

@dataclass
class PlanItem:
    title: str
    priority: int
    why_now: str
    due_at: Optional[datetime]
    source_refs: List[str]

@dataclass
class DeliveryPayload:
    channel: str
    title: str
    body: str
    dedupe_key: str


@dataclass
class PaperCandidate:
    paper_id: str
    title: str
    authors: List[str]
    url: str
    published_at: datetime
    keywords_matched: List[str]
    score: float
    reason: str
    summary: str
