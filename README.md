# Grad Student Survival Agent

An Ara-powered academic operations webapp that watches the tools a grad student already uses and turns activity, deadlines, papers, and tasks into concrete weekly outputs.

Instead of acting like a chatbot, it combines a functional web UI with background Ara automations that do real coordination work across coding, planning, research, scheduling, and advisor communication.

## Core idea

Graduate research lives across too many disconnected systems:

- WakaTime
- GitHub
- Canvas
- Google Calendar
- Gmail
- Todoist
- Notion or Google Drive
- arXiv

This project uses Ara as the persistent automation and reasoning layer behind a functional webapp. The UI gives the user a place to view progress, review outputs, trigger workflows, and configure keywords and integrations.

## What it does

- Watches WakaTime coding activity and logs research work to Notion or Google Drive
- Monitors GitHub commits on the pitch tipping project and drafts a weekly advisor update
- Searches for relevant new arXiv papers and adds the top results to a reading list
- Scans Canvas and Google Calendar for upcoming deadlines and sends a reminder 48 hours early
- Pulls Todoist tasks and generates a prioritized weekly plan every Sunday

## Why this is a strong hackathon project

- It fits Ara's strengths: persistent runtime, tools, automations, memory, and outbound messaging
- It does real work across multiple systems instead of just summarizing
- It has a functional UI, which makes the product feel complete and demo-ready
- It is easy to explain in one sentence
- It is highly relatable to judges, students, and researchers
- It has a clean demo path with visible before-and-after outputs

## Why Ara

Ara is the right backend orchestration layer for this because the product needs:

- scheduled background runs
- multi-step tool usage
- persistent state across runs
- outbound messages and drafts
- a runtime that can reason over several integrations in sequence

Relevant references:

