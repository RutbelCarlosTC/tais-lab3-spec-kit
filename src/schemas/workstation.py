from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class WorkstationBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Código del puesto (ej. WS-01)")
    description: str = Field(default="", max_length=200, description="Detalles o especificaciones")
    status: str = Field(default="AVAILABLE", description="Estado operativo (AVAILABLE o MAINTENANCE)")

class WorkstationCreate(WorkstationBase):
    pass

class WorkstationResponse(WorkstationBase):
    id: int
    laboratory_id: int
    model_config = ConfigDict(from_attributes=True)
