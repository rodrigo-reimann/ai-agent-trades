"""Tests for the FakeCalendarConnector. Run with: pytest"""
from datetime import date, datetime, time, timedelta

import pytest

from homeconfirm.config import TZ
from homeconfirm.connectors.base import SlotTakenError
from homeconfirm.connectors.fake_calendar import FakeCalendarConnector
from homeconfirm.models import Appointment, Contractor, Slot, Status

# A Wednesday far in the future, so "is this slot in the past?" never trips.
DAY = date(2030, 6, 5)


def at(hhmm, day=DAY):
    return datetime.combine(day, time.fromisoformat(hhmm), tzinfo=TZ)


@pytest.fixture
def cal(tmp_path):
    contractor = Contractor("Ryan", "+16045550199", "Test Plumbing", time(8), time(12))
    c = FakeCalendarConnector(tmp_path / "cal.json", contractor)
    c.replace_all([
        Appointment("a1", "Sarah", "+1", "1 Main St", at("09:00"), at("10:00"), "faucet"),
        Appointment("a2", "Dave", "+2", "2 Main St", at("10:30"), at("11:30"), "tank"),
    ])
    return c


def test_get_appointments_sorted_by_time(cal):
    jobs = cal.get_appointments(DAY)
    assert [a.id for a in jobs] == ["a1", "a2"]
    assert cal.get_appointments(DAY + timedelta(days=1)) == []


def test_open_slots_skip_booked_times(cal):
    slots = cal.find_open_slots((DAY, DAY), timedelta(hours=1))
    starts = [s.start.strftime("%H:%M") for s in slots]
    # Working 8-12; booked 9-10 and 10:30-11:30.
    assert starts == ["08:00"]


def test_open_slots_skip_weekends(cal):
    saturday = date(2030, 6, 8)
    assert cal.find_open_slots((saturday, saturday), timedelta(hours=1)) == []


def test_move_appointment(cal):
    moved = cal.move_appointment("a1", Slot(at("08:00", DAY + timedelta(days=1)), at("09:00", DAY + timedelta(days=1))))
    assert moved.start.date() == DAY + timedelta(days=1)
    assert [a.id for a in cal.get_appointments(DAY)] == ["a2"]  # saved to the file


def test_move_into_booked_slot_is_refused(cal):
    with pytest.raises(SlotTakenError):
        cal.move_appointment("a1", Slot(at("11:00"), at("12:00")))


def test_cancelled_jobs_free_up_their_slot(cal):
    cal.mark_status("a2", Status.CANCELLED)
    starts = [s.start.strftime("%H:%M") for s in cal.find_open_slots((DAY, DAY), timedelta(hours=1))]
    assert "10:30" in starts


def test_mark_status(cal):
    cal.mark_status("a1", Status.CONFIRMED)
    assert cal.get_appointments(DAY)[0].status == Status.CONFIRMED
