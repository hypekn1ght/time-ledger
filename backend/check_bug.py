from datetime import date, timedelta

def get_week_string(d):
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"

def get_week_range_actual(week_str):
    """Return the actual correct week range for an ISO week string."""
    year, week = week_str.split("-W")
    year, week = int(year), int(week)
    # ISO week 1 contains Jan 4, starts on Monday
    jan4 = date(year, 1, 4)
    # Find Monday of week 1
    monday_week1 = jan4 - timedelta(days=jan4.weekday())  # weekday Mon=0
    start_of_week = monday_week1 + timedelta(weeks=week - 1)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def get_week_range_buggy(week_str):
    """Return the buggy week range from aggregate.py."""
    year, week = week_str.split("-W")
    year, week = int(year), int(week)
    jan4 = date(year, 1, 4)
    start_of_week = jan4 + timedelta(weeks=week - 1, days=jan4.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

# Check all weeks that have data
known_weeks = ["2026-W02", "2026-W03", "2026-W04", "2026-W05", "2026-W06",
               "2026-W07", "2026-W08", "2026-W09", "2026-W10", "2026-W11",
               "2026-W12", "2026-W13", "2026-W14", "2026-W15"]

print("Week string | Buggy Start | Correct Start | Buggy End | Correct End")
print("-" * 80)
for wk in known_weeks:
    bs, be = get_week_range_buggy(wk)
    cs, ce = get_week_range_actual(wk)
    match = "✓" if bs == cs else "✗ BUG"
    print(f"{wk} | {bs} | {cs} | {be} | {ce} | {match}")

# Check: what week does April 7 actually belong to?
print(f"\nApril 7, 2026 is: {get_week_string(date(2026, 4, 7))}")
print(f"Buggy: April 7 in week {get_week_string(date(2026, 4, 7))} -> range {get_week_range_buggy('2026-W15')}")
print(f"Correct: April 7 in week {get_week_string(date(2026, 4, 7))} -> range {get_week_range_actual('2026-W15')}")

# What week is April 6 (Monday of W15)?
print(f"April 6 (Monday): {get_week_string(date(2026, 4, 6))}, range: {get_week_range_actual('2026-W15')}")

# Show March 30 (yesterday, Monday of W14) for reference
print(f"March 30 (Monday of W14): {get_week_string(date(2026, 3, 30))}")