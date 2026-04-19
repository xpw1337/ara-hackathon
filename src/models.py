from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

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
