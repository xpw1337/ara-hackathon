# Team Worksplit: Grad Student Survival Agent

## Goal

Split the project into 3 parallel workstreams that can be built independently by:

1. Arijit
2. Archit
3. Harsh

The split below is designed to minimize merge conflicts and let each person finish a meaningful end-to-end slice of the product.

This version assumes the final deliverable is a functional webapp, not just backend automations.

## Current status

As of April 19, 2026, the project is in a good `all lanes present, not fully wired` state.

- Arijit lane is in:
  - Ara app skeleton
  - shared backend/state scaffolding
  - research log workflow
  - advisor update workflow
- Archit lane is in:
  - Vite/React frontend scaffold
  - dashboard cards
  - frontend API client and settings shell
- Harsh lane is in:
  - paper scout
  - deadline guardian
  - week planner
  - Canvas, Calendar, Todoist, delivery, and research integrations

The critical blockers are now integration blockers, not missing feature blockers:

- no real Ara API adapter layer exists yet under `backend/api/`
- the backend dashboard shape does not match the frontend's expected shape
- `app.py` does not yet expose `deadline_guardian` or `week_planner`
- Gmail drafting is still mock-first
- `tests/test_paper_scout.py` still needs follow-up to be stable in shared environments

## Decisions for the next build block

These decisions are now fixed and should not be re-opened during implementation.

### 1. Backend API framework

Use the `Ara API/runtime` as the backend surface. Do not add a separate `FastAPI` service.

### 2. Frontend-facing dashboard contract

The API response for `GET /api/dashboard` must be:

```json
{
  "generatedAt": "2026-04-19T15:30:00",
  "stats": {
    "codingHours": 0,
    "commits": 0,
    "upcomingDeadlines": 0,
    "papersFound": 0
  },
  "workflows": {
    "research-log": {
      "status": "idle",
      "lastRun": "",
      "summary": "",
      "artifacts": [],
      "errors": []
    },
    "advisor-update": {},
    "paper-scout": {},
    "deadline-guardian": {},
    "week-planner": {}
  },
  "recentArtifacts": []
}
```

### 3. Workflow run endpoints

The API must expose exactly these endpoints:

- `POST /api/workflows/research-log/run`
- `POST /api/workflows/advisor-update/run`
- `POST /api/workflows/paper-scout/run`
- `POST /api/workflows/deadline-guardian/run`
- `POST /api/workflows/week-planner/run`

Each endpoint should return the shared workflow result shape:

```python
{
    "ok": True,
    "workflow": "advisor_update",
    "summary": "Short human-readable summary",
    "artifacts": [],
    "errors": [],
    "data": {},
    "generated_at": "2026-04-19T15:30:00",
}
```

### 4. Stats derivation rules

The backend API should derive dashboard stats from saved workflow outputs using these exact rules:

- `codingHours`: latest `research_log.data.wakatime.total_hours`
- `commits`: latest `advisor_update.data.github.commit_count`
- `upcomingDeadlines`: latest `deadline_guardian.data.urgent_count`
- `papersFound`: latest `paper_scout.data.recommendation_count`

If a workflow has never run, the stat should be `0`.

### 5. Ownership boundary

- Arijit owns the Ara-facing API layer, shared contract translation, and `app.py`.
- Archit owns consuming the locked API shape in the frontend.
- Harsh owns making the planning/research workflows return the data fields that the API needs.

### 6. Frontend base URL rule

The frontend must use `VITE_API_URL` for the Ara API base URL and must stop assuming `http://localhost:8000/api` as the permanent backend address.

## Next assignments

## 1. Arijit: Integration owner

Arijit owns the shared integration layer from this point forward.

### Scope for the next block

- create the real Ara-facing API adapter layer under `backend/api/`
- add `GET /api/dashboard`
- add all five `POST /api/workflows/*/run` routes
- translate backend state into the locked `stats + workflows` frontend contract
- wire `run_deadline_guardian` and `run_week_planner` into `app.py` and the Ara API surface
- keep Gmail drafting mock-first until the HTTP/API path works end to end

### Files Arijit should own next

- `backend/api/`
- `app.py`
- any shared serializer or adapter under `backend/`

### Done criteria

- frontend can call the Ara API through `VITE_API_URL`
- all five run buttons hit real endpoints
- dashboard data no longer depends on frontend-only mock shape
- `app.py` exposes all five workflows

## 2. Archit: Frontend contract owner

Archit owns making the UI match the locked backend contract exactly.

### Scope for the next block

