import urllib.request, json

url = "http://localhost:8000/api/aggregates/this-week"
with urllib.request.urlopen(url, timeout=10) as resp:
    d = json.loads(resp.read())

print(f'Week: {d["week"]}, Range: {d["start_date"]} to {d["end_date"]}')
print(f'Grand total: {d["grand_total_minutes"]/60:.1f}hrs')
for tier, data in d.get('totals', {}).items():
    print(f'  {tier}: {data["minutes"]}min ({data["hours"]}hrs)')
active_days = sum(1 for day in d["daily_breakdown"].values() for v in day.values() if v > 0)
print(f'Days with data: {active_days}')

# Also check W14
import urllib.request, json
url2 = "http://localhost:8000/api/aggregates/weekly?week=2026-W14"
with urllib.request.urlopen(url2, timeout=10) as resp:
    d2 = json.loads(resp.read())
print(f'\nW14 (Mar 30-Apr 05): {d2["grand_total_minutes"]/60:.1f}hrs total')
for tier, data in d2.get('totals', {}).items():
    print(f'  {tier}: {data["minutes"]}min')