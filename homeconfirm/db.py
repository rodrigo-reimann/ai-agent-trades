"""SQLite storage: contractor, customers, and the events log.

Appointments live in the calendar (via a CalendarConnector), not here.
"""
import json
import sqlite3
from datetime import time

from homeconfirm import clock, config
from homeconfirm.models import Contractor, Customer

SCHEMA = """
CREATE TABLE IF NOT EXISTS contractor (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    phone         TEXT NOT NULL,
    business_name TEXT NOT NULL,
    work_start    TEXT NOT NULL,   -- "08:00"
    work_end      TEXT NOT NULL,   -- "17:00"
    work_days     TEXT NOT NULL    -- JSON list, Mon=0
);

CREATE TABLE IF NOT EXISTS customers (
    phone      TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    opted_out  INTEGER NOT NULL DEFAULT 0
);

-- Every message, classification and action gets a row here.
CREATE TABLE IF NOT EXISTS events (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    ts             TEXT NOT NULL,   -- ISO time, America/Vancouver
    appointment_id TEXT,
    kind           TEXT NOT NULL,   -- e.g. "seeded", "sms_out", "sms_in", "classified"
    detail         TEXT             -- JSON
);
"""


def connect(path=None) -> sqlite3.Connection:
    path = path or config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def reset(conn: sqlite3.Connection) -> None:
    conn.executescript("DROP TABLE IF EXISTS contractor; DROP TABLE IF EXISTS customers; DROP TABLE IF EXISTS events;")
    conn.executescript(SCHEMA)


def log_event(conn, kind: str, appointment_id: str | None = None, **detail) -> None:
    conn.execute(
        "INSERT INTO events (ts, appointment_id, kind, detail) VALUES (?, ?, ?, ?)",
        (clock.now().isoformat(timespec="seconds"), appointment_id, kind, json.dumps(detail)),
    )
    conn.commit()


# --- contractor ---

def save_contractor(conn, c: Contractor) -> None:
    conn.execute("DELETE FROM contractor")
    conn.execute(
        "INSERT INTO contractor (id, name, phone, business_name, work_start, work_end, work_days) "
        "VALUES (1, ?, ?, ?, ?, ?, ?)",
        (c.name, c.phone, c.business_name, c.work_start.strftime("%H:%M"),
         c.work_end.strftime("%H:%M"), json.dumps(c.work_days)),
    )
    conn.commit()


def get_contractor(conn) -> Contractor | None:
    row = conn.execute("SELECT * FROM contractor WHERE id = 1").fetchone()
    if row is None:
        return None
    return Contractor(
        name=row["name"],
        phone=row["phone"],
        business_name=row["business_name"],
        work_start=time.fromisoformat(row["work_start"]),
        work_end=time.fromisoformat(row["work_end"]),
        work_days=json.loads(row["work_days"]),
    )


# --- customers ---

def save_customer(conn, c: Customer) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO customers (phone, name, opted_out) VALUES (?, ?, ?)",
        (c.phone, c.name, int(c.opted_out)),
    )
    conn.commit()


def get_customer(conn, phone: str) -> Customer | None:
    row = conn.execute("SELECT * FROM customers WHERE phone = ?", (phone,)).fetchone()
    if row is None:
        return None
    return Customer(name=row["name"], phone=row["phone"], opted_out=bool(row["opted_out"]))
