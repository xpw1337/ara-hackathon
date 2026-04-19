# Grad Student Survival Agent

An Ara-powered academic operations webapp that watches the tools a grad student already uses and turns activity, deadlines, papers, and tasks into concrete weekly outputs.

Instead of acting like a chatbot, it combines a functional web UI with background Ara automations that do real coordination work across coding, planning, research, scheduling, and advisor communication.

## Core idea

Graduate research lives across too many disconnected systems:

- WakaTime
- GitHub
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
- Scans Google Calendar for upcoming deadlines and sends a reminder 48 hours early
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

### Automations

1. `Research Log Sync`
   Pull WakaTime activity and write a weekly research log entry.
2. `Advisor Update Draft`
   Summarize GitHub commits and work progress into a Gmail draft every Friday.
3. `Paper Scout`
   Search arXiv for new relevant papers and update a reading list.
4. `Deadline Guardian`
   Watch Calendar events and send a reminder 48 hours before important deadlines.
5. `Sunday Week Planner`
   Pull Todoist tasks and build a prioritized plan for the upcoming week.

## Demo flow

1. Open the web dashboard and show connected academic workflows.
2. Show recent coding activity and GitHub progress in the UI.
3. Run the advisor update workflow and open the drafted email result card.
4. Run the paper scout workflow and show the reading list update in the UI.
5. Trigger a deadline reminder flow.
6. Generate the Sunday week plan and show the summary plus outbound message result.

Judge takeaway:

"This isn't just an assistant. It's an academic operations layer that keeps a grad student's work life in sync."

## Current repo contents

- `app.py`: Ara starter automation entrypoint
- `frontend/`: planned webapp UI
- `backend/`: planned API layer between UI and workflows
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

## Product doc

The main build spec lives here:

- [docs/prd-grad-student-survival-agent.md](./docs/prd-grad-student-survival-agent.md)

## Next steps

1. Refactor `app.py` from the earlier starter concept into the Grad Student Survival Agent flows.
2. Scaffold a frontend dashboard and a thin backend API for workflow triggers and result cards.
3. Create integration modules for WakaTime, GitHub, Todoist, Calendar, Gmail, and research search.
4. Add local state files to prevent duplicate alerts and repeated paper recommendations.
5. Implement one reliable outbound message channel, with Telegram as the safest fallback if WhatsApp is unavailable.
