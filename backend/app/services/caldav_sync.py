import caldav
from datetime import datetime, timedelta
import keyring
from dateutil import parser as dateparser
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_credentials(caldav_url: str) -> tuple[str, str]:
    """Retrieve stored credentials from keyring."""
    apple_id = keyring.get_password("timeledger_caldav", f"{caldav_url}_apple_id")
    apple_password = keyring.get_password("timeledger_caldav", f"{caldav_url}_apple_password")
    return apple_id, apple_password

def store_credentials(caldav_url: str, apple_id: str, apple_password: str):
    """Store credentials securely in OS keyring."""
    keyring.set_password("timeledger_caldav", f"{caldav_url}_apple_id", apple_id)
    keyring.set_password("timeledger_caldav", f"{caldav_url}_apple_password", apple_password)

def remove_credentials(caldav_url: str):
    """Remove stored credentials."""
    try:
        keyring.delete_password("timeledger_caldav", f"{caldav_url}_apple_id")
        keyring.delete_password("timeledger_caldav", f"{caldav_url}_apple_password")
    except keyring.errors.PasswordDeleteError:
        pass

def test_connection(caldav_url: str, apple_id: str, apple_password: str) -> tuple[bool, str, list]:
    """
    Test CalDAV connection and return (success, error_message, calendars).
    """
    try:
        client = caldav.DAVClient(
            url=caldav_url,
            username=apple_id,
            password=apple_password
        )
        principal = client.principal()
        calendars = list(principal.calendars())
        
        calendar_data = []
        for cal in calendars:
            try:
                calendar_data.append({
                    "name": cal.name,
                    "caldav_url": cal.canonical_url,
                    "id": cal.id,
                })
            except Exception:
                calendar_data.append({
                    "name": cal.name or "Unknown",
                    "caldav_url": cal.canonical_url,
                    "id": "unknown",
                })
        
        return True, "", calendar_data
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "authentication" in error_msg.lower():
            return False, "Invalid Apple ID or app-specific password. Note: Use an App-Specific Password, not your Apple ID password.", []
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            return False, "Cannot connect to iCloud. Check your internet connection and CalDAV URL.", []
        else:
            return False, f"Connection failed: {error_msg}", []

def fetch_events(caldav_url: str, calendar_id: str, apple_id: str, apple_password: str, days_back: int = 90) -> list[dict]:
    """
    Fetch events from a specific calendar for the last N days.
    """
    try:
        client = caldav.DAVClient(
            url=caldav_url,
            username=apple_id,
            password=apple_password
        )
        principal = client.principal()
        
        # Find the specific calendar
        target_calendar = None
        for cal in principal.calendars():
            if cal.canonical_url == calendar_id or cal.id == calendar_id:
                target_calendar = cal
                break
        
        if not target_calendar:
            return []
        
        start_date = datetime.now() - timedelta(days=days_back)
        results = target_calendar.search(
            start=start_date,
            end=datetime.now(),
            event=True,
            expand=True
        )
        
        events = []
        for event in results:
            try:
                if hasattr(event, 'vobject_item') and event.vobject_item:
                    vevent = event.vobject_item.vevent
                    summary = str(vevent.summary.value) if vevent.summary else "No title"
                    start = vevent.dtstart.value
                    end = vevent.dtend.value if vevent.dtend else start + timedelta(hours=1)
                    
                    # Handle all-day events
                    if hasattr(start, 'date') and not hasattr(start, 'hour'):
                        start = datetime.combine(start.date(), datetime.min.time())
                        end = datetime.combine(end.date(), datetime.min.time()) if hasattr(end, 'date') else start + timedelta(hours=1)
                    
                    events.append({
                        "apple_event_id": vevent.uid.value if vevent.uid else str(hash(str(vevent))),
                        "summary": summary,
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                    })
            except Exception as e:
                logger.warning(f"Failed to parse event: {e}")
                continue
        
        return events
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        return []
