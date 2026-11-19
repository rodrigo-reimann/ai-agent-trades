"""Command line tools.

    python -m homeconfirm seed                    # build the fake world
    python -m homeconfirm jobs                    # list tomorrow's jobs
    python -m homeconfirm jobs --date 2026-11-24  # list jobs on any day
"""
import argparse
from datetime import date, timedelta

from homeconfirm import clock, db
from homeconfirm.connectors import get_calendar
from homeconfirm.seed import seed


def cmd_seed(args) -> None:
    appointments = seed()
    print(f"Seeded {len(appointments)} appointments. Try: python -m homeconfirm jobs")


def cmd_jobs(args) -> None:
    conn = db.connect()
    contractor = db.get_contractor(conn)
    if contractor is None:
        print("No data yet. Run: python -m homeconfirm seed")
        return

    day = date.fromisoformat(args.date) if args.date else clock.today() + timedelta(days=1)
    jobs = get_calendar(contractor).get_appointments(day)

    print()
    print(f"  {contractor.business_name}  |  {day:%A, %B %d}  |  {len(jobs)} jobs")
    print()
    print(f"  {'TIME':<13} {'CUSTOMER':<16} {'PHONE':<13} {'ADDRESS':<38} {'JOB':<34} STATUS")
    print(f"  {'-' * 125}")
    for a in jobs:
        when = f"{a.start:%H:%M}-{a.end:%H:%M}"
        print(f"  {when:<13} {a.customer_name:<16} {a.customer_phone:<13} {a.address:<38} {a.job:<34} {a.status.value}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(prog="homeconfirm", description="Home-Confirm agent tools")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("seed", help="Reset and create the fake contractor, customers and jobs")

    jobs = sub.add_parser("jobs", help="List jobs (tomorrow by default)")
    jobs.add_argument("--date", help="YYYY-MM-DD (default: tomorrow)")

    args = parser.parse_args()
    {"seed": cmd_seed, "jobs": cmd_jobs}[args.command](args)


if __name__ == "__main__":
    main()
