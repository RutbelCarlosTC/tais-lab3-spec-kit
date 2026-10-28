from datetime import datetime
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.laboratory import Laboratory
from src.models.workstation import Workstation
from src.models.reservation import Reservation
from src.schemas.laboratory import LaboratoryCreate
from src.schemas.workstation import WorkstationCreate
from src.schemas.reservation import (
    LaboratoryAvailabilityResponse,
    WorkstationAvailabilityResponse
)
from src.core.exceptions import ResourceNotFoundError, ValidationError

class LaboratoryService:
    @staticmethod
    async def create_laboratory(db: AsyncSession, data: LaboratoryCreate) -> Laboratory:
        existing = await db.scalar(select(Laboratory).where(Laboratory.code == data.code))
        if existing:
            raise ValidationError(f"Ya existe un laboratorio con el código '{data.code}'")
        
        lab = Laboratory(
            code=data.code,
            name=data.name,
            location=data.location,
            is_active=data.is_active
        )
        db.add(lab)
        await db.commit()
        await db.refresh(lab)
        return lab

    @staticmethod
    async def get_laboratory(db: AsyncSession, lab_id: int) -> Laboratory:
        lab = await db.get(Laboratory, lab_id)
        if not lab:
            raise ResourceNotFoundError(f"Laboratorio con id {lab_id} no encontrado")
        return lab

    @staticmethod
    async def list_laboratories(db: AsyncSession) -> List[Laboratory]:
        result = await db.scalars(select(Laboratory).order_by(Laboratory.id))
        return list(result.all())

    @staticmethod
    async def add_workstation(db: AsyncSession, lab_id: int, data: WorkstationCreate) -> Workstation:
        lab = await LaboratoryService.get_laboratory(db, lab_id)
        
        existing = await db.scalar(
            select(Workstation).where(
                Workstation.laboratory_id == lab.id,
                Workstation.code == data.code
            )
        )
        if existing:
            raise ValidationError(f"Ya existe un puesto con el código '{data.code}' en este laboratorio")

        ws = Workstation(
            laboratory_id=lab.id,
            code=data.code,
            description=data.description,
            status=data.status
        )
        db.add(ws)
        await db.commit()
        await db.refresh(ws)
        return ws

    @staticmethod
    async def check_availability(
        db: AsyncSession,
        lab_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> LaboratoryAvailabilityResponse:
        lab = await LaboratoryService.get_laboratory(db, lab_id)

        # Buscar todos los puestos del laboratorio (incluyendo MAINTENANCE para visibilidad completa)
        result = await db.scalars(
            select(Workstation).where(
                Workstation.laboratory_id == lab.id
            ).order_by(Workstation.code)
        )
        workstations = list(result.all())

        # Buscar las reservas activas que se solapan en este rango de tiempo para los puestos disponibles
        ws_ids = [w.id for w in workstations if w.status == "AVAILABLE"]
        occupied_ws_ids = set()
        
        if ws_ids:
            conflicts_query = select(Reservation.workstation_id).where(
                Reservation.workstation_id.in_(ws_ids),
                Reservation.status == "CONFIRMED",
                Reservation.start_time < end_time,
                Reservation.end_time > start_time
            )
            conflict_results = await db.scalars(conflicts_query)
            occupied_ws_ids = set(conflict_results.all())

        availability_list: List[WorkstationAvailabilityResponse] = []
        for ws in workstations:
            if ws.status == "MAINTENANCE":
                is_free = False
                op_status = "MAINTENANCE"
            else:
                is_free = ws.id not in occupied_ws_ids
                op_status = "AVAILABLE"

            availability_list.append(
                WorkstationAvailabilityResponse(
                    workstation_id=ws.id,
                    code=ws.code,
                    description=ws.description,
                    is_available=is_free,
                    status=op_status
                )
            )

        available_count = sum(1 for item in availability_list if item.is_available)

        return LaboratoryAvailabilityResponse(
            laboratory_id=lab.id,
            laboratory_code=lab.code,
            laboratory_name=lab.name,
            start_time=start_time,
            end_time=end_time,
            total_workstations=len(workstations),
            available_workstations_count=available_count,
            available_workstations=availability_list
        )
