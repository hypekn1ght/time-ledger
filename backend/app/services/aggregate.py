from datetime import date, datetime, timedelta
from dateutil import parser as dateparser
from typing import Optional
import aiosqlite
import logging

logger = logging.getLogger(__name__)

async def recalculate_daily_aggregates(db: aiosqlite.Connection, start_date: date, end_date: date):
    """
    Recalculate daily_aggregates from raw events for the given date range.
    This is called after sync and when tier assignments change.
    """
    cursor = await db.execute("""
        SELECT 
            date(e.start, 'unixepoch', 'localtime') as day,
            c.tier,
            SUM((julianday(e.end) - julianday(e.start)) * 1440) as total_minutes,
            COUNT(*) as event_count
        FROM events e
        JOIN calendars c ON e.calendar_id = c.id
        WHERE date(e.start, 'unixepoch', 'localtime') BETWEEN ? AND ?
        GROUP BY day, c.tier
    """, (start_date.isoformat(), end_date.isoformat()))
    rows = await cursor.fetchall()
    
    for row in rows:
        day_str, tier, total_minutes, event_count = row
        await db.execute("""
            INSERT INTO daily_aggregates (date, tier, total_minutes, event_count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date, tier) DO UPDATE SET
                total_minutes = excluded.total_minutes,
                event_count = excluded.event_count
        """, (day_str, tier, int(total_minutes) if total_minutes else 0, event_count))
    
    await db.commit()

async def recalculate_all_aggregates(db: aiosqlite.Connection):
    """Recalculate all aggregates from scratch."""
    # Get date range from events
    cursor = await db.execute("SELECT MIN(date(start, 'unixepoch', 'localtime')), MAX(date(start, 'unixepoch', 'localtime')) FROM events")
    row = await cursor.fetchone()
    if row and row[0] and row[1]:
        start = dateparser.parse(row[0]).date()
        end = dateparser.parse(row[1]).date()
        await recalculate_daily_aggregates(db, start, end)

def get_week_string(d: date) -> str:
    """Return ISO week string YYYY-Www."""
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"

async def get_weekly_aggregate(db: aiosqlite.Connection, week_str: str) -> dict:
    """
    Get weekly aggregate for a given ISO week string (e.g., '2026-W03').
    Returns tier breakdown with daily breakdown.
    """
    # Parse week string to date range
    year, week = week_str.split("-W")
    jan4 = date(int(year), 1, 4)
    start_of_week = jan4 + timedelta(weeks=int(week) - 1, days=jan4.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    cursor = await db.execute("""
        SELECT tier, SUM(total_minutes) as total_minutes, SUM(event_count) as event_count
        FROM daily_aggregates
        WHERE date BETWEEN ? AND ?
        GROUP BY tier
    """, (start_of_week.isoformat(), end_of_week.isoformat()))
    tier_rows = await cursor.fetchall()
    
    # Get daily breakdown
    cursor = await db.execute("""
        SELECT date, tier, total_minutes
        FROM daily_aggregates
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """, (start_of_week.isoformat(), end_of_week.isoformat()))
    daily_rows = await cursor.fetchall()
    
    # Build daily breakdown dict
    daily_breakdown = {}
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        daily_breakdown[day.isoformat()] = {"$1000/hr": 0, "$100/hr": 0, "Learning": 0, "Routine": 0}
    
    for row in daily_rows:
        day_str, tier, minutes = row
        if day_str in daily_breakdown:
            daily_breakdown[day_str][tier] = minutes
    
    result = {
        "week": week_str,
        "start_date": start_of_week.isoformat(),
        "end_date": end_of_week.isoformat(),
        "totals": {},
        "grand_total_minutes": 0,
        "daily_breakdown": daily_breakdown
    }
    
    for row in tier_rows:
        tier, total_minutes, event_count = row
        result["totals"][tier] = {
            "minutes": total_minutes,
            "hours": round(total_minutes / 60, 1),
            "event_count": event_count
        }
        result["grand_total_minutes"] += total_minutes
    
    return result

async def get_daily_aggregate(db: aiosqlite.Connection, target_date: date) -> dict:
    """Get aggregate for a specific day."""
    cursor = await db.execute("""
        SELECT tier, total_minutes, event_count
        FROM daily_aggregates
        WHERE date = ?
    """, (target_date.isoformat(),))
    rows = await cursor.fetchall()
    
    result = {
        "date": target_date.isoformat(),
        "totals": {"$1000/hr": {"minutes": 0, "hours": 0}, "$100/hr": {"minutes": 0, "hours": 0}, 
                  "Learning": {"minutes": 0, "hours": 0}, "Routine": {"minutes": 0, "hours": 0}},
        "grand_total_minutes": 0
    }
    
    for row in rows:
        tier, minutes, event_count = row
        result["totals"][tier] = {"minutes": minutes, "hours": round(minutes / 60, 1), "event_count": event_count}
        result["grand_total_minutes"] += minutes
    
    return result
