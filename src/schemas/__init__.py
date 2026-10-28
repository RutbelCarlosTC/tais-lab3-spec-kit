from src.schemas.laboratory import LaboratoryCreate, LaboratoryResponse
from src.schemas.workstation import WorkstationCreate, WorkstationResponse
from src.schemas.reservation import (
    AvailabilityQuery,
    LaboratoryAvailabilityResponse,
    WorkstationAvailabilityResponse,
    ReservationCreate,
    ReservationResponse,
)
from src.schemas.auth import LoginRequest, TokenResponse, UserResponse

__all__ = [
    "LaboratoryCreate",
    "LaboratoryResponse",
    "WorkstationCreate",
    "WorkstationResponse",
    "AvailabilityQuery",
    "LaboratoryAvailabilityResponse",
    "WorkstationAvailabilityResponse",
    "ReservationCreate",
    "ReservationResponse",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
]
