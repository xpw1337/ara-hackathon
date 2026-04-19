# PRD: Grad Student Survival Agent

## 1. Overview

### Product name

`Grad Student Survival Agent`

### One-line pitch

An Ara-powered academic operations webapp that watches the tools a grad student already uses and proactively turns activity, deadlines, papers, and tasks into concrete weekly outputs.

### Product thesis

Most "student assistants" stop at summarization. Grad students actually need a system that notices work happening across coding, writing, planning, scheduling, and reading, then takes follow-through actions on their behalf.

This project uses Ara as the persistent agent runtime behind a functional webapp that:

- monitors multiple academic signals
- synthesizes them into useful updates
- writes to external tools
- nudges the user before something slips
- exposes results through a dashboard the user can actually operate

The goal is to make graduate research feel coordinated rather than fragmented.

## 2. Problem

Grad students operate across too many disconnected systems:

- coding work lives in GitHub and WakaTime
- project planning lives in Todoist
- schedules live in Google Calendar
- reading lives across arXiv and scattered notes
- advisor communication lives in Gmail
- weekly logs live in Notion or Drive

This fragmentation creates predictable failures:

- research hours are not logged consistently
- weekly progress updates are forgotten or written in a rush
- relevant new papers are found too late
- deadlines sneak up
- weekly plans are reactive instead of intentional

## 3. Target User

### Primary user

A CS/HCI/ML grad student doing ongoing project work with:

- a codebase under active development
- an advisor or PI expecting regular updates
- weekly tasks and milestone deadlines
- a need to track literature continuously

### Example user

A Johns Hopkins grad student working on the pitch tipping project who codes during the week, meets an advisor regularly, keeps tasks in Todoist, and needs to stay current on papers.

## 4. Product Goals

### Primary goals

- Reduce academic coordination overhead by automating weekly upkeep.
- Surface the most important upcoming obligations before they become urgent.
- Turn scattered work signals into deliverables a student would have written manually.
- Demonstrate Ara as a real execution agent inside a polished, functional webapp.

### Success criteria for the hackathon

- At least 3 end-to-end automations work reliably in demo.
- The agent writes to at least 2 external systems.
- The agent proactively sends at least 1 outbound reminder/update.
- The webapp shows workflow outputs and supports manual workflow triggers.
- Judges can understand the value in under 30 seconds.

### Non-goals

- Full LMS integration
- Full citation manager replacement
- Perfect semantic search across all research artifacts
- Enterprise-grade auth or multi-user collaboration

## 5. Core User Value

By the end of each week, the user should feel:

- "My research hours were captured without me doing admin work."
- "My advisor update was basically done for me."
- "I did not miss relevant papers or deadlines."
- "My week plan feels prioritized, not random."

## 6. Core Features

## Feature 0: Functional Web Dashboard

### User value

The student can see what the agent has done, what is pending, and what to run next without relying on a terminal or hidden backend logs.

### Core UI surfaces

- Home dashboard
- Advisor update card
- Research log card
- Paper scout card
- Deadline alerts card
- Weekly plan card
- Settings/config section

### Core behavior

- Display latest outputs from each workflow
- Allow manual "run now" action for each workflow
- Show connected integration status
- Surface recent generated artifacts such as email drafts, plans, and paper recommendations

### Demoable output

A dashboard that visibly updates after a workflow run and makes the product feel like a complete tool, not just a backend automation.

## Feature A: WakaTime to Research Log

### User value

The student no longer has to manually remember how much time they spent coding or what they worked on.

### Trigger

- Daily scheduled run
- Optional manual run

### Inputs

- WakaTime activity summary
- GitHub commit metadata for the selected project

### Outputs

- Weekly research log entry in Notion or Google Drive
- Optional local cache in Ara workspace

### Core behavior

- Pull coding activity by day and project
- Extract rough themes from file/project names and commit messages
- Append a structured log entry for the current week
- Avoid duplicate entries by checking previously written dates

### Demoable output

"This week you spent 11.8 hours coding on pitch tipping, mostly in model training, UI cleanup, and evaluation scripts."

## Feature B: Friday Advisor Update Draft

### User value

The student gets a clean advisor update drafted from real work instead of writing it from scratch every Friday.

### Trigger

- Every Friday afternoon
- Manual "draft now" option

### Inputs

- GitHub commits from the pitch tipping repo
- WakaTime weekly activity summary
- Todoist completed tasks
- Prior advisor update memory

### Outputs

- Draft email in Gmail
- Optional saved markdown file in Ara workspace

### Core behavior

- Collect commits from the week
- Group work into meaningful progress themes
- Identify wins, blockers, and next steps
- Draft an advisor-style summary with clear bullet points
- Send as a draft, not a final sent email, for safety

