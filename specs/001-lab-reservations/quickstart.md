# Quickstart: LabReserve API

Guía rápida para inicializar el servicio y ejecutar las pruebas de integración.

## 1. Instalación de Dependencias

```bash
uv sync
```

## 2. Ejecutar la Suite de Pruebas (Pytest)

```bash
uv run pytest -v
```

## 3. Iniciar el Servidor de Desarrollo

```bash
uv run uvicorn src.main:app --reload --port 8000
```

## 4. Documentación Interactiva OpenAPI (Swagger)

Una vez iniciado el servidor, acceder a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 5. Endpoints Principales

- `POST /api/laboratories`: Registrar un laboratorio.
- `POST /api/laboratories/{id}/workstations`: Añadir puestos de trabajo a un laboratorio.
- `GET /api/laboratories/{id}/availability?start_time=...&end_time=...`: Consultar disponibilidad.
- `POST /api/reservations`: Solicitar nueva reserva.
- `POST /api/reservations/{id}/cancel`: Cancelar reserva activa (mínimo 30m de antelación).
