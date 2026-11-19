"""A pretend calendar stored in a JSON file.

Open data/fake_calendar.json in any editor to see (or change) the jobs.
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from homeconfirm import clock
from homeconfirm.config import TZ
from homeconfirm.connectors.base import CalendarConnector, SlotTakenError
from homeconfirm.models import Appointment, Contractor, Slot, Status


class FakeCalendarConnector(CalendarConnector):

    def __init__(self, path: Path, contractor: Contractor):
        self.path = Path(path)
        self.contractor = contractor  # we need their working hours to find open slots

    # ---------- the four interface methods ----------

    def get_appointments(self, day: date) -> list[Appointment]:
        jobs = [a for a in self._load() if a.start.date() == day]
        return sorted(jobs, key=lambda a: a.start)

    def find_open_slots(self, date_range: tuple[date, date], duration: timedelta) -> list[Slot]:
        first_day, last_day = date_range
        booked = [a for a in self._load() if a.status != Status.CANCELLED]
        slots = []

        day = first_day
        while day <= last_day:
            if day.weekday() in self.contractor.work_days:
                start = datetime.combine(day, self.contractor.work_start, tzinfo=TZ)
                day_end = datetime.combine(day, self.contractor.work_end, tzinfo=TZ)
                # Try every start time on the hour or half hour.
                while start + duration <= day_end:
                    slot = Slot(start, start + duration)
                    in_future = slot.start > clock.now()
                    is_free = not any(a.overlaps(slot) for a in booked)
                    if in_future and is_free:
                        slots.append(slot)
                    start += timedelta(minutes=30)
            day += timedelta(days=1)
        return slots

    def move_appointment(self, appointment_id: str, new_slot: Slot) -> Appointment:
        appointments = self._load()
        job = self._find(appointments, appointment_id)
        others = [a for a in appointments if a.id != appointment_id and a.status != Status.CANCELLED]
        if any(a.overlaps(new_slot) for a in others):
            raise SlotTakenError(f"{new_slot.start:%a %b %d %H:%M} is already booked")
        job.start, job.end = new_slot.start, new_slot.end
        self._save(appointments)
        return job

    def mark_status(self, appointment_id: str, status: Status) -> None:
        appointments = self._load()
        self._find(appointments, appointment_id).status = Status(status)
        self._save(appointments)

    # ---------- extras used by the seed script ----------

    def replace_all(self, appointments: list[Appointment]) -> None:
        self._save(appointments)

    # ---------- reading / writing the JSON file ----------

    def _find(self, appointments, appointment_id) -> Appointment:
        for a in appointments:
            if a.id == appointment_id:
                return a
        raise KeyError(f"No appointment with id {appointment_id}")

    def _load(self) -> list[Appointment]:
        if not self.path.exists():
            return []
        rows = json.loads(self.path.read_text())["appointments"]
        return [
            Appointment(
                id=r["id"],
                customer_name=r["customer_name"],
                customer_phone=r["customer_phone"],
                address=r["address"],
                start=datetime.fromisoformat(r["start"]),
                end=datetime.fromisoformat(r["end"]),
                job=r["job"],
                status=Status(r["status"]),
            )
            for r in rows
        ]

    def _save(self, appointments: list[Appointment]) -> None:
        rows = [
            {
                "id": a.id,
                "customer_name": a.customer_name,
                "customer_phone": a.customer_phone,
                "address": a.address,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "job": a.job,
                "status": a.status.value,
            }
            for a in sorted(appointments, key=lambda a: a.start)
        ]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"appointments": rows}, indent=2))
