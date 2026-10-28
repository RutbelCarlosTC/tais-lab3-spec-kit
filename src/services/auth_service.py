from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.core.security import verify_password, create_access_token
from src.core.exceptions import AuthenticationError

class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, username_or_email: str, password: str) -> User:
        user = await db.scalar(
            select(User).where(
                or_(
                    User.username == username_or_email,
                    User.email == username_or_email
                )
            )
        )
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Credenciales inválidas: usuario o contraseña incorrectos")

        if not user.is_active:
            raise AuthenticationError("La cuenta de usuario está desactivada")

        return user

    @staticmethod
    def generate_token(user: User) -> str:
        payload = {
            "sub": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "user_id": user.id
        }
        return create_access_token(payload)
