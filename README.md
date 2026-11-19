# Home-Confirm

An AI agent for small trades contractors (plumbers, HVAC, electricians, handymen) in BC.
It makes sure the customer is actually **home** for the appointment. It reads messy replies,
reschedules, chases people who don't answer, and warns the contractor *before* he drives to an empty house.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

## Milestone 1: skeleton + fake world

```bash
python -m homeconfirm seed       # creates 1 contractor, 6 customers, tomorrow's jobs
python -m homeconfirm jobs       # lists tomorrow's jobs
python -m homeconfirm jobs --date 2026-11-23
pytest                           # runs the tests
```

`seed` always puts the 6 jobs on **tomorrow** (BC time), so the demo works whatever day you film.
It also adds a few jobs later in the week so rescheduling has something to work around.
Open `data/fake_calendar.json` to see or hand-edit the "calendar".

## How it's built

```
homeconfirm/
  config.py          settings from .env, timezone (America/Vancouver)
  clock.py           the one place that knows "now" (demo clock plugs in here)
  models.py          Contractor, Customer, Appointment, Slot, Status
  db.py              SQLite: contractor, customers, events log
  seed.py            the fake world
  cli.py             command-line tools
  connectors/
    base.py          CalendarConnector: the only way the agent touches a calendar
    fake_calendar.py FakeCalendarConnector (JSON file)
```

**Where data lives:** the calendar is the source of truth for jobs (time, address, customer phone, status).
SQLite holds the contractor, customers (including opt-outs) and the `events` log, which records every message and action with a timestamp.

**Adding a calendar** (Google, Jobber, ...): write one file in `connectors/` with a class that
inherits `CalendarConnector` and fills in its 4 methods, then add one line to `connectors/__init__.py`.