- [Ara Docs](https://docs.ara.so/)
- [Ara SDK Quickstart](https://docs.ara.so/sdk/quickstart)
- [Ara SDK Reference](https://docs.ara.so/sdk/reference/modal)
- [Ara Architecture](https://docs.ara.so/architecture)
- [Telegram channel docs](https://docs.ara.so/channels/telegram)
- [Ara Python SDK](https://github.com/Aradotso/ara-python-sdk/)

## MVP

The hackathon MVP includes a functional webapp plus five automations:

### Webapp UI

- dashboard for this week's work, deadlines, tasks, and papers
- manual buttons to run each workflow
- cards for advisor draft, research log, paper scout, deadline alerts, and weekly plan
- lightweight settings/config surface for keywords and integration status
- Canvas-backed college deadline visibility

### Automations

1. `Research Log Sync`
   Pull WakaTime activity and write a weekly research log entry.
2. `Advisor Update Draft`
   Summarize GitHub commits and work progress into a Gmail draft every Friday.
3. `Paper Scout`
   Search arXiv for new relevant papers and update a reading list.
4. `Deadline Guardian`
   Watch Canvas and Calendar events and send a reminder 48 hours before important deadlines.
5. `Sunday Week Planner`
   Pull Todoist tasks plus upcoming Canvas/Calendar deadlines and build a prioritized plan for the upcoming week.

## Demo flow

1. Open the web dashboard and show connected academic workflows.
2. Show recent coding activity and GitHub progress in the UI.
3. Run the advisor update workflow and open the drafted email result card.
4. Run the paper scout workflow and show the reading list update in the UI.
5. Trigger a Canvas-backed deadline reminder flow.
6. Generate the Sunday week plan and show the summary plus outbound message result.

Judge takeaway:

"This isn't just an assistant. It's an academic operations layer that keeps a grad student's work life in sync."

## Current build status

As of April 19, 2026, the repo is in an `all lanes present, not fully wired` state.

- Arijit lane is in: Ara app skeleton, shared state layer, research log, advisor update, and backend fixtures.
- Archit lane is in: Vite/React frontend scaffold with dashboard cards, API client, and settings shell.
- Harsh lane is in: paper scout, deadline guardian, week planner, and the supporting integration clients.

What is still missing before the app works end to end:

- there is no real Ara API adapter layer wired for the frontend yet
- the backend dashboard shape currently centers on `workflow_cards`, while the frontend expects `stats` plus `workflows`
- `app.py` exposes `research_log`, `advisor_update`, and `paper_scout`, but not `deadline_guardian` or `week_planner`
- Gmail drafting is still mock-first rather than real OAuth-backed draft creation
- `tests/test_paper_scout.py` still needs follow-up so the research lane is stable in shared environments

## Integration decisions

These decisions are now locked so the team can move without re-discussing architecture:

1. The backend surface will be the `Ara API/runtime`. Do not add a separate `FastAPI` service.
2. The frontend-facing dashboard contract is:

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
    }
  },
  "recentArtifacts": []
}
```

3. The canonical workflow run endpoints are:
   - `POST /api/workflows/research-log/run`
   - `POST /api/workflows/advisor-update/run`
   - `POST /api/workflows/paper-scout/run`
   - `POST /api/workflows/deadline-guardian/run`
   - `POST /api/workflows/week-planner/run`
4. The frontend should consume the Ara API base URL through `VITE_API_URL` instead of hardcoding `http://localhost:8000/api`.
5. Internal storage in `src/state/store.py` can keep using `workflow_cards` if useful, but the Ara-facing API layer must translate that into the frontend contract above.
6. No new product features should be added until the API layer and all five workflow triggers work through one shared contract.

## Current repo contents

- `app.py`: Ara runtime entrypoint with research log, advisor update, and paper scout tools
- `frontend/`: Vite/React webapp scaffold with dashboard UI and API client
- `backend/`: currently fixtures only; still needs the real Ara-facing API adapter layer
- `docs/ideas.md`: earlier idea exploration
- `docs/prd-grad-student-survival-agent.md`: detailed product requirements and implementation plan
- `docs/team-worksplit.md`: team ownership and parallel work plan
- `requirements.txt`: Python dependency list

## Planned project structure

```text
ara-hackathon/
  app.py
  frontend/
  backend/
  docs/
    ideas.md
    prd-grad-student-survival-agent.md
    team-worksplit.md
  src/
    integrations/
    workflows/
    state/
  data/
```

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ara setup

```bash
ara auth login
ara run app.py
ara deploy app.py --cron "*/5 * * * *"
```

For the hackathon build, Ara should be used for orchestration, memory, scheduling, and outbound messaging. The webapp should sit on top of a thin API layer that calls the Ara workflows and exposes workflow results to the UI. External services like WakaTime, Todoist, Calendar, Gmail, Notion, and Drive should be integrated through custom tools.

Canvas should be treated as the primary institutional deadline source. If a course uses Gradescope through Canvas, those deadlines may still surface through Canvas and can be handled indirectly without a standalone Gradescope API integration.

## Product doc

The main build spec lives here:

- [docs/prd-grad-student-survival-agent.md](./docs/prd-grad-student-survival-agent.md)

## Next steps

1. Build the real Ara-facing API adapter layer under `backend/api/`.
2. Normalize dashboard and workflow responses to the locked `stats + workflows` API contract.
3. Wire `deadline_guardian` and `week_planner` into `app.py` and the Ara API surface.
4. Make the frontend consume the real Ara API contract instead of relying on mock-shape fallbacks.
5. Finish Gmail OAuth drafting and one reliable outbound reminder channel after the integration layer works.

## Local development right now

Ara runtime:

```bash
ara auth login
ara run app.py
```

Frontend scaffold:

```bash
cd frontend
npm install
npm run dev
```

Current caveat:

- the frontend currently assumes an HTTP API at `http://localhost:8000/api`
- that should be replaced with the Ara API base URL via `VITE_API_URL`
- so the dashboard can render with mock fallbacks, but the full product is not wired end to end yet
