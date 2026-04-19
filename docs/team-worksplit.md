# Team Worksplit: Grad Student Survival Agent

## Goal

Split the project into 3 parallel workstreams that can be built independently by:

1. Arijit
2. Archit
3. Harsh

The split below is designed to minimize merge conflicts and let each person finish a meaningful end-to-end slice of the product.

## Product recap

The `Grad Student Survival Agent` has five core automations:

- WakaTime to weekly research log
- GitHub commit tracking to Friday advisor update draft
- arXiv paper scout to reading list
- Google Calendar deadline reminder
- Todoist Sunday week planner

To keep the build practical, we are grouping these into 3 independent lanes:

- `Progress Lane`
- `Planning Lane`
- `Research Lane`

## Team split

## 1. Arijit: Core Runtime + Progress Lane

### Ownership

Arijit owns the Ara app skeleton and the work-progress automation flow.

### Main features

- Ara runtime entrypoint and scheduling skeleton
- WakaTime activity fetch
- GitHub weekly commit fetch
- Friday advisor update generation
- Gmail draft creation

### Deliverables

- `app.py` updated to reflect the real Grad Student Survival Agent
- progress workflow that can:
  - fetch WakaTime activity
  - fetch project commits
  - summarize weekly work
  - generate advisor update content
  - create a draft email

### Suggested file ownership

- `app.py`
- `src/integrations/wakatime.py`
- `src/integrations/github_client.py`
- `src/integrations/gmail_client.py`
- `src/workflows/advisor_update.py`
- `src/workflows/research_log.py`

### Done criteria

- Manual run can produce a weekly progress summary
- Manual run can create a Gmail draft or mocked draft output
- WakaTime and GitHub data are normalized into a common structure

### Notes

Arijit is the best owner for this lane because it includes the highest-risk core flow and touches the top-level Ara orchestration.

## 2. Archit: Planning Lane

### Ownership

Archit owns the planning and reminder automations.

### Main features

- Google Calendar deadline scan
- 48-hour reminder logic
- Todoist task fetch
- Sunday week planner
- outbound nudge channel abstraction

### Deliverables

- deadline guardian workflow
- weekly planning workflow
- message delivery layer for reminders and week plans

### Suggested file ownership

- `src/integrations/calendar_client.py`
- `src/integrations/todoist_client.py`
- `src/integrations/delivery.py`
- `src/workflows/deadline_guardian.py`
- `src/workflows/week_planner.py`

### Done criteria

- Calendar events can be filtered into "needs reminder" vs "ignore"
- Todoist tasks can be ranked into a weekly plan
- Reminder delivery works through one reliable channel
- If WhatsApp is unavailable, Telegram fallback is supported

### Notes

This lane is highly demoable and mostly independent from the advisor-update workflow.

## 3. Harsh: Research Lane + Reading List

### Ownership

Harsh owns the paper discovery and reading-list automation flow.

### Main features

- arXiv search and ranking
- keyword-based paper filtering
- duplicate-paper prevention
- reading list update target
- optional research digest output

### Deliverables

- paper scout workflow that:
  - searches for relevant papers
  - ranks top results
  - avoids repeats
  - updates a reading list

### Suggested file ownership

- `src/integrations/research_sources.py`
- `src/integrations/reading_list_writer.py`
- `src/workflows/paper_scout.py`
- `src/state/papers_seen.py`

### Done criteria

- A weekly run can produce top 3 papers from user keywords
- Already-seen papers are filtered out
- A reading list can be updated in one destination:
  - Notion
  - Google Drive
  - or local markdown fallback for demo stability

### Notes

This lane is independent enough to build in parallel and adds strong "research-native" value to the product.

## Shared contracts

To keep the three lanes independent, everyone should build against the same simple contracts.

## 1. Common workflow output shape

Each workflow should return a JSON-serializable object like:

```python
{
    "ok": True,
    "workflow": "advisor_update",
    "summary": "Short human-readable summary",
    "artifacts": [],
    "errors": [],
}
```

This makes integration into `app.py` straightforward.

## 2. Common file structure

All new code should follow this layout:

```text
src/
  integrations/
  workflows/
  state/
```

## 3. State handling rule

Each owner should manage only their own state files.

Examples:

- Arijit: `data/research_log_state.json`, `data/weekly_updates.json`
- Archit: `data/deadline_alerts.json`, `data/week_plan_history.json`
- Harsh: `data/papers_seen.json`

## 4. Secrets rule

No API keys in code or committed files.

Use environment variables or Ara secrets only.

## 5. Mock-first rule

If a real integration is slow or blocked, each lane should still support mocked/demo data so the feature can be shown reliably.

## Integration plan

## Merge point 1: shared app skeleton

Arijit sets up:

- the main Ara entrypoint
- top-level workflow registration
- a lightweight shared utils/state layout

This should happen first so everyone can code against the same structure.

## Merge point 2: vertical lane merge

Each person merges only their owned files.

Avoid editing someone else's workflow unless explicitly coordinated.

## Merge point 3: final demo wiring

After all three lanes exist:

- hook all workflows into `app.py`
- add one manual demo trigger per workflow
- test one full run per lane

## Recommended implementation order

### Day 1 / first block

- Arijit: create `src/` structure and app skeleton
- Archit: stub planning integrations and reminder logic
- Harsh: stub paper search and reading-list logic

### Day 1 / second block

- Arijit: finish WakaTime + GitHub summary path
- Archit: finish Calendar + Todoist ranking path
- Harsh: finish arXiv ranking + dedupe path

### Day 1 / final block

- wire Gmail draft creation
- wire one outbound channel
- wire one reading list destination
- end-to-end testing and demo prep

## Scope guardrails

To prevent overload, each owner should prioritize:

### Arijit

- real GitHub
- real WakaTime if possible
- Gmail draft or mocked draft fallback

### Archit

- real Todoist
- real Calendar
- Telegram fallback if WhatsApp is blocked

### Harsh

- real arXiv search via web/API
- local markdown reading list fallback if Notion/Drive is slow

## Final assignment summary

- `Arijit`:
  - core Ara app skeleton
  - WakaTime research log
  - GitHub weekly progress
  - Gmail advisor draft

- `Archit`:
  - Google Calendar deadline guardian
  - Todoist weekly planner
  - reminder/message delivery

- `Harsh`:
  - arXiv paper scout
  - keyword ranking and dedupe
  - reading list integration

## Recommended ownership rule for commits

Each person should primarily commit only within their owned file set. This keeps merge conflicts low and makes debugging easier during the hackathon.
