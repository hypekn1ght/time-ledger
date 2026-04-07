import sqlite3

conn = sqlite3.connect("timeledger.db")
conn.row_factory = sqlite3.Row

# Check what the aggregate.py formula gives vs actual isocalendar
from datetime import date, timedelta

def get_week_string_buggy(d):
    iso = d.isocalendar()
    year, week = iso.year, iso.week
    jan4 = date(year, 1, 4)
    start_of_week = jan4 + timedelta(weeks=week - 1, days=jan4.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week, f"W{week:02d}"

# Check all days with events
cur = conn.execute("""
    SELECT DISTINCT date(start, 'unixepoch', 'localtime') as day
    FROM events
    ORDER BY day
""")
rows = cur.fetchall()
print("All event days and their calculated week ranges:")
for row in rows:
    day_str = row[0]
    d = date.fromisoformat(day_str)
    start, end, week = get_week_string_buggy(d)
    print(f"  {day_str} ({d.strftime('%A')}) -> {week}: {start} to {end}")

# Also check where April 7 events fall
cur2 = conn.execute("""
    SELECT date, tier, SUM(total_minutes) as mins
    FROM daily_aggregates
    WHERE date >= '2026-04-01'
    GROUP BY date, tier
    ORDER BY date
""")
print("\nApril aggregates:")
for row in cur2.fetchall():
    print(f"  {row[0]} {row[1]} {row[2]}min")
conn.close()