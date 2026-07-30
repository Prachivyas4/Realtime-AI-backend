from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from .websocket import websocket_session

app = FastAPI()

@app.websocket("/ws/session/{session_id}")
async def ws_endpoint(websocket: WebSocket, session_id: str):
    await websocket_session(websocket, session_id)