### Demoable output

An email draft with sections:

- progress this week
- current blockers
- plan for next week

## Feature C: Weekly arXiv Research Scout

### User value

The student gets a lightweight stream of new papers relevant to their work without manually checking arXiv.

### Trigger

- Weekly scheduled run

### Inputs

- User-defined keywords
- arXiv search results via web retrieval
- Existing reading list state

### Outputs

- Top 3 paper recommendations
- Reading list entry in Notion/Drive/local file
- Optional digest message via Telegram/WhatsApp

### Core behavior

- Query arXiv or web search with user keywords
- Rank papers by novelty and relevance
- Avoid repeats already seen in prior weeks
- Save shortlisted papers with link, summary, and reason it matters

### Demoable output

"3 new papers relevant to your work on pitch tipping and HCI behavior modeling, with 1-sentence reasons each."

## Feature D: Deadline Guardian

### User value

The student gets warned early enough to act, not merely informed after it is already urgent.

### Trigger

- Daily scan

### Inputs

- Google Calendar events

### Outputs

- Reminder message 48 hours before deadline
- Optional escalation summary in daily digest

### Core behavior

- Identify deadlines and important events
- Filter out low-value calendar noise
- Send a nudge exactly once per threshold window
- Include suggested prep action in the reminder

### Demoable output

"HCI cheat sheet is due in 48 hours. Best next step: block 90 minutes tonight to finalize the reference section."

## Feature E: Sunday Week Planner

### User value

The student starts the week with a prioritized plan instead of an unranked task dump.

### Trigger

- Every Sunday evening

### Inputs

- Todoist tasks
- Google Calendar events for the upcoming week
- Open advisor/research obligations from agent memory

### Outputs

- Prioritized weekly plan
- Text/Telegram/WhatsApp delivery
- Optional Notion weekly page update

### Core behavior

- Pull open tasks
- Cluster by urgency, effort, and deadline
- Propose a realistic top-priority sequence
- Highlight one overloaded day and one recovery opportunity

### Demoable output

A message with:

- top 3 priorities
- key deadlines
- recommended focus blocks

## 7. Why Ara

Ara is the right runtime because the product requires:

- persistent automation
- multi-step tool usage
- scheduled background execution
- outbound communication
- memory across runs

Ara should be the orchestration and reasoning layer, not the source of truth for every external tool.

Ara should also not be the entire product surface. The user-facing product should be a webapp that calls into the Ara-backed workflow layer.

### Verified Ara capabilities relevant here

- `ara.Automation(...)` for long-running agents and scheduled deployments
- `@ara.tool` for custom integration logic
- channel delivery through at least documented Telegram support
- connector-backed runtime flows in the official SDK examples, including Gmail-style usage

References:

