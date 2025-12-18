from typing import Optional
from datetime import datetime
from .db import supabase


async def create_session(session_id: str, user_id: Optional[str] = None):
    supabase.table("sessions").insert({
        "session_id": session_id,
        "user_id": user_id
    }).execute()


async def log_event(
    session_id: str,
    event_type: str,
    role: Optional[str],
    content: str
):
    supabase.table("session_events").insert({
        "session_id": session_id,
        "event_type": event_type,
        "role": role,
        "content": content
    }).execute()


async def close_session(
    session_id: str,
    summary: str,
    duration_seconds: int
):
    supabase.table("sessions").update({
        "end_time": datetime.utcnow().isoformat(),
        "duration_seconds": duration_seconds,
        "summary": summary
    }).eq("session_id", session_id).execute()
