import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_login_and_me(client: AsyncClient):
    # 1. Sembrar usuarios y datos iniciales
    seed_resp = await client.post("/api/demo/seed")
    assert seed_resp.status_code == 200

    # 2. Login como Estudiante
    login_stu = await client.post("/api/auth/login", json={
        "username": "20240981",
        "password": "estudiante123"
    })
    assert login_stu.status_code == 200
    stu_data = login_stu.json()
    assert "access_token" in stu_data
    assert stu_data["user"]["role"] == "STUDENT"
    stu_token = stu_data["access_token"]

    # 3. Consultar /api/auth/me con token de estudiante
    me_resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {stu_token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "20240981"

    # 4. Login como Administrador
    login_adm = await client.post("/api/auth/login", json={
        "username": "ADMIN-01",
        "password": "admin123"
    })
    assert login_adm.status_code == 200
    assert login_adm.json()["user"]["role"] == "ADMIN"

    # 5. Login con contraseña errónea -> 401
    bad_login = await client.post("/api/auth/login", json={
        "username": "20240981",
        "password": "wrongpassword"
    })
    assert bad_login.status_code == 401

@pytest.mark.asyncio
async def test_one_click_reservation_and_my_reservations(client: AsyncClient):
    # Setup
    await client.post("/api/demo/seed")

    # Login estudiante
    login_res = await client.post("/api/auth/login", json={
        "username": "20240981",
        "password": "estudiante123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener un puesto disponible del primer lab
    labs = (await client.get("/api/laboratories")).json()
    lab_id = labs[0]["id"]

    now = datetime.now(timezone.utc) + timedelta(days=2)
    start = now.replace(hour=14, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1, minutes=30)

    avail = (await client.get(
        f"/api/laboratories/{lab_id}/availability",
        params={"start_time": start.isoformat(), "end_time": end.isoformat()}
    )).json()

    available_ws = [w for w in avail["available_workstations"] if w["is_available"]][0]
    ws_id = available_ws["workstation_id"]

    # Reserva en 1 Clic (SIN enviar student_id ni student_email en el body)
    res_resp = await client.post(
        "/api/reservations",
        headers=headers,
        json={
            "workstation_id": ws_id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    assert res_resp.status_code == 201
    res_data = res_resp.json()
    assert res_data["student_id"] == "20240981"
    assert res_data["student_email"] == "estudiante@unsa.edu.pe"
    assert res_data["status"] == "CONFIRMED"

    # Consultar /api/reservations/me
    me_reservations = await client.get("/api/reservations/me", headers=headers)
    assert me_reservations.status_code == 200
    my_list = me_reservations.json()
    assert len(my_list) >= 1
    assert any(r["id"] == res_data["id"] for r in my_list)

@pytest.mark.asyncio
async def test_rbac_security_and_admin_privileges(client: AsyncClient):
    await client.post("/api/demo/seed")

    # 1. Tokens
    stu_res = await client.post("/api/auth/login", json={"username": "20240981", "password": "estudiante123"})
    stu_headers = {"Authorization": f"Bearer {stu_res.json()['access_token']}"}

    adm_res = await client.post("/api/auth/login", json={"username": "ADMIN-01", "password": "admin123"})
    adm_headers = {"Authorization": f"Bearer {adm_res.json()['access_token']}"}

    # 2. Estudiante intenta acceder a listado global de reservas (solo admin) -> 403
    forbidden_resp = await client.get("/api/reservations", headers=stu_headers)
    assert forbidden_resp.status_code == 403

    # 3. Administrador accede a listado global de reservas -> 200
    admin_list = await client.get("/api/reservations", headers=adm_headers)
    assert admin_list.status_code == 200

    # 4. Estudiante intenta cambiar estado de un puesto -> 403
    patch_stu = await client.patch("/api/workstations/1/status", headers=stu_headers, json={"status": "MAINTENANCE"})
    assert patch_stu.status_code == 403

    # 5. Administrador cambia estado de un puesto -> 200
    patch_adm = await client.patch("/api/workstations/1/status", headers=adm_headers, json={"status": "MAINTENANCE"})
    assert patch_adm.status_code == 200
    assert patch_adm.json()["status"] == "MAINTENANCE"
