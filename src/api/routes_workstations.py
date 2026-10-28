from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_db, require_admin
from src.models.workstation import Workstation
from src.models.user import User
from src.schemas.workstation import WorkstationResponse
from src.core.exceptions import ResourceNotFoundError
from src.core.events import event_broadcaster

router = APIRouter(prefix="/api/workstations", tags=["Workstations"])

class StatusUpdatePayload(BaseModel):
    status: str = Field(..., pattern="^(AVAILABLE|MAINTENANCE)$", description="Nuevo estado operativo (AVAILABLE o MAINTENANCE)")

@router.patch("/{workstation_id}/status", response_model=WorkstationResponse, status_code=status.HTTP_200_OK)
async def update_workstation_status(
    workstation_id: int,
    payload: StatusUpdatePayload,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint exclusivo para Administradores: Cambia el estado operativo de un puesto (AVAILABLE / MAINTENANCE) y emite un evento SSE en tiempo real."""
    ws = await db.get(Workstation, workstation_id)
    if not ws:
        raise ResourceNotFoundError(f"Puesto de trabajo {workstation_id} no encontrado")

    ws.status = payload.status
    await db.commit()
    await db.refresh(ws)

    # Emitir evento en tiempo real a todos los clientes conectados
    await event_broadcaster.broadcast(
        "workstation_status_changed",
        {
            "workstation_id": ws.id,
            "laboratory_id": ws.laboratory_id,
            "code": ws.code,
            "status": ws.status
        }
    )

    return ws
