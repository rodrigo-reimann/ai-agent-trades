"""The basic things the app talks about. Plain dataclasses, no magic."""
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum


class Status(str, Enum):
    SCHEDULED = "scheduled"
    REMINDER_SENT = "reminder_sent"
    CONFIRMED = "confirmed"
    RESCHEDULE_REQUESTED = "reschedule_requested"
    QUESTION = "question"
    NO_REPLY = "no_reply"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"
    ON_THE_WAY = "on_the_way"
    COMPLETED = "completed"


@dataclass
class Contractor:
    name: str
    phone: str
    business_name: str
    work_start: time = time(8, 0)
    work_end: time = time(17, 0)
    work_days: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Mon=0 ... Fri=4


@dataclass
class Customer:
    name: str
    phone: str
    opted_out: bool = False


@dataclass
class Slot:
    start: datetime
    end: datetime


@dataclass
class Appointment:
    id: str
    customer_name: str
    customer_phone: str
    address: str
    start: datetime
    end: datetime
    job: str
    status: Status = Status.SCHEDULED

    def overlaps(self, slot: Slot) -> bool:
        return self.start < slot.end and slot.start < self.end
