# Time Ledger

Apple Calendar Analyzer — track how you spend time across four value tiers.

## Tiers

| Tier | Value | Description |
|------|-------|-------------|
| **$1000/hr** | $1,000/hr | High-value client work, premium engagements |
| **$100/hr** | $100/hr | Standard work, meetings, collaboration |
| **Learning** | — | Courses, reading, skill development |
| **Routine** | — | Admin, email, low-value tasks |

## Tech Stack

- **Backend:** FastAPI + SQLite + icloud-caldav
- **Frontend:** React 18 + Vite + TypeScript + Tailwind + Recharts
- **Deployment:** Vercel (frontend) + Tailscale (backend tunnel)

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start
cd ..
./start-backend.sh
# Or directly:
cd backend && ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # Local dev
npm run build    # Production build
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `./timeledger.db` | SQLite database path |

## Architecture

```
backend/
├── app/
│   ├── main.py           # FastAPI app + CORS
│   ├── api/calendars.py  # REST endpoints
│   ├── db/database.py    # SQLite schema + init
│   ├── models/schemas.py # Pydantic models
│   └── services/
│       ├── caldav_sync.py # CalDAV connection + event fetch
│       └── aggregate.py   # Daily/weekly aggregate computation
└── requirements.txt

frontend/
├── src/
│   ├── App.tsx
│   ├── components/
│   │   ├── Dashboard.tsx    # Hero stats + chart
│   │   ├── WeeklyChart.tsx  # Stacked bar chart
│   │   └── Settings.tsx     # CalDAV connection UI
│   ├── hooks/
│   │   ├── useCalendars.ts   # Calendar CRUD
│   │   └── useAggregates.ts  # Sync + aggregates
│   ├── api/index.ts          # API client
│   └── types/index.ts        # TypeScript types
├── vercel.json              # Rewrites /api → backend
└── tailwind.config.js
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendars` | List calendars |
| POST | `/api/calendars` | Add CalDAV connection |
| PATCH | `/api/calendars/{id}/tier` | Update tier |
| DELETE | `/api/calendars/{id}` | Remove calendar |
| POST | `/api/sync` | Trigger sync |
| GET | `/api/sync/status` | Sync status |
| GET | `/api/aggregates/this-week` | Current week |
| GET | `/api/aggregates/weekly?week=` | ISO week |
| GET | `/api/aggregates/daily?date=` | Day aggregate |

## License

MIT
