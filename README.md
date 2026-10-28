# LabReserve

Sistema web para gestionar la reserva de puestos de laboratorios universitarios. Incluye una API con FastAPI, una interfaz web, autenticación por roles y sincronización en tiempo real mediante SSE.

## Requisitos

- Python 3.11 o superior
- `uv`

Instala `uv` si aún no lo tienes:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Ejecutar el proyecto

1. Instala las dependencias:

   ```bash
   uv sync
   ```

2. Inicia la aplicación:

   ```bash
   uv run uvicorn src.main:app --reload --port 8000
   ```

3. Abre la aplicación en el navegador:

   - Web: http://localhost:8000
   - Documentación de la API: http://localhost:8000/docs

## Ejecutar las pruebas

```bash
uv run pytest -v
```

Para cargar los datos de demostración, abre la aplicación y pulsa **Sembrar Demo**.
