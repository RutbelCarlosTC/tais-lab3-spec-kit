from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.core.exceptions import InvalidTimeRangeError, MaxDurationExceededError

class AvailabilityQuery(BaseModel):
    start_time: datetime = Field(..., description="Inicio del intervalo a consultar")
    end_time: datetime = Field(..., description="Fin del intervalo a consultar")

    @model_validator(mode="after")
    def validate_timerange(self) -> "AvailabilityQuery":
        if self.end_time <= self.start_time:
            raise InvalidTimeRangeError("La hora de fin debe ser estrictamente posterior a la hora de inicio")
        return self

class WorkstationAvailabilityResponse(BaseModel):
    workstation_id: int
    code: str
    description: str
    is_available: bool
    status: str = "AVAILABLE"  # AVAILABLE | MAINTENANCE

class LaboratoryAvailabilityResponse(BaseModel):
    laboratory_id: int
    laboratory_code: str
    laboratory_name: str
    start_time: datetime
    end_time: datetime
    total_workstations: int
    available_workstations_count: int
    available_workstations: List[WorkstationAvailabilityResponse]

class ReservationCreate(BaseModel):
    workstation_id: int = Field(..., description="ID del puesto a reservar")
    student_id: Optional[str] = Field(default=None, description="Código de estudiante (opcional si se envía token JWT)")
    student_email: Optional[str] = Field(default=None, description="Correo institucional (opcional si se envía token JWT)")
    start_time: datetime = Field(..., description="Fecha y hora de inicio de la reserva")
    end_time: datetime = Field(..., description="Fecha y hora de finalización de la reserva")

    @model_validator(mode="after")
    def validate_reservation_times(self) -> "ReservationCreate":
        if self.end_time <= self.start_time:
            raise InvalidTimeRangeError("La hora de fin de la reserva debe ser posterior a la de inicio")
        
        duration = self.end_time - self.start_time
        if duration > timedelta(hours=2):
            raise MaxDurationExceededError("La duración máxima permitida para una reserva es de 2 horas (120 minutos)")
        
        return self

class ReservationResponse(BaseModel):
    id: int
    workstation_id: int
    student_id: str
    student_email: str
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
