import sqlite3

conn = sqlite3.connect("timeledger.db")
conn.row_factory = sqlite3.Row
cur = conn.execute('SELECT MIN(date(start, "unixepoch", "localtime")), MAX(date(start, "unixepoch", "localtime")) FROM events')
row = cur.fetchone()
print(f"Events range: {row[0]} to {row[1]}")
cur2 = conn.execute("SELECT COUNT(*) FROM events")
print(f"Total events: {cur2.fetchone()[0]}")
cur3 = conn.execute("SELECT date, tier, total_minutes FROM daily_aggregates ORDER BY date DESC LIMIT 20")
print("Recent aggregates:")
for row in cur3.fetchall():
    print(f"  {row[0]} {row[1]} {row[2]}min")
conn.close()