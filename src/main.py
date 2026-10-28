from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.core.database import engine, Base
from src.core.exceptions import register_exception_handlers
from src.api.routes_laboratories import router as laboratories_router
from src.api.routes_reservations import router as reservations_router
from src.api.routes_demo import router as demo_router
from src.api.routes_auth import router as auth_router
from src.api.routes_workstations import router as workstations_router
from src.api.routes_events import router as events_router
import src.models  # asegura que los modelos sean cargados en Base.metadata

STATIC_DIR = Path(__file__).parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas en el inicio de la app si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Limpieza al apagar
    await engine.dispose()

app = FastAPI(
    title="LabReserve API & Web App",
    description="Microservicio y Frontend Web de Gestión y Reserva de Puestos de Cómputo con JWT, RBAC & SSE en Tiempo Real - Flujo SDD con GitHub Spec Kit",
    version="1.3.0",
    lifespan=lifespan
)

# Registrar manejadores de error centralizados
register_exception_handlers(app)

# Montar routers modulares de la API
app.include_router(auth_router)
app.include_router(laboratories_router)
app.include_router(reservations_router)
app.include_router(workstations_router)
app.include_router(events_router)
app.include_router(demo_router)

# Montar directorio de archivos estáticos
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "LabReserve API activa. Visita /docs para la documentación Swagger."}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "LabReserve API & UI", "version": "1.3.0"}
