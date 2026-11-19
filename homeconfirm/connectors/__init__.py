"""Pick the calendar connector based on CALENDAR_PROVIDER in .env."""
from homeconfirm import config
from homeconfirm.connectors.base import CalendarConnector, SlotTakenError
from homeconfirm.models import Contractor


def get_calendar(contractor: Contractor) -> CalendarConnector:
    if config.CALENDAR_PROVIDER == "fake":
        from homeconfirm.connectors.fake_calendar import FakeCalendarConnector
        return FakeCalendarConnector(config.FAKE_CALENDAR_PATH, contractor)
    raise ValueError(f"Unknown CALENDAR_PROVIDER: {config.CALENDAR_PROVIDER!r}")


__all__ = ["CalendarConnector", "SlotTakenError", "get_calendar"]
