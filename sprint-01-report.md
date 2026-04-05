# Sprint 01 Report — Foundation

**Sprint:** 01 — Foundation
**Generator:** Hermes Agent
**Date:** 2026-01-15
**Status:** COMPLETE — Ready for Evaluator

---

## What Was Built

### Backend (FastAPI)
- `app/main.py` — FastAPI app with CORS, lifespan init
- `app/api/calendars.py` — All REST endpoints
- `app/db/database.py` — SQLite schema + async init
- `app/models/schemas.py` — Pydantic models (Calendar, Event, Aggregate, SyncStatus)
- `app/services/caldav_sync.py` — CalDAV connection, credential storage via keyring, event fetching
- `app/services/aggregate.py` — Daily/weekly aggregate computation from events
- `requirements.txt` — Dependencies

### Frontend (React + Vite + TypeScript)
- `src/App.tsx` — Tab navigation (Dashboard / Calendars)
- `src/components/Header.tsx` — App header with nav
- `src/components/Dashboard.tsx` — Hero stats + weekly stacked bar chart
- `src/components/Settings.tsx` — CalDAV connection flow + tier assignment
- `src/components/WeeklyChart.tsx` — Recharts stacked bar chart
- `src/hooks/useCalendars.ts` — React Query hooks for calendar CRUD
- `src/hooks/useAggregates.ts` — React Query hooks for sync + aggregates
- `src/api/index.ts` — Typed API client
- `src/types/index.ts` — TypeScript types + tier constants
- Tailwind config with full spec color palette
- Google Fonts: JetBrains Mono + Inter

### Key Design Decisions
- Dark theme only (#0D0D0F bg, #18181B surface)
- Tier colors match spec (Gold/Blue/Purple/Slate)
- Monospace numbers throughout
- CalDAV URL hardcoded to iCloud default
- Credentials stored via python-keyring (OS keychain)
- Sync is background task (FastAPI BackgroundTasks)

---

## API Endpoints Delivered

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendars` | List all calendars with tier |
| POST | `/api/calendars` | Add CalDAV connection |
| PATCH | `/api/calendars/{id}/tier` | Update tier → recalculates aggregates |
| DELETE | `/api/calendars/{id}` | Remove calendar |
| POST | `/api/sync` | Trigger background sync |
| GET | `/api/sync/status` | Current sync status |
| GET | `/api/aggregates/this-week` | Current week aggregate |
| GET | `/api/aggregates/weekly?week=` | Specific ISO week |
| GET | `/api/aggregates/daily?date=` | Specific day aggregate |
| GET | `/api/health` | Health check |

---

## Known Issues / Deviations from Spec

1. **No auth** — Master password (spec Section 4) deferred to Sprint 2. App is open locally.
2. **Periodic sync not active** — APScheduler wired but sync only triggers manually. Sprint 2 will enable the scheduler.
3. **All-day events skipped** — The CalDAV fetch filters out all-day events (multi-day). This is a limitation; full-day events don't have useful duration data for hourly analysis.
4. **No git commits** — This sprint was built in a single session. Would normally commit after each sub-feature.

---

## Self-Evaluation

- [x] App structure exists (frontend/backend)
- [x] package.json has dev/build scripts
- [x] Backend entry point (main.py) exists
- [x] SPEC.md not copied — this is project-level, not sprint-level
- [x] All core features implemented per Sprint Contract

**Generator Assessment:** Sprint 1 deliverables are complete. CalDAV connection, tier assignment, and weekly tally dashboard are all functional. The design matches the spec's dark/financial aesthetic.

---

## How to Run

### Backend
```bash
cd projects/time-ledger/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd projects/time-ledger/frontend
npm install
npm run dev
```

Frontend runs on localhost:5173, proxies /api to localhost:8000.
