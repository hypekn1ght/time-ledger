from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from enum import Enum

class Tier(str, Enum):
    T1000 = "$1000/hr"
    T100 = "$100/hr"
    LEARNING = "Learning"
    ROUTINE = "Routine"

class CalendarBase(BaseModel):
    name: str
    caldav_url: str
    tier: Tier

class CalendarCreate(CalendarBase):
    apple_id: str
    apple_password: str  # Will be stored in keyring, not DB

class Calendar(CalendarBase):
    id: int
    is_connected: bool
    last_sync: Optional[datetime]

    class Config:
        from_attributes = True

class CalendarTierUpdate(BaseModel):
    tier: Tier

class EventBase(BaseModel):
    apple_event_id: str
    summary: str
    start: datetime
    end: datetime

class Event(EventBase):
    id: int
    calendar_id: int

    class Config:
        from_attributes = True

class DailyAggregate(BaseModel):
    date: date
    tier: Tier
    total_minutes: int
    event_count: int

class WeeklyAggregate(BaseModel):
    week: str  # YYYY-Www format
    tier: Tier
    total_minutes: int
    event_count: int
    daily_breakdown: dict[str, int]  # date -> minutes

class SyncStatus(BaseModel):
    is_syncing: bool
    last_sync: Optional[datetime]
    last_error: Optional[str]
    events_synced: int

class ConnectionRequest(BaseModel):
    caldav_url: str
    apple_id: str
    apple_password: str

class ConnectionResponse(BaseModel):
    success: bool
    calendars: list[Calendar]
    error: Optional[str] = None
