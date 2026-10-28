import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.reservation_service import ReservationService

@pytest.mark.asyncio
async def test_successful_cancellation_with_lead_time(client: AsyncClient):
    # Setup lab y puesto
    lab_resp = await client.post("/api/laboratories", json={
        "code": "LAB-CANCEL", "name": "Lab Cancelación", "location": "Pab D", "is_active": True
    })
    lab_id = lab_resp.json()["id"]
    ws_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={"code": "WS-C1"})
    ws_id = ws_resp.json()["id"]

    # Crear reserva para dentro de 3 días (muy superior a 30m)
    future = datetime.now(timezone.utc) + timedelta(days=3)
    start = future.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)

    res_resp = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-CANC-1",
        "student_email": "canc1@unsa.edu.pe",
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })
    assert res_resp.status_code == 201
    res_id = res_resp.json()["id"]

    # Cancelar reserva
    cancel_resp = await client.post(
        f"/api/reservations/{res_id}/cancel",
        json={"student_id": "STU-CANC-1"}
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

    # Verificar que el estudiante ahora puede hacer una nueva reserva (al haberse liberado su cuota)
    next_start = start + timedelta(hours=2)
    next_end = next_start + timedelta(hours=1)
    new_res_resp = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-CANC-1",
        "student_email": "canc1@unsa.edu.pe",
        "start_time": next_start.isoformat(),
        "end_time": next_end.isoformat()
    })
    assert new_res_resp.status_code == 201

@pytest.mark.asyncio
async def test_reject_cancellation_within_thirty_minutes(client: AsyncClient, db_session: AsyncSession):
    # Setup
    lab_resp = await client.post("/api/laboratories", json={
        "code": "LAB-EXP", "name": "Lab Ventana", "location": "Pab D", "is_active": True
    })
    lab_id = lab_resp.json()["id"]
    ws_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={"code": "WS-EXP"})
    ws_id = ws_resp.json()["id"]

    # Crear reserva a futuro
    future = datetime.now(timezone.utc) + timedelta(days=1)
    start = future.replace(hour=11, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)

    res_resp = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-EXP",
        "student_email": "exp@unsa.edu.pe",
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })
    res_id = res_resp.json()["id"]

    # Simular intento de cancelación cuando faltan solo 10 minutos (a nivel de servicio inyectando `now`)
    simulated_now = start - timedelta(minutes=10)
    
    with pytest.raises(Exception) as exc_info:
        await ReservationService.cancel_reservation(
            db=db_session,
            reservation_id=res_id,
            student_id="STU-EXP",
            now=simulated_now
        )
    assert "30 minutos de antelación" in str(exc_info.value)

@pytest.mark.asyncio
async def test_reject_cancellation_non_owner(client: AsyncClient):
    lab_resp = await client.post("/api/laboratories", json={
        "code": "LAB-OWN", "name": "Lab Owner", "location": "Pab D", "is_active": True
    })
    lab_id = lab_resp.json()["id"]
    ws_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={"code": "WS-OWN"})
    ws_id = ws_resp.json()["id"]

    future = datetime.now(timezone.utc) + timedelta(days=2)
    start = future.replace(hour=15, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)

    res_resp = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-REAL-OWNER",
        "student_email": "owner@unsa.edu.pe",
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })
    res_id = res_resp.json()["id"]

    # Intento de cancelación por otro estudiante
    cancel_resp = await client.post(
        f"/api/reservations/{res_id}/cancel",
        json={"student_id": "STU-INTRUDER"}
    )
    assert cancel_resp.status_code in [400, 403]

    assert "Solo el estudiante titular" in cancel_resp.json()["detail"]
