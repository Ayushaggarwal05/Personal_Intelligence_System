from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.projects import router as projects_router
from app.api.interview import router as interview_router
from app.api.workspace import router as workspace_router
from app.api.chat import router as chat_router
from app.api.diagrams import router as diagrams_router
from app.api.search import router as search_router
from app.api.memory import router as memory_router
from app.api.system import router as system_router
from app.api.settings_api import router as settings_router
from app.api.prompts import router as prompts_router
from app.api.review import router as review_router
from app.core.websocket_manager import websocket_manager
from app.core.logging import logger

api_router = APIRouter(prefix="/api")

# Mount Routers
api_router.include_router(projects_router)
api_router.include_router(interview_router)
api_router.include_router(workspace_router)
api_router.include_router(chat_router)
api_router.include_router(diagrams_router)
api_router.include_router(search_router)
api_router.include_router(memory_router)
api_router.include_router(system_router)
api_router.include_router(settings_router)
api_router.include_router(prompts_router)
api_router.include_router(review_router)

# WebSocket connection route
@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Establishes real-time connection tunnel for status alerts and streaming tokens."""
    await websocket_manager.connect(websocket)
    logger.info("[WebSocket] New client connection accepted.")
    try:
        while True:
            # Wait/receive client text messages to keep connection active
            data = await websocket.receive_text()
            # Auto-respond to client ping checks
            if data.strip().lower() == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        logger.info("[WebSocket] Client connection closed.")
    finally:
        await websocket_manager.disconnect(websocket)
