from pydantic import BaseModel, ConfigDict, Field

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="Código de estudiante o username")
    password: str = Field(..., min_length=4, description="Contraseña")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