- update `frontend/src/api/client.js` to treat the backend API shape as the source of truth
- replace the hardcoded `http://localhost:8000/api` assumption with `VITE_API_URL`
- keep mock fallback data only if it matches the exact production contract
- update `Dashboard.jsx` and workflow cards to read `stats`, `workflows`, and `recentArtifacts`
- ensure the five workflow ids match the API ids exactly:
  - `research-log`
  - `advisor-update`
  - `paper-scout`
  - `deadline-guardian`
  - `week-planner`
- add graceful loading and backend-error handling without inventing new response shapes

### Files Archit should own next

- `frontend/src/api/client.js`
- `frontend/src/components/Dashboard.jsx`
- `frontend/src/components/WorkflowCard.jsx`
- `frontend/src/pages/Settings.jsx`

### Done criteria

- the dashboard loads from the real backend contract
- manual run buttons update the correct cards
- no frontend-only contract assumptions remain

## 3. Harsh: Workflow completion owner

Harsh owns finishing the workflow side so the integration layer has stable inputs.

### Scope for the next block

- make `deadline_guardian` return `data.urgent_count`
- make `week_planner` return stable `data` fields for top priorities and plan counts
- make `paper_scout` return `data.recommendation_count`
- ensure all planning/research workflows follow the shared result shape with `data` and `generated_at`
- fix `tests/test_paper_scout.py` so it passes reliably in shared environments
- keep reading list and delivery fallbacks local/mock-safe for demo reliability

### Files Harsh should own next

- `src/workflows/deadline_guardian.py`
- `src/workflows/week_planner.py`
- `src/workflows/paper_scout.py`
- `src/integrations/delivery.py`
- `tests/test_paper_scout.py`

### Done criteria

- planning and research workflows are API-safe
- stats can be computed directly from workflow `data`
- the research-lane test passes reliably

## Recommended implementation order from here

1. Arijit builds the thin backend API and app wiring.
2. Harsh adjusts workflow outputs so the backend can compute dashboard stats.
3. Archit switches the frontend to the real API contract.
4. Arijit finishes Gmail OAuth draft creation only after the full path works end to end.

## Product recap

The `Grad Student Survival Agent` has:

- a functional web UI
- a backend/API layer
- five core automations

- WakaTime to weekly research log
- GitHub commit tracking to Friday advisor update draft
- arXiv paper scout to reading list
- Canvas + Google Calendar deadline reminder
- Todoist Sunday week planner with academic deadlines

To keep the build practical, we are grouping these into 3 independent lanes:

- `Core Backend + Progress Lane`
- `Frontend Webapp Lane`
- `Planning + Research Lane`

## Team split

## 1. Arijit: Core Backend + Progress Lane

### Ownership

Arijit owns the Ara app skeleton, backend orchestration, and the work-progress automation flow.

### Main features

- Ara runtime entrypoint and scheduling skeleton
- backend API skeleton
- WakaTime activity fetch
- GitHub weekly commit fetch
- Friday advisor update generation
- Gmail draft creation

### Deliverables

- `app.py` updated to reflect the real Grad Student Survival Agent
- backend API endpoints for workflow triggering and dashboard data
- progress workflow that can:
  - fetch WakaTime activity
  - fetch project commits
  - summarize weekly work
  - generate advisor update content
  - create a draft email

### Suggested file ownership

- `app.py`
- `backend/api/`
- `backend/services/`
- `src/integrations/wakatime.py`
- `src/integrations/github_client.py`
- `src/integrations/gmail_client.py`
- `src/workflows/advisor_update.py`
- `src/workflows/research_log.py`

### Done criteria

- Manual run can produce a weekly progress summary
- Manual run can create a Gmail draft or mocked draft output
- WakaTime and GitHub data are normalized into a common structure
- Frontend has stable API endpoints to call for workflow actions

### Notes

Arijit is the best owner for this lane because it includes the highest-risk backend flow and touches the top-level Ara orchestration.

## 2. Archit: Frontend Webapp Lane

### Ownership

Archit owns the user-facing webapp.

### Main features

- dashboard UI
- workflow cards and result panels
- manual run controls
- settings/config UI
- frontend integration with backend API

### Deliverables

- responsive frontend that:
  - shows all major workflows
  - displays latest outputs
  - lets the user trigger runs manually
  - exposes configuration inputs for keywords and preferences
  - includes Canvas connection/settings state in the UI

### Suggested file ownership

- `frontend/`
- frontend routing/pages/components
- dashboard cards
- API client layer

### Done criteria

- The app opens into a polished dashboard
- The UI can display outputs from all workflows
- The UI can trigger workflow runs through the backend
- The UI is clean and demoable on a laptop

### Notes

This lane is critical because the final deliverable is a real webapp, and one person needs full ownership of the UI experience.

## 3. Harsh: Planning + Research Lane

