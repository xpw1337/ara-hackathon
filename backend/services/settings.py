from __future__ import annotations

from pathlib import Path
from typing import Any

from src.state.store import load_json, save_json

SETTINGS_PATH = Path("data") / "settings.json"

DEFAULT_SETTINGS: dict[str, Any] = {
    "keywords": "machine learning, neural networks, transformers",
    "repoName": "pitch-tipping",
    "projectName": "pitch-tipping",
    "advisorEmail": "",
    "deliveryChannel": "telegram",
    "writeDestination": "local",
    "canvasUrl": "",
    "canvasConnected": False,
    "useMock": True,
}


def get_settings() -> dict[str, Any]:
    return load_json(SETTINGS_PATH, DEFAULT_SETTINGS)


def update_settings(patch: dict[str, Any]) -> dict[str, Any]:
    current = get_settings()
    current.update({k: v for k, v in patch.items() if k in DEFAULT_SETTINGS})
    save_json(SETTINGS_PATH, current)
    return current
