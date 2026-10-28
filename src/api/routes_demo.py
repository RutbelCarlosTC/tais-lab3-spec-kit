from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_db
from src.models.laboratory import Laboratory
from src.models.workstation import Workstation
from src.models.user import User
from src.core.security import hash_password

router = APIRouter(prefix="/api/demo", tags=["Demo"])

@router.post("/seed", status_code=status.HTTP_200_OK)
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    """Siembra datos iniciales de usuarios (Estudiante y Admin) y laboratorios para la práctica."""
    created_users = []

    # 1. Asegurar Usuarios Demo
    student_user = await db.scalar(select(User).where(User.username == "20240981"))
    if not student_user:
        student_user = User(
            username="20240981",
            email="estudiante@unsa.edu.pe",
            hashed_password=hash_password("estudiante123"),
            full_name="Carlos Mendoza (Estudiante)",
            role="STUDENT",
            is_active=True
        )
        db.add(student_user)
        created_users.append("20240981 (Estudiante)")

    admin_user = await db.scalar(select(User).where(User.username == "ADMIN-01"))
    if not admin_user:
        admin_user = User(
            username="ADMIN-01",
            email="admin@unsa.edu.pe",
            hashed_password=hash_password("admin123"),
            full_name="Ing. Roberto Díaz (Encargado Lab)",
            role="ADMIN",
            is_active=True
        )
        db.add(admin_user)
        created_users.append("ADMIN-01 (Admin)")

    # 2. Asegurar Laboratorios y Puestos
    existing_lab = await db.scalar(select(Laboratory).limit(1))
    if not existing_lab:
        lab1 = Laboratory(
            code="LAB-IA-201",
            name="Laboratorio de Inteligencia Artificial & Visión",
            location="Pabellón Turing - Piso 2",
            is_active=True
        )
        db.add(lab1)
        await db.flush()

        for i in range(1, 7):
            st = "MAINTENANCE" if i == 4 else "AVAILABLE"
            desc = "GPU NVIDIA RTX 4090, 64GB RAM" if i != 4 else "Hardware en revisión técnica"
            ws = Workstation(
                laboratory_id=lab1.id,
                code=f"WS-{i:02d}",
                description=desc,
                status=st
            )
            db.add(ws)

        lab2 = Laboratory(
            code="LAB-SW-102",
            name="Laboratorio de Ingeniería de Software (TAIS)",
            location="Pabellón San Agustín - Piso 1",
            is_active=True
        )
        db.add(lab2)
        await db.flush()

        for i in range(1, 5):
            ws = Workstation(
                laboratory_id=lab2.id,
                code=f"WS-{i:02d}",
                description="Intel Core i7 13th Gen, 32GB RAM",
                status="AVAILABLE"
            )
            db.add(ws)

    await db.commit()
    
    if not created_users and existing_lab:
        return {"message": "La base de datos ya contiene datos completos.", "status": "existing"}

    return {
        "message": "Datos de demostración y usuarios sembrados con éxito",
        "status": "seeded",
        "users": [
            {"username": "20240981", "role": "STUDENT", "default_password": "estudiante123"},
            {"username": "ADMIN-01", "role": "ADMIN", "default_password": "admin123"}
        ],
        "laboratories": ["LAB-IA-201", "LAB-SW-102"]
    }
