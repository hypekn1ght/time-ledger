import caldav
from datetime import datetime, timedelta
import keyring
from dateutil import parser as dateparser
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_credentials(caldav_url: str) -> tuple[str, str]:
    """Retrieve stored credentials from keyring.
    
    Credentials are stored under the root iCloud CalDAV URL (https://caldav.icloud.com/),
    not the calendar-specific URL, since one Apple ID credentials apply to all calendars.
    """
    # Normalize to root iCloud URL for credential lookup
    if "icloud.com" in caldav_url:
        root_url = "https://caldav.icloud.com/"
    else:
        root_url = caldav_url
    apple_id = keyring.get_password("timeledger_caldav", f"{root_url}_apple_id")
    apple_password = keyring.get_password("timeledger_caldav", f"{root_url}_apple_password")
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
                vevent = event.icalendar_component
                
                # Summary: vText -> use .to_ical().decode() or cast to str
                summary_raw = vevent.get("SUMMARY")
                summary = str(summary_raw.to_ical().decode()) if summary_raw else "No title"
                
                # UID: vText -> string
                uid_raw = vevent.get("UID")
                uid = str(uid_raw.to_ical().decode()) if uid_raw else str(hash(str(vevent)))
                
                # DTSTART/DTEND: vDDDTypes -> .dt attribute
                start_val = vevent.get("DTSTART")
                end_val = vevent.get("DTEND")
                
                start_dt = start_val.dt if start_val else datetime.now()
                end_dt = end_val.dt if end_val else start_dt + timedelta(hours=1)
                
                # Strip timezone info for consistency (store as naive UTC)
                if hasattr(start_dt, 'tzinfo') and start_dt.tzinfo:
                    start_dt = start_dt.replace(tzinfo=None)
                if hasattr(end_dt, 'tzinfo') and end_dt.tzinfo:
                    end_dt = end_dt.replace(tzinfo=None)
                
                events.append({
                    "apple_event_id": uid,
                    "summary": summary,
                    "start": start_dt.isoformat(),
                    "end": end_dt.isoformat(),
                })
            except Exception as e:
                logger.warning(f"Failed to parse event: {e}")
                continue
        
        return events
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        return []
