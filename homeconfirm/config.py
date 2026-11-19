"""All settings in one place. Values come from the .env file (see .env.example)."""
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Everything in this app runs on BC time.
TZ = ZoneInfo("America/Vancouver")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")

CALENDAR_PROVIDER = os.getenv("CALENDAR_PROVIDER", "fake")

DB_PATH = PROJECT_ROOT / os.getenv("DB_PATH", "data/homeconfirm.db")
FAKE_CALENDAR_PATH = PROJECT_ROOT / os.getenv("FAKE_CALENDAR_PATH", "data/fake_calendar.json")
