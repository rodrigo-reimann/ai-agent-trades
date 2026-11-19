"""The app's single source of "what time is it".

Everything asks this module for the time instead of calling datetime.now()
directly. That way the demo clock (Milestone 5) can fast-forward time in one place.
"""
from datetime import date, datetime

from homeconfirm.config import TZ


def now() -> datetime:
    return datetime.now(TZ)


def today() -> date:
    return now().date()
