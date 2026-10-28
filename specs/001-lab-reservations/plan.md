# Implementation Plan: Sistema de Reservas de Laboratorios de Computo (LabReserve)

**Branch**: `001-lab-reservations` | **Date**: 2026-10-26 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/001-lab-reservations/spec.md`

## Summary

Implementar un servicio REST en FastAPI para la gestión de laboratorios y reservas de puestos de cómputo en la universidad. El sistema garantiza la consistencia transaccional mediante SQLAlchemy 2.0 en modo asíncrono sobre SQLite (con base de datos en memoria para testing y archivo local para desarrollo), validando disponibilidad sin solapamiento, cuotas por estudiante (máximo 1 reserva activa), ventanas de duración (máx. 2h) y política de cancelación previa (mínimo 30 minutos).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI (v0.115+), Uvicorn, SQLAlchemy 2.0 (asyncio), Pydantic v2, aiosqlite  
**Storage**: SQLite (`sqlite+aiosqlite:///lab_reserve.db` para desarrollo; `sqlite+aiosqlite:///:memory:` para tests)  
**Testing**: Pytest, `pytest-asyncio`, `httpx` (ASGI test client)  
**Target Platform**: Linux server / Contenedor Docker / CLI local  
**Project Type**: Microservicio Web REST / API  
**Performance Goals**: Latencia p95 < 50ms para consultas de disponibilidad  
**Constraints**: Operaciones atómicas para evitar condiciones de carrera en reservas simultáneas; 100% de tipos anotados.  
**Scale/Scope**: Laboratorios universitarios de la facultad (10-20 laboratorios, ~50 puestos por laboratorio).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Requisito de la Constitución | Estado | Evidencia de Cumplimiento |
| :--- | :--- | :---: | :--- |
| **I. Arquitectura Modular** | Separación estricta: API, Servicios, Modelos, Esquemas | **PASS** | `src/api`, `src/services`, `src/models`, `src/schemas` separados. |
| **II. TDD & Aislamiento** | Tests unitarios y de integración con BD en memoria | **PASS** | Tests en `tests/` con fixtures async aislados por test. |
| **III. Tipado y Pydantic** | Validación de esquemas y tipos estrictos | **PASS** | Pydantic v2 para validación de entrada/salida y reglas de tiempo. |
| **IV. Contratos de Error** | Códigos HTTP semánticos y excepciones de dominio | **PASS** | Mapeo de `ReservationConflictError` a 409, `NotFoundError` a 404, etc. |
| **V. Simplicidad (YAGNI)** | Minimal suficiente sin sobre-ingeniería | **PASS** | Arquitectura limpia directa con repositorio/servicio liviano. |

## Project Structure

### Documentation (this feature)

```text
specs/001-lab-reservations/
├── spec.md              # Requisitos y escenarios BDD
├── plan.md              # Este plan de implementación
├── research.md          # Decisiones de diseño y trade-offs
├── data-model.md        # Entidades, relaciones y diagramas
├── quickstart.md        # Guía rápida de ejecución y pruebas
├── checklists/
│   └── requirements.md  # Checklist de calidad
└── tasks.md             # Tareas atómicas de desarrollo
```

### Source Code Layout

```text
src/
├── __init__.py
├── main.py                  # Entrada FastAPI y registro de routers
├── core/
│   ├── __init__.py
│   ├── config.py            # Configuraciones y settings
│   ├── database.py          # Async engine, sessionmaker y Base
│   └── exceptions.py        # Excepciones de dominio y handlers globales
├── models/
│   ├── __init__.py
│   ├── laboratory.py        # Modelo SQLAlchemy Laboratory
│   ├── workstation.py       # Modelo SQLAlchemy Workstation
│   └── reservation.py       # Modelo SQLAlchemy Reservation
├── schemas/
│   ├── __init__.py
│   ├── laboratory.py        # Schemas Pydantic para Laboratorios
│   ├── workstation.py       # Schemas Pydantic para Puestos
│   └── reservation.py       # Schemas Pydantic para Reservas y Consultas
├── services/
│   ├── __init__.py
│   ├── laboratory_service.py# Lógica de creación y consulta de laboratorios
│   └── reservation_service.py # Lógica de validación, reservas y cancelación
└── api/
    ├── __init__.py
    ├── deps.py              # Inyección de dependencias (get_db_session)
    ├── routes_laboratories.py # Endpoints /api/laboratories
    └── routes_reservations.py # Endpoints /api/reservations

tests/
├── conftest.py              # Fixtures para cliente async y BD en memoria
├── test_availability.py     # Tests para US1: Consulta de disponibilidad
├── test_reservations.py     # Tests para US2: Creación y reglas de negocio
└── test_cancellation.py     # Tests para US3: Política de cancelación
```
