import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_maintenance_workstation_visibility(client: AsyncClient):
    # 1. Sembrar datos demo (Lab 1 tiene WS-04 en MAINTENANCE)
    await client.post("/api/demo/seed")

    labs = (await client.get("/api/laboratories")).json()
    lab1_id = labs[0]["id"]

    now = datetime.now(timezone.utc) + timedelta(days=1)
    start = now.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=2)

    # 2. Consultar disponibilidad
    avail_resp = await client.get(
        f"/api/laboratories/{lab1_id}/availability",
        params={"start_time": start.isoformat(), "end_time": end.isoformat()}
    )
    assert avail_resp.status_code == 200
    data = avail_resp.json()

    # Comprobar que WS-04 está presente y tiene status MAINTENANCE
    ws_codes = {w["code"]: w for w in data["available_workstations"]}
    assert "WS-04" in ws_codes
    assert ws_codes["WS-04"]["status"] == "MAINTENANCE"
    assert ws_codes["WS-04"]["is_available"] is False

@pytest.mark.asyncio
async def test_admin_bidirectional_maintenance_toggle(client: AsyncClient):
    await client.post("/api/demo/seed")

    # Login Admin
    adm_res = await client.post("/api/auth/login", json={"username": "ADMIN-01", "password": "admin123"})
    adm_headers = {"Authorization": f"Bearer {adm_res.json()['access_token']}"}

    # Login Student
    stu_res = await client.post("/api/auth/login", json={"username": "20240981", "password": "estudiante123"})
    stu_headers = {"Authorization": f"Bearer {stu_res.json()['access_token']}"}

    # Obtener el puesto WS-04 (actualmente en mantenimiento)
    labs = (await client.get("/api/laboratories")).json()
    lab1_id = labs[0]["id"]
    avail = (await client.get(
        f"/api/laboratories/{lab1_id}/availability",
        params={
            "start_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=1)).isoformat()
        }
    )).json()

    ws_04 = [w for w in avail["available_workstations"] if w["code"] == "WS-04"][0]
    ws_id = ws_04["workstation_id"]

    # 1. El estudiante no puede quitar mantenimiento -> 403
    forbidden_patch = await client.patch(
        f"/api/workstations/{ws_id}/status",
        headers=stu_headers,
        json={"status": "AVAILABLE"}
    )
    assert forbidden_patch.status_code == 403

    # 2. El Administrador DESACTIVA el mantenimiento (Pasa a AVAILABLE) -> 200
    deactivate_maint = await client.patch(
        f"/api/workstations/{ws_id}/status",
        headers=adm_headers,
        json={"status": "AVAILABLE"}
    )
    assert deactivate_maint.status_code == 200
    assert deactivate_maint.json()["status"] == "AVAILABLE"

    # 3. El Administrador REACTIVA el mantenimiento (Pasa a MAINTENANCE) -> 200
    reactivate_maint = await client.patch(
        f"/api/workstations/{ws_id}/status",
        headers=adm_headers,
        json={"status": "MAINTENANCE"}
    )
    assert reactivate_maint.status_code == 200
    assert reactivate_maint.json()["status"] == "MAINTENANCE"

@pytest.mark.asyncio
async def test_event_broadcaster_subscribe_and_broadcast():
    from src.core.events import event_broadcaster
    # 1. Verificar suscripción y ping inicial
    gen = event_broadcaster.subscribe()
    initial_ping = await anext(gen)
    assert "event: ping" in initial_ping
    assert "SSE conectado exitosamente" in initial_ping

    # 2. Verificar broadcast de ocupación en tiempo real
    await event_broadcaster.broadcast(
        "workstation_occupied",
        {"workstation_id": 99, "status": "OCCUPIED"}
    )
    occupied_event = await anext(gen)
    assert "event: workstation_occupied" in occupied_event
    assert '"workstation_id": 99' in occupied_event

    # 3. Verificar broadcast de liberación en tiempo real
    await event_broadcaster.broadcast(
        "workstation_freed",
        {"workstation_id": 99, "status": "AVAILABLE"}
    )
    freed_event = await anext(gen)
    assert "event: workstation_freed" in freed_event

    # 4. Limpieza del generador
    await gen.aclose()

@pytest.mark.asyncio
async def test_sse_endpoint_configuration():
    from src.api.routes_events import subscribe_events
    response = await subscribe_events()
    assert response.media_type == "text/event-stream"
    assert response.headers["Cache-Control"] == "no-cache"
    assert response.headers["Connection"] == "keep-alive"
