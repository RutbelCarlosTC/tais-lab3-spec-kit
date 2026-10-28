from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class LaboratoryBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Código único del laboratorio")
    name: str = Field(..., min_length=2, max_length=100, description="Nombre descriptivo")
    location: str = Field(..., min_length=2, max_length=100, description="Ubicación física / Pabellón")
    is_active: bool = Field(default=True, description="Indica si el laboratorio está activo")

class LaboratoryCreate(LaboratoryBase):
    pass

class LaboratoryResponse(LaboratoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
