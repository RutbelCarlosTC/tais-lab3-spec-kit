from datetime import datetime, timezone, timedelta
from typing import Optional, List, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.workstation import Workstation
from src.models.reservation import Reservation
from src.models.user import User
from src.schemas.reservation import ReservationCreate
from src.core.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    ReservationConflictError,
    ActiveReservationLimitError,
    CancellationWindowExpiredError,
    InvalidReservationStateError,
    PermissionDeniedError
)
from src.core.events import event_broadcaster

class ReservationService:
    @staticmethod
    async def create_reservation(
        db: AsyncSession,
        data: ReservationCreate,
        current_user: Optional[User] = None,
        now: Optional[datetime] = None
    ) -> Reservation:
        current_time = now or datetime.now(timezone.utc)

        # 1. Determinar identidad del estudiante
        if current_user:
            student_id = current_user.username
            student_email = current_user.email
        elif data.student_id and data.student_email:
            student_id = data.student_id
            student_email = data.student_email
        else:
            raise ValidationError("Se requiere autenticación o especificar student_id y student_email")

        # 2. Validar que la reserva no sea para el pasado
        start_tz = data.start_time if data.start_time.tzinfo else data.start_time.replace(tzinfo=timezone.utc)
        if start_tz < current_time:
            raise ValidationError("No se pueden registrar reservas para fechas u horas en el pasado")

        # 3. Verificar que el puesto de trabajo existe y está operativo
        workstation = await db.get(Workstation, data.workstation_id)
        if not workstation:
            raise ResourceNotFoundError(f"Puesto de trabajo con id {data.workstation_id} no encontrado")
        
        if workstation.status != "AVAILABLE":
            raise ValidationError(f"El puesto de trabajo {workstation.code} está actualmente en mantenimiento ({workstation.status})")

        # 4. Regla de Negocio: Máximo 1 reserva activa por estudiante
        active_student_reservation = await db.scalar(
            select(Reservation).where(
                Reservation.student_id == student_id,
                Reservation.status == "CONFIRMED"
            )
        )
        if active_student_reservation:
            raise ActiveReservationLimitError(
                f"El estudiante {student_id} ya posee una reserva activa confirmada (ID: {active_student_reservation.id}). No se permiten reservas simultáneas."
            )

        # 5. Regla de Negocio: No solapamiento de horarios en el mismo puesto de trabajo
        conflict = await db.scalar(
            select(Reservation).where(
                Reservation.workstation_id == data.workstation_id,
                Reservation.status == "CONFIRMED",
                Reservation.start_time < data.end_time,
                Reservation.end_time > data.start_time
            )
        )
        if conflict:
            raise ReservationConflictError(
                f"Conflicto de horario: El puesto {workstation.code} ya se encuentra reservado entre {conflict.start_time.isoformat()} y {conflict.end_time.isoformat()}."
            )

        # 6. Persistir reserva confirmada
        reservation = Reservation(
            workstation_id=data.workstation_id,
            student_id=student_id,
            student_email=student_email,
            start_time=data.start_time,
            end_time=data.end_time,
            status="CONFIRMED"
        )
        db.add(reservation)
        await db.commit()
        await db.refresh(reservation)

        # Emitir evento en tiempo real SSE: Puesto Ocupado
        await event_broadcaster.broadcast(
            "workstation_occupied",
            {
                "reservation_id": reservation.id,
                "workstation_id": reservation.workstation_id,
                "laboratory_id": workstation.laboratory_id,
                "start_time": reservation.start_time.isoformat(),
                "end_time": reservation.end_time.isoformat(),
                "student_id": reservation.student_id
            }
        )

        return reservation

    @staticmethod
    async def get_user_reservations(db: AsyncSession, student_id: str) -> List[Reservation]:
        """Retorna todas las reservas correspondientes a un estudiante ordenadas cronológicamente."""
        result = await db.scalars(
            select(Reservation)
            .where(Reservation.student_id == student_id)
            .order_by(Reservation.start_time.desc())
        )
        return list(result.all())

    @staticmethod
    async def get_all_reservations(db: AsyncSession) -> List[Reservation]:
        """Retorna todas las reservas del sistema para el panel de administración."""
        result = await db.scalars(
            select(Reservation)
            .order_by(Reservation.start_time.desc())
        )
        return list(result.all())

    @staticmethod
    async def cancel_reservation(
        db: AsyncSession,
        reservation_id: int,
        student_id: Union[User, str],
        now: Optional[datetime] = None
    ) -> Reservation:
        reservation = await db.get(Reservation, reservation_id)
        if not reservation:
            raise ResourceNotFoundError(f"Reserva con id {reservation_id} no encontrada")

        if reservation.status != "CONFIRMED":
            raise InvalidReservationStateError(
                f"La reserva no se encuentra activa (estado actual: {reservation.status})"
            )

        current_time = now or datetime.now(timezone.utc)
        res_start = reservation.start_time if reservation.start_time.tzinfo else reservation.start_time.replace(tzinfo=timezone.utc)

        # Verificar si es Administrador o Estudiante
        if isinstance(student_id, User):
            if student_id.role == "ADMIN":
                reservation.status = "CANCELLED"
                await db.commit()
                await db.refresh(reservation)

                # Emitir evento en tiempo real SSE: Puesto Liberado
                await event_broadcaster.broadcast(
                    "workstation_freed",
                    {
                        "reservation_id": reservation.id,
                        "workstation_id": reservation.workstation_id,
                        "student_id": reservation.student_id
                    }
                )
                return reservation
            else:
                student_code = student_id.username
        else:
            student_code = student_id

        # Validación para estudiante: debe ser el titular
        if reservation.student_id != student_code:
            raise PermissionDeniedError("Solo el estudiante titular o un Administrador puede cancelar esta reserva")

        # Regla de los 30 minutos
        lead_time = res_start - current_time
        if lead_time < timedelta(minutes=30):
            raise CancellationWindowExpiredError(
                "La política exige cancelar con al menos 30 minutos de antelación al inicio del turno"
            )

        reservation.status = "CANCELLED"
        await db.commit()
        await db.refresh(reservation)

        # Emitir evento en tiempo real SSE: Puesto Liberado
        await event_broadcaster.broadcast(
            "workstation_freed",
            {
                "reservation_id": reservation.id,
                "workstation_id": reservation.workstation_id,
                "student_id": reservation.student_id
            }
        )

        return reservation

    @staticmethod
    async def get_reservation(db: AsyncSession, reservation_id: int) -> Reservation:
        res = await db.get(Reservation, reservation_id)
        if not res:
            raise ResourceNotFoundError(f"Reserva con id {reservation_id} no encontrada")
        return res