- [Ara Docs](https://docs.ara.so/)
- [SDK Quickstart](https://docs.ara.so/sdk/quickstart)
- [SDK Reference](https://docs.ara.so/sdk/reference/modal)
- [Telegram channel docs](https://docs.ara.so/channels/telegram)
- [Architecture](https://docs.ara.so/architecture)
- [Official Gmail-to-iMessage example](https://github.com/Aradotso/ara-python-sdk/blob/main/examples/11-gmail-to-imessage.py)

### Practical implication

For the hackathon, the safest implementation is:

- use Ara for schedules, memory, reasoning, and outbound messages
- use custom tools to bridge WakaTime, GitHub, Todoist, Google Calendar, Gmail, and Notion/Drive
- use Telegram as the guaranteed messaging fallback if WhatsApp is not exposed in the event environment

## 8. System Architecture

## High-level flow

1. The webapp UI displays current status, outputs, and run controls.
2. The backend API receives UI actions or scheduled triggers.
3. External tools are polled on a schedule or on-demand.
4. Ara calls custom tools to fetch fresh state.
5. Ara normalizes data into a shared internal model.
6. Ara compares new state against prior memory to prevent duplicate or noisy outputs.
7. Ara writes the resulting artifact or message to the appropriate destination.
8. The backend returns workflow outputs to the UI for display.

## Components

### A. Web frontend

Responsibilities:

- show workflow results and system state
- provide manual run controls
- display generated artifacts in a judge-friendly way
- expose settings for keywords, project name, and destinations

Suggested surfaces:

- dashboard
- workflow detail cards
- settings page or panel
- activity/history feed

### B. Backend API layer

Responsibilities:

- serve frontend requests
- trigger workflow runs
- read and return saved workflow outputs
- provide a stable interface between UI and Ara-backed logic

Example endpoints:

- `GET /api/dashboard`
- `POST /api/workflows/advisor-update/run`
- `POST /api/workflows/paper-scout/run`
- `POST /api/workflows/deadline-guardian/run`
- `POST /api/workflows/week-planner/run`
- `GET /api/history`

### C. Ara automation runtime

Responsibilities:

- schedule execution
- decide which workflow should run
- reason over fetched tool outputs
- generate summaries, plans, and drafts
- maintain persistent memory files

### D. Integration tool layer

Custom tools we implement as Python functions:

- `get_wakatime_summary`
- `get_github_weekly_commits`
- `get_calendar_upcoming_events`
- `get_todoist_tasks`
- `search_arxiv_papers`
- `append_research_log`
- `create_gmail_draft`
- `send_nudge_message`
- `update_reading_list`

### E. Memory/state layer

Stored locally in Ara workspace as JSON or markdown:

- `state/research_log_state.json`
- `state/deadline_alerts.json`
- `state/papers_seen.json`
- `state/weekly_updates.json`
- `state/week_plan_history.json`

These files prevent duplicate alerts and preserve continuity.

### F. Delivery layer

Primary:

- Gmail drafts
- Notion or Google Drive updates

Secondary:

- Telegram or WhatsApp nudge channel

## 9. Data Model

## Shared objects

### WorkLogEntry

- `week_start`
- `date`
- `source`
- `hours`
- `project`
- `summary`
- `commit_refs`

### AdvisorUpdate

- `week_start`
- `repo`
- `progress_points`
- `blockers`
- `next_steps`
- `draft_id`
- `created_at`

### PaperCandidate

- `id`
- `title`
- `authors`
- `url`
- `abstract_summary`
- `relevance_reason`
- `discovered_at`
- `status`

### DeadlineAlert

- `event_id`
- `title`
- `start_time`
- `alert_window`
- `sent_at`
- `message_channel`

### WeeklyPlan

- `week_start`
- `top_priorities`
- `deadline_risks`
- `recommended_blocks`
- `sent_at`

### DashboardSnapshot

- `generated_at`
- `research_log_summary`
- `advisor_update_status`
- `paper_scout_summary`
- `deadline_alert_summary`
- `weekly_plan_summary`
- `recent_artifacts`

## 10. User Stories

- As a grad student, I want my coding time logged automatically so I do not lose track of my weekly research effort.
- As a grad student, I want a Friday advisor update drafted from my real work so I can send a thoughtful update quickly.
- As a grad student, I want relevant new papers surfaced weekly so I stay current without browsing for hours.
- As a grad student, I want deadline nudges before key events so I can prepare early.
- As a grad student, I want a Sunday week plan based on my real tasks and calendar so I start the week with direction.

## 11. MVP Scope

### Must-have for hackathon demo

- functional web dashboard
- manual run buttons for each workflow
- workflow result cards in UI
- WakaTime summary fetch
- GitHub weekly commit fetch
- advisor update draft generation
- arXiv paper discovery
- Google Calendar deadline nudge
- Todoist weekly plan generation
- one outbound messaging channel
- one write-back destination for logs

### Nice-to-have

- Notion integration and Google Drive integration both supported
- richer settings/config UI
- conversation interface for "what changed this week?"
- confidence scoring on paper recommendations

### Out of scope

- full bi-directional Gmail inbox agent
- smart auto-reply sending without user review
- collaborative advisor feedback loop
- PDF ingestion and annotation workflow

## 12. Functional Requirements

- The system must run scheduled workflows without manual prompting.
- The system must expose a web UI that can manually trigger workflows.
- The system must display the latest workflow outputs in the UI.
- The system must store enough local state to avoid duplicate alerts and duplicate paper recommendations.
- The system must draft, not auto-send, advisor emails by default.
- The system must send a deadline nudge exactly once per configured threshold.
- The system must generate a weekly plan from Todoist and Calendar together, not from Todoist alone.
- The system must allow keyword configuration for paper search.

## 13. Non-Functional Requirements

- The demo path must complete within 10-20 seconds for a single run.
- Failures in one integration should not block unrelated workflows.
- Outputs should be legible and concise enough for real use.
- The UI should load quickly and work on laptop-sized demo screens.
- Secrets must live in environment variables or Ara secret storage, not committed files.

## 14. UI Requirements

### Primary screens

- `Dashboard`
- `Workflow details`
- `Settings / integrations`

### Dashboard requirements

- show 5 workflow cards
- show latest run timestamp per workflow
- show latest output summary per workflow
- include one-click manual run controls

### Workflow card requirements

Each card should show:

- status
- latest summary
- primary artifact preview
- manual run button

### Settings requirements

- editable research keywords
- project/repo name
- preferred delivery channel
- selected writing destination

### Design requirements

- polished and presentable enough for a hackathon demo
- clear visual grouping
- not just raw JSON output
- usable on standard laptop width
## 15. Risks and Mitigations

## Risk: too many integrations for one hackathon

Mitigation:

- build the tool interfaces first
- mock one or two sources if auth setup becomes slow
- prioritize Gmail, GitHub, Calendar, Todoist, and one writing destination

## Risk: WhatsApp delivery may not be available

Mitigation:

- implement delivery behind a single `send_nudge_message` abstraction
- use Telegram as the primary fallback because it is publicly documented by Ara

## Risk: Notion and Google Drive both take too long

Mitigation:

- support one write-back target in MVP
- keep the other in the PRD as an extension path

## Risk: advisor update quality feels generic

Mitigation:

- include commit metadata, completed tasks, and current blockers
- store prior update examples so tone can improve over time

## Risk: backend works but UI feels unfinished

Mitigation:

- assign one person full ownership of frontend
- keep the UI focused on dashboard + cards + manual runs
- render workflow outputs as polished summaries, not raw logs
## 16. Demo Narrative

### Demo goal

Show that the agent does real academic upkeep across tools with minimal user prompting.

### Suggested 2-3 minute demo

1. Open the web dashboard and explain the 5 workflow cards.
2. Seed or connect real WakaTime, GitHub, Calendar, and Todoist data.
3. Run the Friday update workflow.
4. Show:
   - fetched coding hours
   - summarized commits
   - drafted advisor email
5. Run the paper scout workflow.
6. Show:
   - top 3 papers
   - reading list update
7. Run deadline guardian or week planner.
8. Show:
   - outbound reminder or weekly plan message
   - reflected UI status and artifact previews

### Judge takeaway

"This is not a chatbot. It is a grad school operations webapp that keeps your academic life in sync."
## 17. Implementation Plan

## Phase 1: Foundation

- set up Ara app structure
- set up frontend app shell
- set up backend API shell
- define tool interfaces
- create state files and schemas
- define schedule map

## Phase 2: Core integrations

- GitHub weekly commit tool
- WakaTime summary tool
- Todoist task fetch tool
- Calendar upcoming deadline tool
- arXiv search tool

## Phase 3: Write-back and delivery

- Gmail draft creation
- Notion or Drive weekly log writer
- Telegram/WhatsApp nudge sender

## Phase 4: Demo polish

- improve prompt templates
- add sample data seeding
- add one command to run all demo workflows
- polish dashboard cards and workflow states

## 18. Suggested Workflow Schedule

- Daily at 8 PM: WakaTime research log sync
- Friday at 3 PM: advisor update draft
- Saturday morning: arXiv paper scout
- Daily at 9 AM: deadline scan with 48-hour warning logic
- Sunday at 6 PM: weekly plan generation
## 19. Proposed File Structure

```text
ara-hackathon/
  app.py
  frontend/
    src/
    public/
  backend/
    api/
    services/
  docs/
    prd-grad-student-survival-agent.md
  src/
    integrations/
      wakatime.py
      github_client.py
      todoist_client.py
      calendar_client.py
      gmail_client.py
      research_sources.py
      delivery.py
    workflows/
      research_log.py
      advisor_update.py
      paper_scout.py
      deadline_guardian.py
      week_planner.py
    state/
      store.py
      models.py
  data/
    .gitkeep
```
## 20. Acceptance Criteria

- The app has a functional web UI with workflow cards and manual triggers.
- A research log can be generated from WakaTime data and written to one destination.
- A Friday advisor update can be drafted from GitHub and WakaTime data.
- A weekly paper scout can produce 3 non-duplicate relevant papers.
- A 48-hour deadline reminder can be generated from Calendar events.
- A weekly Todoist-based plan can be delivered to the user.
- The app can demonstrate at least one outbound message channel through Ara.
## 21. Open Decisions

- Primary write-back target: Notion or Google Drive?
- Primary nudge channel: Telegram or WhatsApp?
- Real auth for all integrations or partial mock data for demo resilience?
- Single-project only for MVP or multiple projects later?
## 22. Recommendation for the Hackathon

To maximize reliability and still look impressive:

- use real GitHub, Todoist, Calendar, and Gmail draft flows
- use Telegram as the main nudge channel unless WhatsApp is confirmed in Ara
- use either Notion or Drive, not both, for MVP
- keep arXiv discovery real, but cache results locally for demo stability
- keep the UI focused on one polished dashboard rather than many screens

This yields a product that feels rich and cross-tool without taking on too much integration risk in one day.
