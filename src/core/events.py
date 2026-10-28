import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Set

class EventBroadcaster:
    """Gestor singleton asíncrono para difusión de Server-Sent Events (SSE)."""

    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    async def subscribe(self) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(queue)
        
        # Enviar evento de conexión inicial
        yield f"event: ping\ndata: {json.dumps({'message': 'SSE conectado exitosamente'})}\n\n"

        try:
            while True:
                # Esperar nuevo mensaje de la cola
                message = await queue.get()
                yield message
        except asyncio.CancelledError:
            pass
        finally:
            self._subscribers.discard(queue)

    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        """Difunde un evento en formato SSE a todos los clientes web conectados."""
        if not self._subscribers:
            return

        payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(payload)
            except Exception:
                self._subscribers.discard(queue)

# Instancia global del broadcaster
event_broadcaster = EventBroadcaster()
