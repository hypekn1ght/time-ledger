import aiosqlite
import os
from pathlib import Path

DATABASE_PATH = os.environ.get("DATABASE_PATH", str(Path(__file__).parent.parent.parent / "timeledger.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    caldav_url TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'Routine',
    is_connected INTEGER NOT NULL DEFAULT 0,
    last_sync TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calendar_id INTEGER NOT NULL,
    apple_event_id TEXT NOT NULL,
    summary TEXT,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    synced_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (calendar_id) REFERENCES calendars(id),
    UNIQUE(calendar_id, apple_event_id)
);

CREATE TABLE IF NOT EXISTS daily_aggregates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    tier TEXT NOT NULL,
    total_minutes INTEGER NOT NULL DEFAULT 0,
    event_count INTEGER NOT NULL DEFAULT 0,
    UNIQUE(date, tier)
);

CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    events_synced INTEGER DEFAULT 0,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_calendar ON events(calendar_id);
CREATE INDEX IF NOT EXISTS idx_events_start ON events(start);
CREATE INDEX IF NOT EXISTS idx_aggregates_date ON daily_aggregates(date);
"""

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()

async def get_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
