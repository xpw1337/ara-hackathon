# How We Use Ara

**Ara is the AI agent runtime that orchestrates our backend.** Our project isn't just a Flask/FastAPI CRUD app — it's a set of **autonomous workflows** that an AI agent can reason about and execute.

## The architecture in one sentence

We define **tools** that the Ara agent can call, wrap them in an **Automation**, and Ara's runtime handles scheduling, orchestration, and intelligent decision-making about when and how to run them.

## Concretely, in `app.py`

```python
@ara.tool
def run_research_log_workflow(...):
    """Generate a weekly research log from coding activity."""
    return run_research_log(...)

@ara.tool
def run_advisor_update_workflow(...):
    """Draft a weekly advisor update using GitHub and WakaTime progress."""
    return run_advisor_update(...)

# ... 5 tools total

ara.Automation(
    "grad-student-survival-agent",
    system_instructions="You are the Grad Student Survival Agent...",
    tools=[get_dashboard, run_research_log_workflow, ...],
)
```

## What each piece does

1. **`@ara.tool`** — Registers a Python function as a tool the AI agent can invoke. Each tool has a name, typed parameters, and a docstring the agent uses to understand when to call it. We have 6 tools: dashboard, research log, advisor update, paper scout, deadline guardian, and week planner.

2. **`ara.Automation("grad-student-survival-agent", ...)`** — Declares the agent itself. It bundles the tools with system instructions that tell the agent its role: "prefer workflow tools over ad-hoc reasoning, return structured outputs, distinguish live data from mocked fallback data."

3. **The Ara runtime** — When deployed, Ara hosts this automation as a persistent agent that can be triggered on a schedule (e.g., every Sunday for the week planner, every Friday for the advisor update) or on-demand. The runtime handles authentication, secret management (`ara.secret`), environment variables (`ara.env`), and agent-to-agent communication.

## Why Ara instead of just a REST API

- **Agent intelligence** — The Ara agent can chain tools together. Ask it "prepare my weekly update" and it can decide to run the research log first, then use that output to draft the advisor email — without us hardcoding that sequence.
- **Structured tool outputs** — Every workflow returns a standard `{ok, workflow, summary, artifacts, errors, data}` contract. The agent can inspect these results, handle errors, and retry.
- **Deployment as a service** — `app.py` is the single entrypoint. Push it to Ara's platform and it becomes a live agent with scheduling, logging, and secret management built in.

## The local dev adapter

For hackathon development and demo, we built a thin FastAPI adapter (`backend/server.py`) that exposes the same tools as HTTP endpoints so the React frontend can call them. In production, the frontend would talk to Ara's hosted API directly.

## A week in the life: how a grad student actually uses this

Meet Arijit. He's a CS grad student at JHU working on a research project called "pitch-tipping." He has an advisor meeting every Friday, three classes with Canvas deadlines, a Todoist full of tasks, and a stack of papers he never gets around to reading. Here's how the Grad Student Survival Agent handles his week:

### Sunday evening — Week Planner

The agent runs **`run_week_planner_workflow`**. It pulls tasks from Todoist, upcoming assignments from Canvas, and events from Google Calendar. It merges everything, sorts by priority and due date, and produces a ranked plan:

> 1. [Canvas] CS500: Distributed Systems Project 1 — due Tuesday
> 2. [Cal] Advisor Meeting: Thesis Review — Thursday
> 3. Read paper on Paxos consensus — from Todoist

Arijit opens the dashboard on Sunday night and sees his whole week laid out. No more checking three apps to figure out what's due.

### Monday through Thursday — Research Log

Every day, WakaTime silently tracks how long Arijit codes and which files he touches. GitHub tracks his commits. On Thursday, the agent runs **`run_research_log_workflow`**. It pulls WakaTime activity and GitHub commits, and generates a structured research log:

> Weekly Research Log — Week of Apr 13
> - Coding hours: 14.5h
> - Main themes: model training, evaluation, backend scaffolding
> - Key commits: "Add pitch classifier v2", "Fix eval metrics bug", "Scaffold API endpoints"

This log goes into his records — no more trying to remember what he did all week.

### Thursday night — Deadline Guardian

The agent runs **`run_deadline_guardian_workflow`**. It scans Canvas and Google Calendar for anything due within 48 hours and fires off alerts:

> URGENT: CS500 Weekly Quiz — due Friday 11:59 PM
> URGENT: Proposal draft — due Saturday 5 PM

It deduplicates so he doesn't get the same alert twice. If Telegram is configured, it sends a push notification to his phone.

### Friday morning — Advisor Update

Before his advisor meeting, the agent runs **`run_advisor_update_workflow`**. It combines the WakaTime hours and GitHub commits into a polished email draft:

> Hi,
>
> Here is my weekly update for pitch-tipping for the week of Apr 13.
>
> Progress this week:
> - Captured 14.5 hours of coding activity, focused on model training and evaluation.
> - Shaped backend workflow contracts through 30 tracked commits.
> - Notable changes: Add pitch classifier v2; Fix eval metrics bug.
>
> Current blockers:
> - Waiting on GPU cluster access.
>
> Best,
> Arijit

The agent creates a Gmail draft — Arijit just reviews, tweaks, and hits send. What used to take 30 minutes of digging through git logs now takes 2 minutes.

### Saturday — Paper Scout

The agent runs **`run_paper_scout_workflow`**. It searches arXiv for papers matching his research keywords ("pitch tipping", "HCI", "behavior modeling"), ranks them by relevance, filters out papers he's already seen, and saves the top 3 to a reading list:

> 1. "Modeling Conversational Repair Signals in HCI" — score: 0.92
> 2. "Pitch Tipping Detection From Multimodal Dialogue" — score: 0.87
> 3. "Adaptive Behavior Modeling for Interactive Systems" — score: 0.81

No more doomscrolling arXiv. The agent finds what matters and skips what he's already read.

### The dashboard ties it all together

Arijit opens the web dashboard anytime and sees everything in one place: coding hours, commit count, upcoming deadlines, new papers, and the status of every workflow. He can hit "Run Now" on any workflow card to trigger it manually, or let the agent handle it on schedule.

**One agent. Five workflows. Zero context switching.**

## The key message

Ara turns our Python workflows into an intelligent agent that can reason about what to run, when, and in what order — we just define the tools and the agent figures out the orchestration.

## Claude Code agent log

Full conversation log for this build session:

```
C:\Users\ariji\.claude\projects\C--Studies-JHU-AraHackathon-ara-hackathon\975ceed0-a0bb-46a1-9874-18a640f9ad20.jsonl
```
