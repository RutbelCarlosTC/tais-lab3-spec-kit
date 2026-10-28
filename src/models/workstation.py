from typing import List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.models.laboratory import Laboratory
    from src.models.reservation import Reservation

class Workstation(Base):
    __tablename__ = "workstations"
    __table_args__ = (
        UniqueConstraint("laboratory_id", "code", name="uq_lab_workstation_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    laboratory_id: Mapped[int] = mapped_column(ForeignKey("laboratories.id", ondelete="CASCADE"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="AVAILABLE", nullable=False)  # AVAILABLE | MAINTENANCE

    laboratory: Mapped["Laboratory"] = relationship("Laboratory", back_populates="workstations")
    reservations: Mapped[List["Reservation"]] = relationship(
        "Reservation",
        back_populates="workstation",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
