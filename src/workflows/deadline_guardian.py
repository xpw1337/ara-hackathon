import os
import json
from datetime import datetime, timedelta
from src.integrations.canvas_client import fetch_canvas_deadlines
from src.integrations.calendar_client import fetch_calendar_events
from src.integrations.delivery import send_message
from src.models import DeliveryPayload

STATE_FILE = "data/deadline_alerts.json"

def load_alert_history() -> set:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_alert_history(history: set):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(list(history), f)

def run_deadline_guardian() -> dict:
    """
    Workflow to check for 48-hour deadline risks, deduplicate them,
    and trigger alerts via the delivery channel.
    """
    try:
        # 1. Fetch from sources
        canvas_deadlines = fetch_canvas_deadlines()
        cal_events = fetch_calendar_events()
        
        # 2. Merge deadlines
        merged = {d.dedupe_key: d for d in canvas_deadlines + cal_events}.values()
        
        # 3. Filter for < 48 hours
        now = datetime.now()
        threshold = now + timedelta(hours=48)
        urgent = [d for d in merged if now <= d.due_at <= threshold]
        
        # 4. Deduplicate using state
        alerted_keys = load_alert_history()
        new_alerts = [d for d in urgent if d.dedupe_key not in alerted_keys]
        
        if not new_alerts:
            return {
                "ok": True,
                "workflow": "deadline_guardian",
                "summary": f"No new urgent deadlines. Checked {len(merged)} total items.",
                "artifacts": [],
                "errors": []
            }
        
        # 5. Send alerts and record state
        sent_count = 0
        for alert in new_alerts:
            payload = DeliveryPayload(
                channel="mock", 
                title=f"URGENT DEADLINE: {alert.title}",
                body=f"Source: {alert.source}\nDue At: {alert.due_at}\nLink: {alert.url}",
                dedupe_key=alert.dedupe_key
            )
            success = send_message(payload)
            if success:
                alerted_keys.add(alert.dedupe_key)
                sent_count += 1
        
        save_alert_history(alerted_keys)
        
        return {
            "ok": True,
            "workflow": "deadline_guardian",
            "summary": f"Sent {sent_count} urgent reminders.",
            "artifacts": [{"sent_dedupe_keys": list(alerted_keys)}],
            "errors": []
        }
    except Exception as e:
        return {
            "ok": False,
            "workflow": "deadline_guardian",
            "summary": "Failed to run deadline guardian.",
            "artifacts": [],
            "errors": [str(e)]
        }

if __name__ == "__main__":
    import pprint
    pprint.pprint(run_deadline_guardian())
