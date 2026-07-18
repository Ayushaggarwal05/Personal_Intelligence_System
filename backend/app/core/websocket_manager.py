from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio

class ConnectionManager:
    """Thread-safe connection manager routing real-time WebSockets notifications and agent token buffers."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accepts and registers a new client socket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Deregisters a closed client socket connection."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def send_json_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Sends a JSON package to a specific client socket."""
        try:
            await websocket.send_json(message)
        except Exception:
            await self.disconnect(websocket)

    async def broadcast_json(self, message: Dict[str, Any]):
        """Broadcasts a JSON status notification package to all active client sockets."""
        async with self._lock:
            dead_connections = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append(connection)
            
            # Cleanup any dead sockets
            for conn in dead_connections:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)

    async def stream_tokens(self, stream_id: str, tokens_iterable):
        """Streams text generation chunks back to all connected client sockets in real-time."""
        for token in tokens_iterable:
            payload = {
                "type": "token_stream",
                "stream_id": stream_id,
                "token": token
            }
            await self.broadcast_json(payload)
            # Sleep brief moment to allow event loop cooperative context switches
            await asyncio.sleep(0.01)

websocket_manager = ConnectionManager()
