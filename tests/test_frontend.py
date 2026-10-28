import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_serve_frontend_index(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "LabReserve" in response.text
    assert "workstations-grid" in response.text

@pytest.mark.asyncio
async def test_serve_static_assets(client: AsyncClient):
    css_resp = await client.get("/static/css/style.css")
    assert css_resp.status_code == 200
    assert "--bg-dark" in css_resp.text

    js_resp = await client.get("/static/js/app.js")
    assert js_resp.status_code == 200
    assert "checkAvailability" in js_resp.text

@pytest.mark.asyncio
async def test_demo_seed_endpoint(client: AsyncClient):
    # 1. Ejecutar siembra inicial
    seed_resp = await client.post("/api/demo/seed")
    assert seed_resp.status_code == 200
    seed_data = seed_resp.json()
    assert seed_data["status"] == "seeded"
    assert "LAB-IA-201" in seed_data["laboratories"]

    # 2. Verificar que los laboratorios creados son listados por la API
    labs_resp = await client.get("/api/laboratories")
    assert labs_resp.status_code == 200
    labs = labs_resp.json()
    assert len(labs) >= 2
    lab_codes = [l["code"] for l in labs]
    assert "LAB-IA-201" in lab_codes
    assert "LAB-SW-102" in lab_codes

    # 3. Segunda ejecución es idempotente
    repeat_resp = await client.post("/api/demo/seed")
    assert repeat_resp.status_code == 200
    assert repeat_resp.json()["status"] == "existing"
