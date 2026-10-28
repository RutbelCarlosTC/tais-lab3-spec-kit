from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_db
from src.services.laboratory_service import LaboratoryService
from src.schemas.laboratory import LaboratoryCreate, LaboratoryResponse
from src.schemas.workstation import WorkstationCreate, WorkstationResponse
from src.schemas.reservation import LaboratoryAvailabilityResponse
from src.core.exceptions import InvalidTimeRangeError

router = APIRouter(prefix="/api/laboratories", tags=["Laboratories"])

@router.post("", response_model=LaboratoryResponse, status_code=status.HTTP_201_CREATED)
async def create_laboratory(
    payload: LaboratoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crea un nuevo laboratorio en el campus."""
    return await LaboratoryService.create_laboratory(db, payload)

@router.get("", response_model=List[LaboratoryResponse])
async def list_laboratories(db: AsyncSession = Depends(get_db)):
    """Lista todos los laboratorios registrados."""
    return await LaboratoryService.list_laboratories(db)

@router.get("/{lab_id}", response_model=LaboratoryResponse)
async def get_laboratory(
    lab_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene los detalles de un laboratorio específico."""
    return await LaboratoryService.get_laboratory(db, lab_id)

@router.post("/{lab_id}/workstations", response_model=WorkstationResponse, status_code=status.HTTP_201_CREATED)
async def add_workstation(
    lab_id: int,
    payload: WorkstationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Agrega un puesto de cómputo a un laboratorio."""
    return await LaboratoryService.add_workstation(db, lab_id, payload)

@router.get("/{lab_id}/availability", response_model=LaboratoryAvailabilityResponse)
async def check_availability(
    lab_id: int,
    start_time: datetime = Query(..., description="Fecha/hora inicio ISO-8601"),
    end_time: datetime = Query(..., description="Fecha/hora fin ISO-8601"),
    db: AsyncSession = Depends(get_db)
):
    """Consulta la disponibilidad de puestos en un laboratorio para un rango horario."""
    if end_time <= start_time:
        raise InvalidTimeRangeError("La hora de fin debe ser posterior a la de inicio")
    return await LaboratoryService.check_availability(db, lab_id, start_time, end_time)
