from datetime import date, timedelta

def get_week_range_fixed(week_str):
    year, week = week_str.split("-W")
    year, week = int(year), int(week)
    jan4 = date(year, 1, 4)
    monday_week1 = jan4 - timedelta(days=jan4.weekday())
    start_of_week = monday_week1 + timedelta(weeks=week - 1)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

# Verify all weeks now match isocalendar
known_weeks = ["2026-W02", "2026-W03", "2026-W04", "2026-W05", "2026-W06",
               "2026-W07", "2026-W08", "2026-W09", "2026-W10", "2026-W11",
               "2026-W12", "2026-W13", "2026-W14", "2026-W15"]

print("Week | Fixed Start | Fixed End | Correct ISO Start | OK?")
for wk in known_weeks:
    fs, fe = get_week_range_fixed(wk)
    # isocalendar gives (year, week, weekday) — verify
    iso_correct = fs.isocalendar()
    year, iso_week = wk.split("-W")
    ok = "✓" if (iso_correct.year == int(year) and iso_correct.week == int(iso_week)) else "✗"
    print(f"{wk} | {fs} | {fe} | {fs.isocalendar()} | {ok}")

# Check: April 7 data should now be in W15 (2026-04-06 to 2026-04-12)
print("\nApril 2026 data with fixed range:")
print("W13 (Mar 23-29): 2026-03-23 to 2026-03-29")
print("W14 (Mar 30-Apr 05): 2026-03-30 to 2026-04-05")
print("W15 (Apr 06-12): 2026-04-06 to 2026-04-12")
print("\nApril 6-7 events should now appear in W15, not future W15")