from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import ara_sdk as ara


DATA_DIR = Path("data")
STATE_PATH = DATA_DIR / "state.json"


@dataclass
class Task:
    title: str
    due: str = ""
    importance: int = 3
    status: str = "open"
    created_at: str = ""


def _ensure_state() -> dict[str, Any]:
    DATA_DIR.mkdir(exist_ok=True)
    if not STATE_PATH.exists():
        initial = {"notes": [], "tasks": []}
        STATE_PATH.write_text(json.dumps(initial, indent=2), encoding="utf-8")
        return initial
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict[str, Any]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _score_task(task: dict[str, Any]) -> int:
    score = int(task.get("importance", 3))
    due = task.get("due", "").strip()
    if due:
        try:
            due_date = datetime.fromisoformat(due)
            delta_hours = (due_date - datetime.now()).total_seconds() / 3600
            if delta_hours < 0:
                score += 5
            elif delta_hours < 24:
                score += 3
            elif delta_hours < 72:
                score += 1
        except ValueError:
            score += 0
    return score


@ara.tool
def save_note(note: str, source: str = "manual") -> dict[str, Any]:
    state = _ensure_state()
    entry = {
        "note": note.strip(),
        "source": source,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    state["notes"].append(entry)
    _save_state(state)
    return {"saved": True, "note_count": len(state["notes"]), "entry": entry}


@ara.tool
def add_task(title: str, due: str = "", importance: int = 3) -> dict[str, Any]:
    state = _ensure_state()
    task = Task(
        title=title.strip(),
        due=due.strip(),
        importance=max(1, min(5, int(importance))),
        created_at=datetime.now().isoformat(timespec="seconds"),
    )
    state["tasks"].append(asdict(task))
    _save_state(state)
    return {"saved": True, "task": asdict(task), "task_count": len(state["tasks"])}


@ara.tool
def complete_task(title: str) -> dict[str, Any]:
    state = _ensure_state()
    for task in state["tasks"]:
        if task["title"].lower() == title.strip().lower():
            task["status"] = "done"
            _save_state(state)
            return {"updated": True, "task": task}
    return {"updated": False, "reason": "task not found"}


@ara.tool
def get_dashboard() -> dict[str, Any]:
    state = _ensure_state()
    open_tasks = [task for task in state["tasks"] if task.get("status") != "done"]
    ranked_tasks = sorted(open_tasks, key=_score_task, reverse=True)
    next_action = ranked_tasks[0]["title"] if ranked_tasks else "No open tasks yet."
    risks = [
        task
        for task in ranked_tasks
        if task.get("due") and _score_task(task) >= 6
    ][:3]
    recent_notes = state["notes"][-5:]
    return {
        "summary": {
            "open_tasks": len(open_tasks),
            "saved_notes": len(state["notes"]),
            "next_best_action": next_action,
        },
        "top_tasks": ranked_tasks[:5],
        "risks": risks,
        "recent_notes": recent_notes,
    }


@ara.tool
def seed_demo_context() -> dict[str, Any]:
    state = {
        "notes": [
            {
                "note": "Hackathon demo is at 5 PM. Need clear pitch and polished slides.",
                "source": "demo",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            },
            {
                "note": "Need to message teammate about final UI screenshots.",
                "source": "demo",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            },
        ],
        "tasks": [
            asdict(
                Task(
                    title="Finish demo slides",
                    due="2026-04-19T16:30:00",
                    importance=5,
                    created_at=datetime.now().isoformat(timespec="seconds"),
                )
            ),
            asdict(
                Task(
                    title="Text teammate for screenshots",
                    due="2026-04-19T15:30:00",
                    importance=4,
                    created_at=datetime.now().isoformat(timespec="seconds"),
                )
            ),
            asdict(
                Task(
                    title="Practice 60-second pitch",
                    due="2026-04-19T16:45:00",
                    importance=5,
                    created_at=datetime.now().isoformat(timespec="seconds"),
                )
            ),
        ],
    }
    _save_state(state)
    return {"seeded": True, "state": state}


ara.Automation(
    "parallel-you",
    system_instructions=(
        "You are Parallel You, an AI personal computer that behaves like a calm, "
        "proactive chief of staff. Use the available tools to save notes, track tasks, "
        "and inspect the dashboard before giving advice. When you respond, prioritize: "
        "1) the single next best action, 2) the main risk if the user does nothing, "
        "and 3) one concrete draft message or checklist. Be concise, practical, and "
        "decisive. If connector tools are available, you may suggest actions that could "
        "be automated later, but do not pretend an external action happened unless a tool "
        "actually ran."
    ),
    tools=[save_note, add_task, complete_task, get_dashboard, seed_demo_context],
)
