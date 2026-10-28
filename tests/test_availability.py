import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_laboratory_and_workstations(client: AsyncClient):
    # 1. Crear laboratorio
    lab_resp = await client.post("/api/laboratories", json={
        "code": "LAB-CS-101",
        "name": "Laboratorio de Inteligencia Artificial",
        "location": "Pabellón Turing - Piso 2",
        "is_active": True
    })
    assert lab_resp.status_code == 201
    lab_data = lab_resp.json()
    lab_id = lab_data["id"]

    # 2. Agregar puestos de trabajo
    ws1_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={
        "code": "WS-01",
        "description": "Intel i9, 32GB RAM, RTX 4080",
        "status": "AVAILABLE"
    })
    assert ws1_resp.status_code == 201

    ws2_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={
        "code": "WS-02",
        "description": "Intel i7, 16GB RAM",
        "status": "AVAILABLE"
    })
    assert ws2_resp.status_code == 201

    # 3. Consultar disponibilidad sin reservas previas
    now = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=2)

    avail_resp = await client.get(
        f"/api/laboratories/{lab_id}/availability",
        params={"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
    )
    assert avail_resp.status_code == 200
    avail_data = avail_resp.json()
    assert avail_data["total_workstations"] == 2
    assert avail_data["available_workstations_count"] == 2

@pytest.mark.asyncio
async def test_availability_with_existing_reservation(client: AsyncClient):
    # Setup laboratorio y 2 puestos
    lab_resp = await client.post("/api/laboratories", json={
        "code": "LAB-CS-102",
        "name": "Laboratorio de Redes",
        "location": "Pabellón B",
        "is_active": True
    })
    lab_id = lab_resp.json()["id"]

    ws1_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={
        "code": "WS-01", "description": "Puesto 1"
    })
    ws1_id = ws1_resp.json()["id"]

    ws2_resp = await client.post(f"/api/laboratories/{lab_id}/workstations", json={
        "code": "WS-02", "description": "Puesto 2"
    })
    ws2_id = ws2_resp.json()["id"]

    # Crear una reserva en WS-01 para mañana de 10:00 a 12:00
    base_date = datetime.now(timezone.utc) + timedelta(days=2)
    start_10 = base_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_12 = start_10 + timedelta(hours=2)

    res_resp = await client.post("/api/reservations", json={
        "workstation_id": ws1_id,
        "student_id": "STU-2026-001",
        "student_email": "estudiante1@unsa.edu.pe",
        "start_time": start_10.isoformat(),
        "end_time": end_12.isoformat()
    })
    assert res_resp.status_code == 201

    # Consultar disponibilidad de 10:00 a 12:00 -> WS-01 ocupado, WS-02 libre
    avail_resp = await client.get(
        f"/api/laboratories/{lab_id}/availability",
        params={"start_time": start_10.isoformat(), "end_time": end_12.isoformat()}
    )
    assert avail_resp.status_code == 200
    avail_data = avail_resp.json()
    assert avail_data["total_workstations"] == 2
    assert avail_data["available_workstations_count"] == 1

    ws_map = {w["code"]: w["is_available"] for w in avail_data["available_workstations"]}
    assert ws_map["WS-01"] is False
    assert ws_map["WS-02"] is True

@pytest.mark.asyncio
async def test_availability_invalid_timerange(client: AsyncClient):
    now = datetime.now(timezone.utc) + timedelta(days=1)
    start = now.replace(hour=14, minute=0)
    end = now.replace(hour=13, minute=0)  # end < start

    resp = await client.get(
        "/api/laboratories/1/availability",
        params={"start_time": start.isoformat(), "end_time": end.isoformat()}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "error_type" in data or "detail" in data

@pytest.mark.asyncio
async def test_availability_non_existent_lab(client: AsyncClient):
    now = datetime.now(timezone.utc) + timedelta(days=1)
    start = now.replace(hour=10, minute=0)
    end = now.replace(hour=11, minute=0)

    resp = await client.get(
        "/api/laboratories/999/availability",
        params={"start_time": start.isoformat(), "end_time": end.isoformat()}
    )
    assert resp.status_code == 404
