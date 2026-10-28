from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # Student code (e.g. 20240981) or Admin ID
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="STUDENT", nullable=False)  # STUDENT | ADMIN
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
