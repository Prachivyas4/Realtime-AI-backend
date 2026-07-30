from fastapi import WebSocket, WebSocketDisconnect
from uuid import uuid4
import time

from .models import create_session, log_event, close_session
from .llm import stream_chat_completion
from .db import supabase

# In-memory conversation state
sessions = {}


async def websocket_session(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Create session in DB
    await create_session(session_id)

    start_time = time.time()
    sessions[session_id] = [
        {"role": "system", "content": "You are a helpful real-time AI assistant."}
    ]

    try:
        while True:
            # Receive user message
            user_message = await websocket.receive_text()

            sessions[session_id].append({"role": "user", "content": user_message})

            # Log user message
            await log_event(session_id, "message", "user", user_message)

            # Stream LLM response
            ai_response = ""
            async for token in stream_chat_completion(sessions[session_id]):
                ai_response += token
                await websocket.send_text(token)

            # Log AI message
            sessions[session_id].append({"role": "assistant", "content": ai_response})
            await log_event(session_id, "message", "assistant", ai_response)

    except WebSocketDisconnect:
        duration = int(time.time() - start_time)

        # Fetch events from Supabase
        events_resp = supabase.table("session_events").select("*").eq("session_id", session_id).execute()
        events = events_resp.data

        # Generate session summary
        from .llm import client # LLM client
        messages = [{"role": "system", "content": "Summarize this conversation concisely."}]
        for e in events:
            messages.append({"role": e["role"], "content": e["content"]})
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        summary = response.choices[0].message.content

        # Close session in DB
        await close_session(session_id, summary, duration)

        # Cleanup in-memory state
        sessions.pop(session_id, None)
        print(f"Session {session_id} ended, duration {duration}s")

