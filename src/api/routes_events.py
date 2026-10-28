from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.core.events import event_broadcaster

router = APIRouter(prefix="/api/events", tags=["Realtime Events"])

@router.get("", response_class=StreamingResponse)
async def subscribe_events():
    """Canal de Server-Sent Events (SSE) para sincronización en tiempo real de ocupación y puestos."""
    return StreamingResponse(
        event_broadcaster.subscribe(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
