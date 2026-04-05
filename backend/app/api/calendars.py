from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from dateutil import parser as dateparser
import aiosqlite

from ..models.schemas import (
    Calendar, CalendarCreate, CalendarTierUpdate, 
    ConnectionRequest, ConnectionResponse, SyncStatus
)
from ..db.database import DATABASE_PATH
from ..services import caldav_sync, aggregate

router = APIRouter(prefix="/api", tags=["calendars"])

# In-memory sync state (would be Redis/DB in production)
_sync_status = {
    "is_syncing": False,
    "last_sync": None,
    "last_error": None,
    "events_synced": 0
}

@router.get("/calendars", response_model=list[Calendar])
async def list_calendars():
    """List all configured calendars with their tiers."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, name, caldav_url, tier, is_connected, last_sync FROM calendars ORDER BY name"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

@router.post("/calendars", response_model=ConnectionResponse)
async def add_calendar(req: ConnectionRequest, background_tasks: BackgroundTasks):
    """Add a new CalDAV connection and sync calendars."""
    # Test connection first
    success, error, calendar_data = caldav_sync.test_connection(
        req.caldav_url, req.apple_id, req.apple_password
    )
    
    if not success:
        return ConnectionResponse(success=False, calendars=[], error=error)
    
    # Store credentials
    caldav_sync.store_credentials(req.caldav_url, req.apple_id, req.apple_password)
    
    # Save calendars to DB with default tier
    async with aiosqlite.connect(DATABASE_PATH) as db:
        saved_calendars = []
        for cal in calendar_data:
            # Check if already exists
            cursor = await db.execute(
                "SELECT id FROM calendars WHERE caldav_url = ? AND name = ?",
                (cal["caldav_url"], cal["name"])
            )
            existing = await cursor.fetchone()
            
            if not existing:
                # Suggest tier based on name
                tier = suggest_tier(cal["name"])
                await db.execute("""
                    INSERT INTO calendars (name, caldav_url, tier, is_connected)
                    VALUES (?, ?, ?, 1)
                """, (cal["name"], cal["caldav_url"], tier))
            else:
                # Update connection status
                await db.execute(
                    "UPDATE calendars SET is_connected = 1 WHERE id = ?", (existing[0],)
                )
        
        await db.commit()
        
        # Fetch saved calendars
        cursor = await db.execute(
            "SELECT id, name, caldav_url, tier, is_connected, last_sync FROM calendars WHERE is_connected = 1"
        )
        rows = await cursor.fetchall()
        saved_calendars = [dict(row) for row in rows]
    
    return ConnectionResponse(success=True, calendars=saved_calendars, error=None)

@router.patch("/calendars/{calendar_id}/tier", response_model=Calendar)
async def update_calendar_tier(calendar_id: int, update: CalendarTierUpdate):
    """Update the tier for a calendar. Triggers aggregate recalculation."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM calendars WHERE id = ?", (calendar_id,)
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Calendar not found")
        
        await db.execute(
            "UPDATE calendars SET tier = ? WHERE id = ?",
            (update.tier.value, calendar_id)
        )
        await db.commit()
        
        # Recalculate all aggregates (tier changed)
        await aggregate.recalculate_all_aggregates(db)
        
        cursor = await db.execute(
            "SELECT id, name, caldav_url, tier, is_connected, last_sync FROM calendars WHERE id = ?",
            (calendar_id,)
        )
        row = await cursor.fetchone()
        return dict(row)

@router.delete("/calendars/{calendar_id}")
async def delete_calendar(calendar_id: int):
    """Remove a calendar from sync."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT caldav_url FROM calendars WHERE id = ?", (calendar_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Calendar not found")
        
        # Don't remove credentials (might re-add)
        await db.execute("UPDATE calendars SET is_connected = 0 WHERE id = ?", (calendar_id,))
        await db.execute("DELETE FROM events WHERE calendar_id = ?", (calendar_id,))
        await db.commit()
    
    return {"success": True}

@router.post("/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    """Trigger a full CalDAV sync."""
    global _sync_status
    
    if _sync_status["is_syncing"]:
        return {"success": False, "error": "Sync already in progress"}
    
    _sync_status["is_syncing"] = True
    _sync_status["last_error"] = None
    
    background_tasks.add_task(do_sync)
    
    return {"success": True, "message": "Sync started"}

@router.get("/sync/status", response_model=SyncStatus)
async def get_sync_status():
    """Get current sync status."""
    return SyncStatus(**_sync_status)

async def do_sync():
    """Background sync task."""
    global _sync_status
    from ..services.caldav_sync import fetch_events, get_credentials
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                "SELECT id, name, caldav_url FROM calendars WHERE is_connected = 1"
            )
            calendars = await cursor.fetchall()
        
        total_events = 0
        for cal_id, cal_name, caldav_url in calendars:
            apple_id, apple_password = get_credentials(caldav_url)
            if not apple_id or not apple_password:
                continue
            
            events = fetch_events(caldav_url, caldav_url, apple_id, apple_password)
            
            async with aiosqlite.connect(DATABASE_PATH) as db:
                for event in events:
                    start_dt = dateparser.parse(event["start"])
                    end_dt = dateparser.parse(event["end"])
                    
                    # Skip all-day events (no useful duration data)
                    if (end_dt - start_dt).days >= 1:
                        continue
                    
                    await db.execute("""
                        INSERT OR REPLACE INTO events (calendar_id, apple_event_id, summary, start, end)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        cal_id,
                        event["apple_event_id"],
                        event["summary"],
                        start_dt.timestamp(),
                        end_dt.timestamp()
                    ))
                    total_events += 1
                
                await db.execute(
                    "UPDATE calendars SET last_sync = ? WHERE id = ?",
                    (datetime.now().isoformat(), cal_id)
                )
                await db.commit()
                
                # Recalculate aggregates
                await aggregate.recalculate_all_aggregates(db)
        
        _sync_status["last_sync"] = datetime.now()
        _sync_status["events_synced"] = total_events
        _sync_status["is_syncing"] = False
    except Exception as e:
        _sync_status["is_syncing"] = False
        _sync_status["last_error"] = str(e)

@router.get("/aggregates/weekly")
async def get_weekly_aggregate(week: str):
    """Get weekly aggregate. week format: YYYY-Www (e.g., 2026-W03)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        result = await aggregate.get_weekly_aggregate(db, week)
        return result

@router.get("/aggregates/daily")
async def get_daily_aggregate(date: str):
    """Get daily aggregate. date format: YYYY-MM-DD."""
    target_date = dateparser.parse(date).date()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        result = await aggregate.get_daily_aggregate(db, target_date)
        return result

@router.get("/aggregates/this-week")
async def get_this_week():
    """Get current week's aggregate."""
    today = datetime.now().date()
    from ..services.aggregate import get_week_string
    week_str = get_week_string(today)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        result = await aggregate.get_weekly_aggregate(db, week_str)
        return result

def suggest_tier(calendar_name: str) -> str:
    """Suggest a tier based on calendar name keywords."""
    name_lower = calendar_name.lower()
    if any(k in name_lower for k in ["client", "1000", "premium", "high-value", "revenue"]):
        return "$1000/hr"
    elif any(k in name_lower for k in ["100", "work", "meeting", "collab"]):
        return "$100/hr"
    elif any(k in name_lower for k in ["learn", "course", "study", "book", "reading"]):
        return "Learning"
    return "Routine"