### Ownership

Harsh owns the planning and research automations.

### Main features

- Canvas deadline fetch
- Google Calendar deadline scan
- 48-hour reminder logic
- Todoist task fetch
- Sunday week planner
- arXiv search and ranking
- keyword-based paper filtering
- duplicate-paper prevention
- reading list update target
- optional research digest output
- outbound reminder/message abstraction

### Deliverables

- paper scout workflow that:
  - searches for relevant papers
  - ranks top results
  - avoids repeats
  - updates a reading list
- planning workflows that:
  - merge Canvas and Calendar deadlines
  - detect deadline risks
  - generate weekly plans
  - send reminders

### Suggested file ownership

- `src/integrations/canvas_client.py`
- `src/integrations/calendar_client.py`
- `src/integrations/todoist_client.py`
- `src/integrations/delivery.py`
- `src/integrations/research_sources.py`
- `src/integrations/reading_list_writer.py`
- `src/workflows/deadline_guardian.py`
- `src/workflows/week_planner.py`
- `src/workflows/paper_scout.py`
- `src/state/papers_seen.py`

### Done criteria

- A weekly run can produce top 3 papers from user keywords
- Already-seen papers are filtered out
- Canvas deadlines can be fetched and normalized
- Calendar events can be filtered into "needs reminder" vs "ignore"
- Todoist tasks can be ranked into a weekly plan
- Reminder delivery works through one reliable channel
- A reading list can be updated in one destination:
  - Notion
  - Google Drive
  - or local markdown fallback for demo stability

### Notes

This lane groups the remaining integrations into one backend workstream that is still mostly independent from the frontend and progress lane.

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

This makes integration into `app.py` and the backend API straightforward.

## 2. Common file structure

All new code should follow this layout:

```text
frontend/
backend/
src/
  integrations/
  workflows/
  state/
```

## 3. State handling rule

Each owner should manage only their own state files.

Examples:

- Arijit: `data/research_log_state.json`, `data/weekly_updates.json`
- Archit: no shared backend state ownership by default; owns frontend UI state only
- Harsh: `data/deadline_alerts.json`, `data/week_plan_history.json`, `data/papers_seen.json`

## 4. Secrets rule

No API keys in code or committed files.

Use environment variables or Ara secrets only.

## 5. Mock-first rule

If a real integration is slow or blocked, each lane should still support mocked/demo data so the feature can be shown reliably.

## Integration plan

## Merge point 1: shared app skeleton

Arijit sets up:

- the main Ara entrypoint
- backend API skeleton
- top-level workflow registration
- a lightweight shared utils/state layout

This should happen first so everyone can code against the same structure.

## Merge point 2: vertical lane merge

Each person merges only their owned files.

Avoid editing someone else's workflow unless explicitly coordinated.

## Merge point 3: final demo wiring

After all three lanes exist:

- hook all workflows into `app.py`
- hook frontend to backend APIs
- add one manual demo trigger per workflow
- test one full run per lane

## Recommended implementation order

### Day 1 / first block

- Arijit: create backend and `src/` skeleton plus app orchestration
- Archit: scaffold frontend dashboard and API client
- Harsh: stub planning, Canvas, and research integrations

### Day 1 / second block

- Arijit: finish WakaTime + GitHub summary path
- Archit: finish dashboard cards and manual trigger UI
- Harsh: finish Canvas/planning flows plus arXiv ranking and dedupe path

### Day 1 / final block

- wire Gmail draft creation
- wire one outbound channel
- wire one reading list destination
- wire backend responses into the UI
- end-to-end testing and demo prep

## Scope guardrails

To prevent overload, each owner should prioritize:

### Arijit

- real GitHub
- real WakaTime if possible
- Gmail draft or mocked draft fallback

### Archit

- polished dashboard first
- workflow cards second
- settings UI only if core screens are done

### Harsh

- real Todoist
- real Canvas
- real Calendar
- real arXiv search via web/API
- local markdown reading list fallback if Notion/Drive is slow

## Final assignment summary

- `Arijit`:
  - core Ara app skeleton
  - backend API layer
  - WakaTime research log
  - GitHub weekly progress
  - Gmail advisor draft

- `Archit`:
  - frontend webapp
  - dashboard and workflow cards
  - manual trigger and result UI

- `Harsh`:
  - Canvas academic deadline integration
  - Google Calendar deadline guardian
  - Todoist weekly planner
  - reminder/message delivery
  - arXiv paper scout
  - keyword ranking and dedupe
  - reading list integration

## Recommended ownership rule for commits

Each person should primarily commit only within their owned file set. This keeps merge conflicts low and makes debugging easier during the hackathon.
