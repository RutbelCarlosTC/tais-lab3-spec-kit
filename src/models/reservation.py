from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.models.workstation import Workstation

class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        Index("ix_res_workstation_status_times", "workstation_id", "status", "start_time", "end_time"),
        Index("ix_res_student_status", "student_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workstation_id: Mapped[int] = mapped_column(ForeignKey("workstations.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    student_email: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="CONFIRMED", nullable=False)  # CONFIRMED | CANCELLED | COMPLETED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    workstation: Mapped["Workstation"] = relationship("Workstation", back_populates="reservations")
