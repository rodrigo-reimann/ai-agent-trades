"""The calendar interface.

The agent ONLY talks to calendars through this class. To support a new calendar
(Google, Jobber, Housecall Pro...), write one new file with a class that
inherits from CalendarConnector and fills in these four methods.
"""
from abc import ABC, abstractmethod
from datetime import date, timedelta

from homeconfirm.models import Appointment, Slot, Status


class SlotTakenError(Exception):
    """Raised when you try to move a job into a time that's already booked."""


class CalendarConnector(ABC):

    @abstractmethod
    def get_appointments(self, day: date) -> list[Appointment]:
        """All appointments on this day, sorted by start time."""

    @abstractmethod
    def find_open_slots(self, date_range: tuple[date, date], duration: timedelta) -> list[Slot]:
        """Free slots of `duration` inside working hours, between two dates (inclusive)."""

    @abstractmethod
    def move_appointment(self, appointment_id: str, new_slot: Slot) -> Appointment:
        """Move a job to a new slot. Raises SlotTakenError if the slot isn't free."""

    @abstractmethod
    def mark_status(self, appointment_id: str, status: Status) -> None:
        """Record where this job is in the confirmation process."""
