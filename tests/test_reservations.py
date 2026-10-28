import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient

async def setup_lab_and_workstation(client: AsyncClient, code_suffix: str = "A"):
    lab_resp = await client.post("/api/laboratories", json={
        "code": f"LAB-{code_suffix}",
        "name": "Laboratorio de Pruebas",
        "location": "Pabellón A",
        "is_active": True
    })
    lab_id = lab_resp.json()["id"]

    ws_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={
        "code": f"WS-{code_suffix}-1",
        "description": "Estación de Trabajo",
        "status": "AVAILABLE"
    })
    return ws_resp.json()["id"]

@pytest.mark.asyncio
async def test_create_reservation_success(client: AsyncClient):
    ws_id = await setup_lab_and_workstation(client, "SUC")
    now = datetime.now(timezone.utc) + timedelta(days=1)
    start = now.replace(hour=14, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1, minutes=30)  # 1h30m <= 2h

    resp = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-2026-100",
        "student_email": "stu100@unsa.edu.pe",
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "CONFIRMED"
    assert data["student_id"] == "STU-2026-100"
    assert data["workstation_id"] == ws_id

@pytest.mark.asyncio
async def test_reject_overlapping_reservation(client: AsyncClient):
    ws_id = await setup_lab_and_workstation(client, "OVL")
    now = datetime.now(timezone.utc) + timedelta(days=1)
    start_14 = now.replace(hour=14, minute=0, second=0, microsecond=0)
    end_16 = start_14 + timedelta(hours=2)

    # 1. Primera reserva de 14:00 a 16:00
    res1 = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-A",
        "student_email": "stua@unsa.edu.pe",
        "start_time": start_14.isoformat(),
        "end_time": end_16.isoformat()
    })
    assert res1.status_code == 201

    # 2. Intento de solapamiento: de 15:00 a 17:00 para el mismo puesto
    start_15 = start_14 + timedelta(hours=1)
    end_17 = start_15 + timedelta(hours=2)

    res2 = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-B",
        "student_email": "stub@unsa.edu.pe",
        "start_time": start_15.isoformat(),
        "end_time": end_17.isoformat()
    })
    assert res2.status_code == 409
    assert res2.json()["error_type"] == "RESERVATION_CONFLICT"

@pytest.mark.asyncio
async def test_reject_duration_exceeding_two_hours(client: AsyncClient):
    ws_id = await setup_lab_and_workstation(client, "DUR")
    now = datetime.now(timezone.utc) + timedelta(days=1)
    start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=2, minutes=15)  # 2h 15m > 2h

    resp = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-DUR",
        "student_email": "studur@unsa.edu.pe",
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })
    assert resp.status_code in [400, 422]

@pytest.mark.asyncio
async def test_reject_multiple_active_reservations_same_student(client: AsyncClient):
    # Crear dos puestos distintos
    lab_resp = await client.post("/api/laboratories", json={
        "code": "LAB-MULT",
        "name": "Lab Multiple",
        "location": "Pab C",
        "is_active": True
    })
    lab_id = lab_resp.json()["id"]

    ws1_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={"code": "WS-M1"})
    ws1_id = ws1_resp.json()["id"]
    ws2_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={"code": "WS-M2"})
    ws2_id = ws2_resp.json()["id"]

    now = datetime.now(timezone.utc) + timedelta(days=1)
    start1 = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end1 = start1 + timedelta(hours=1)

    start2 = now.replace(hour=14, minute=0, second=0, microsecond=0)
    end2 = start2 + timedelta(hours=1)

    # Primera reserva confirmada para STU-SINGLE
    r1 = await client.post("/api/reservations", json={
        "workstation_id": ws1_id,
        "student_id": "STU-SINGLE",
        "student_email": "single@unsa.edu.pe",
        "start_time": start1.isoformat(),
        "end_time": end1.isoformat()
    })
    assert r1.status_code == 201

    # Segunda reserva intentada por el mismo estudiante
    r2 = await client.post("/api/reservations", json={
        "workstation_id": ws2_id,
        "student_id": "STU-SINGLE",
        "student_email": "single@unsa.edu.pe",
        "start_time": start2.isoformat(),
        "end_time": end2.isoformat()
    })
    assert r2.status_code == 409
    assert r2.json()["error_type"] == "ACTIVE_RESERVATION_LIMIT"

@pytest.mark.asyncio
async def test_reject_reservation_in_the_past(client: AsyncClient):
    ws_id = await setup_lab_and_workstation(client, "PAST")
    past = datetime.now(timezone.utc) - timedelta(days=1)
    start = past.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)

    resp = await client.post("/api/reservations", json={
        "workstation_id": ws_id,
        "student_id": "STU-PAST",
        "student_email": "past@unsa.edu.pe",
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })
    assert resp.status_code == 400
    assert resp.json()["error_type"] == "VALIDATION_ERROR"
