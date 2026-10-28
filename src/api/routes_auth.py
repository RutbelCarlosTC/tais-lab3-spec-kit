from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_db, get_current_user
from src.services.auth_service import AuthService
from src.schemas.auth import LoginRequest, TokenResponse, UserResponse
from src.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Inicia sesión con credenciales y emite un JSON Web Token (JWT) con claims de rol."""
    user = await AuthService.authenticate_user(db, payload.username, payload.password)
    token = AuthService.generate_token(user)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Retorna la información del usuario actualmente autenticado a partir de su token."""
    return UserResponse.model_validate(current_user)
