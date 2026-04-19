import json
import os
from datetime import datetime, timedelta

from src.integrations.calendar_client import fetch_calendar_events
from src.integrations.canvas_client import fetch_canvas_deadlines
from src.integrations.delivery import send_message
from src.models import DeliveryPayload
from src.state.store import current_timestamp


STATE_FILE = "data/deadline_alerts.json"


def load_alert_state() -> tuple[set[str], list[dict]]:
    if not os.path.exists(STATE_FILE):
        return set(), []

    with open(STATE_FILE, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return set(payload), []

    return set(payload.get("alerted_keys", [])), payload.get("runs", [])


def save_alert_state(history: set[str], runs: list[dict]) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    payload = {
        "alerted_keys": sorted(history),
        "runs": runs[-10:],
    }
    with open(STATE_FILE, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _serialize_deadline(deadline) -> dict:
    return {
        "title": deadline.title,
        "source": deadline.source,
        "due_at": deadline.due_at.isoformat(),
        "url": deadline.url,
        "context": deadline.context,
        "importance": deadline.importance,
        "dedupe_key": deadline.dedupe_key,
    }


def _is_within_alert_window(due_at: datetime, window_hours: int = 48) -> bool:
    current = datetime.now(due_at.tzinfo) if due_at.tzinfo else datetime.now()
    threshold = current + timedelta(hours=window_hours)
    return current <= due_at <= threshold


def run_deadline_guardian() -> dict:
    """
    Workflow to check for 48-hour deadline risks, deduplicate them,
    and trigger alerts via the delivery channel.
    """
    try:
        canvas_deadlines = fetch_canvas_deadlines()
        cal_events = fetch_calendar_events()
        merged = list({d.dedupe_key: d for d in canvas_deadlines + cal_events}.values())

        urgent = [
            deadline for deadline in merged if _is_within_alert_window(deadline.due_at)
        ]

        alerted_keys, prior_runs = load_alert_state()
        new_alerts = [deadline for deadline in urgent if deadline.dedupe_key not in alerted_keys]
        generated_at = current_timestamp()

        data = {
            "checked_count": len(merged),
            "urgent_count": len(urgent),
            "new_alert_count": len(new_alerts),
            "sent_count": 0,
            "sources": {
                "canvas_count": len(canvas_deadlines),
                "calendar_count": len(cal_events),
            },
        }

        if not new_alerts:
            result = {
                "ok": True,
                "workflow": "deadline_guardian",
                "summary": f"No new urgent deadlines. Checked {len(merged)} total items.",
                "artifacts": [
                    {
                        "urgent_deadlines": [_serialize_deadline(deadline) for deadline in urgent],
                    }
                ],
                "errors": [],
                "data": data,
                "generated_at": generated_at,
            }
            save_alert_state(alerted_keys, prior_runs + [result])
            return result

        sent_count = 0
        for alert in new_alerts:
            payload = DeliveryPayload(
                channel=os.environ.get("DELIVERY_CHANNEL", "mock"),
                title=f"URGENT DEADLINE: {alert.title}",
                body=f"Source: {alert.source}\nDue At: {alert.due_at}\nLink: {alert.url}",
                dedupe_key=alert.dedupe_key,
            )
            if send_message(payload):
                alerted_keys.add(alert.dedupe_key)
                sent_count += 1

        data["sent_count"] = sent_count
        result = {
            "ok": True,
            "workflow": "deadline_guardian",
            "summary": f"Sent {sent_count} urgent reminders.",
            "artifacts": [
                {
                    "urgent_deadlines": [_serialize_deadline(deadline) for deadline in urgent],
                    "new_alerts": [_serialize_deadline(deadline) for deadline in new_alerts],
                    "sent_dedupe_keys": sorted(alerted_keys),
                }
            ],
            "errors": [],
            "data": data,
            "generated_at": generated_at,
        }
        save_alert_state(alerted_keys, prior_runs + [result])
        return result
    except Exception as exc:
        return {
            "ok": False,
            "workflow": "deadline_guardian",
            "summary": "Failed to run deadline guardian.",
            "artifacts": [],
            "errors": [str(exc)],
            "data": {
                "checked_count": 0,
                "urgent_count": 0,
                "new_alert_count": 0,
                "sent_count": 0,
                "sources": {
                    "canvas_count": 0,
                    "calendar_count": 0,
                },
            },
            "generated_at": current_timestamp(),
        }


if __name__ == "__main__":
    import pprint

    pprint.pprint(run_deadline_guardian())
