# Parallel You

An Ara-powered AI personal computer that acts like your always-on chief of staff.

Instead of waiting for prompts, it keeps lightweight memory, tracks open obligations, and turns messy context into one clear next action, one drafted message, and one risk to avoid.

## Why this can win

- It fits Ara's strongest features: persistent runtime, tools, automations, and phone/web access.
- It demos well in 2-3 minutes because judges can see proactive behavior, not just chat.
- It feels personally useful, which helps for both `Overall Winner` and `Most Viral`.
- It is still technical under the hood because it uses structured memory, task state, and background runs.

## Core pitch

"Your AI computer should not just answer questions. It should quietly run in the background and move your life forward."

Parallel You ingests your messy personal context, remembers what matters, and proactively helps you execute:

- notes
- tasks
- deadlines
- draft messages
- follow-ups
- decision support

## MVP for the hackathon

Build only these 4 pieces:

1. Intake memory
   Drop in notes, goals, deadlines, and raw context.
2. Personal dashboard
   Generate a "next best action" from the saved context.
3. Proactive follow-up
   Run on a schedule and surface one reminder, one draft, or one warning.
4. Ara-native automation
   Use `ara.Automation(...)` plus custom tools, so the project feels like a real AI computer instead of a web wrapper.

## Fast demo script

1. Add messy context:
   "I have a hackathon demo at 5, need to text my teammate, finish slides, and submit by 6."
2. Ask the agent what matters most.
3. Show the dashboard output with:
   - next action
   - urgent tasks
   - deadlines at risk
4. Add a new task live and rerun.
5. End by saying Ara can keep running this in the background and ping you from your phone.

## Project structure

- `app.py`: Ara SDK starter automation
- `docs/ideas.md`: ranked hackathon concepts
- `docs/prd-grad-student-survival-agent.md`: detailed product requirements for the finalized concept
- `requirements.txt`: Python dependency

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ara setup

According to the current Ara docs:

- install with `pip install ara-sdk`
- authenticate with `ara auth login`
- run once with `ara run app.py`
- deploy a scheduled automation with `ara deploy app.py --cron "*/5 * * * *"`

Reference docs:

- [Ara SDK Quickstart](https://docs.ara.so/sdk/quickstart)
- [Ara SDK Reference](https://docs.ara.so/sdk/reference/modal)
- [Ara Python SDK repo](https://github.com/Aradotso/ara-python-sdk/)

## Recommended next build steps

1. Add a tiny frontend later only if you need it for demo polish.
2. Keep the real magic in the Ara automation and tools.
3. Optimize for one memorable outcome:
   "It remembered my chaos and turned it into action."
