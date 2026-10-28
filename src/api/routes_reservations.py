from typing import List, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_db, get_current_user, get_optional_current_user, require_admin
from src.services.reservation_service import ReservationService
from src.schemas.reservation import ReservationCreate, ReservationResponse
from src.models.user import User

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])

class CancelPayload(BaseModel):
    student_id: Optional[str] = Field(default=None, description="Código del estudiante titular (opcional si se envía Bearer token)")

@router.get("/me", response_model=List[ReservationResponse])
async def get_my_reservations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retorna automáticamente todas las reservas correspondientes al usuario autenticado (Estudiante)."""
    return await ReservationService.get_user_reservations(db, current_user.username)

@router.get("", response_model=List[ReservationResponse])
async def get_all_reservations(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint exclusivo para Administradores: retorna todas las reservas registradas en el sistema."""
    return await ReservationService.get_all_reservations(db)

@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    payload: ReservationCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crea una reserva. Si el usuario está autenticado, infiere automáticamente su identidad (1-click booking)."""
    return await ReservationService.create_reservation(db, payload, current_user=current_user)

@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene los detalles de una reserva por su ID."""
    return await ReservationService.get_reservation(db, reservation_id)

@router.post("/{reservation_id}/cancel", response_model=ReservationResponse)
async def cancel_reservation(
    reservation_id: int,
    payload: Optional[CancelPayload] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancela una reserva. Admite verificación mediante token JWT o parámetro student_id."""
    actor = current_user or (payload.student_id if payload else None)
    if not actor:
        raise ValueError("Se requiere autenticación o especificar el student_id")
    return await ReservationService.cancel_reservation(db, reservation_id, actor)
