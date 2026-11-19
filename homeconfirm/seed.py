"""Builds the fake world: one contractor, six customers, tomorrow's jobs.

Run it any day; the jobs are always placed on "tomorrow" relative to today
(BC time), so the demo works whenever you film it. Running it again wipes
everything and starts fresh.
"""
from datetime import datetime, time, timedelta

from homeconfirm import clock, db
from homeconfirm.config import TZ
from homeconfirm.connectors import get_calendar
from homeconfirm.models import Appointment, Contractor, Customer

CONTRACTOR = Contractor(
    name="Ryan",
    phone="+16045550199",
    business_name="Sea to Sky Plumbing & Heating",
    work_start=time(8, 0),
    work_end=time(17, 0),
)

# 555-01xx numbers are reserved for fiction, so nobody real gets texted.
# (name, phone, address, start, end, job)
TOMORROWS_JOBS = [
    ("Sarah Chen",      "+16045550101", "40 Highlands Way S, Squamish",           "08:00", "09:00", "a leaky kitchen faucet"),
    ("Dave Jones",      "+16045550102", "123 Main St, Squamish",                  "09:00", "11:00", "a hot water tank replacement"),
    ("Priya Sandhu",    "+16045550103", "1820 Depot Rd, Brackendale",             "11:30", "12:30", "a toilet that won't stop running"),
    ("Tom Kowalski",    "+16045550104", "2970 Lynn Valley Rd, North Vancouver",   "13:30", "15:00", "a new bathroom sink install"),
    ("Linda MacDonald", "+16045550105", "455 E 4th St, North Vancouver",          "15:15", "16:00", "a furnace that won't light"),
    ("Jordan Lee",      "+16045550106", "2400 Marine Dr, West Vancouver",         "16:15", "17:00", "a leaking outdoor hose bib"),
]

# A few jobs later in the week so the calendar isn't empty when we reschedule (M4).
# (working days after tomorrow, name, phone, address, start, end, job)
LATER_JOBS = [
    (1, "Gord Thompson",  "+16045550107", "38100 Westway Ave, Squamish",       "09:00", "12:00", "a water heater install"),
    (1, "Mei Wong",       "+16045550108", "1500 Lonsdale Ave, North Vancouver", "13:00", "15:00", "a drain clean-out"),
    (2, "Gord Thompson",  "+16045550107", "38100 Westway Ave, Squamish",       "08:00", "10:00", "a follow-up inspection"),
    (3, "Ali Rezaei",     "+16045550109", "720 Esplanade Ave, North Vancouver", "10:00", "13:00", "a boiler service"),
]


def _at(day, hhmm: str) -> datetime:
    return datetime.combine(day, time.fromisoformat(hhmm), tzinfo=TZ)


def _working_day_after(day, n: int):
    """The n-th working day after `day` (skips weekends)."""
    while n > 0:
        day += timedelta(days=1)
        if day.weekday() in CONTRACTOR.work_days:
            n -= 1
    return day


def seed() -> list[Appointment]:
    conn = db.connect()
    db.reset(conn)
    db.save_contractor(conn, CONTRACTOR)

    tomorrow = clock.today() + timedelta(days=1)
    appointments = []

    for i, (name, phone, address, start, end, job) in enumerate(TOMORROWS_JOBS, start=1):
        db.save_customer(conn, Customer(name, phone))
        appointments.append(Appointment(f"apt-{i:03d}", name, phone, address,
                                        _at(tomorrow, start), _at(tomorrow, end), job))

    for i, (n, name, phone, address, start, end, job) in enumerate(LATER_JOBS, start=101):
        day = _working_day_after(tomorrow, n)
        db.save_customer(conn, Customer(name, phone))
        appointments.append(Appointment(f"apt-{i:03d}", name, phone, address,
                                        _at(day, start), _at(day, end), job))

    get_calendar(CONTRACTOR).replace_all(appointments)
    db.log_event(conn, "seeded", jobs_tomorrow=len(TOMORROWS_JOBS), jobs_later=len(LATER_JOBS))
    conn.close()
    return appointments
