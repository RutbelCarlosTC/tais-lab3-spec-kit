from typing import AsyncGenerator, Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session_maker
from src.core.security import decode_access_token
from src.core.exceptions import AuthenticationError, PermissionDeniedError
from src.models.user import User

security_scheme = HTTPBearer(auto_error=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not credentials:
        raise AuthenticationError("Se requiere cabecera de autenticación 'Authorization: Bearer <token>'")

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as e:
        raise AuthenticationError(str(e))

    username = payload.get("sub")
    if not username:
        raise AuthenticationError("Token inválido: falta claim de sujeto")

    user = await db.scalar(select(User).where(User.username == username))
    if not user:
        raise AuthenticationError("Usuario asociado al token no existe")

    if not user.is_active:
        raise AuthenticationError("La cuenta de usuario se encuentra suspendida")

    return user

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except Exception:
        return None

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "ADMIN":
        raise PermissionDeniedError("Acceso denegado: se requieren privilegios de Administrador del Laboratorio")
    return current_user
