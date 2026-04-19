from __future__ import annotations

import json
import os
from urllib import error, parse, request

from src.models import DeliveryPayload


def send_message(payload: DeliveryPayload) -> bool:
    """
    Send a message via the configured delivery channel.
    Falls back to stdout only when explicitly configured for mock delivery.
    """
    channel = payload.channel or os.environ.get("DELIVERY_CHANNEL", "mock")

    if channel == "mock":
        print(f"--- MOCK DELIVERY: {payload.title} ---")
        print(f"Channel: {channel}")
        print(f"Body: {payload.body}")
        print(f"Dedupe Key: {payload.dedupe_key}")
        print("---------------------------")
        return True

    if channel == "telegram":
        return _send_telegram_message(payload)
    if channel == "slack":
        return _send_slack_message(payload)
    if channel == "email":
        return False
    return False


def _send_telegram_message(payload: DeliveryPayload) -> bool:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not bot_token or not chat_id:
        raise RuntimeError("Telegram delivery requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")

    message_text = f"{payload.title}\n\n{payload.body}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    body = parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message_text,
        }
    ).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, error.URLError) as exc:
        raise RuntimeError(f"Telegram delivery failed: {exc}") from exc

    return bool(payload.get("ok", False))


def _send_slack_message(payload: DeliveryPayload) -> bool:
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not webhook_url:
        raise RuntimeError("Slack delivery requires SLACK_WEBHOOK_URL.")

    body = json.dumps({"text": f"{payload.title}\n\n{payload.body}"}).encode("utf-8")
    req = request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            return 200 <= response.status < 300
    except (OSError, ValueError, error.URLError) as exc:
        raise RuntimeError(f"Slack delivery failed: {exc}") from exc
