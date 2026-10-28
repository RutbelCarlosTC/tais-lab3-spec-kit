# Tasks: Sistema de Reservas de Laboratorios de Computo (LabReserve)

Feature: `001-lab-reservations`  
Spec: [spec.md](./spec.md) | Plan: [plan.md](./plan.md)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and dependencies.

- [x] T001 Inicializar `pyproject.toml` con dependencias: fastapi, uvicorn, sqlalchemy, aiosqlite, pydantic, pytest, pytest-asyncio, httpx, greenlet.
- [x] T002 Crear la estructura de paquetes en `src/` (`core`, `models`, `schemas`, `services`, `api`) y `tests/`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database connection, base models, exception handlers, and FastAPI app setup.

- [x] T003 Configurar motor asíncrono y sesión en `src/core/database.py`.
- [x] T004 Definir excepciones de dominio y manejadores de error HTTP en `src/core/exceptions.py`.
- [x] T005 Configurar aplicación principal FastAPI y middleware en `src/main.py`.
- [x] T006 Configurar fixtures de prueba asíncronos y base de datos en memoria en `tests/conftest.py`.

**Checkpoint**: Base de datos, app FastAPI y entorno de pruebas listos para implementar historias de usuario.

---

## Phase 3: User Story 1 - Consulta de Disponibilidad de Puestos (Priority: P1) 🎯 MVP

**Goal**: Permitir listar laboratorios, puestos de cómputo y consultar qué puestos están libres en un rango horario.

- [x] T007 [US1] Definir modelos SQLAlchemy `Laboratory` y `Workstation` en `src/models/`.
- [x] T008 [US1] Definir esquemas Pydantic para laboratorios, puestos y consulta de disponibilidad en `src/schemas/`.
- [x] T009 [US1] Implementar `LaboratoryService` en `src/services/laboratory_service.py` para gestión de laboratorios y puestos.
- [x] T010 [US1] Implementar endpoints de laboratorios y consulta de disponibilidad en `src/api/routes_laboratories.py`.
- [x] T011 [US1] Escribir y ejecutar pruebas unitarias/integración para disponibilidad en `tests/test_availability.py`.

**Checkpoint**: US1 completamente funcional e independientemente verificable con tests en verde.

---

## Phase 4: User Story 2 - Creación de Reserva con Reglas de Negocio (Priority: P2)

**Goal**: Permitir a los estudiantes reservar un puesto libre con validación de duración (máx 2h), no-solapamiento de turnos y límite de 1 reserva activa por estudiante.

- [x] T012 [US2] Definir modelo SQLAlchemy `Reservation` en `src/models/reservation.py`.
- [x] T013 [US2] Definir esquemas Pydantic `ReservationCreate` y `ReservationResponse` en `src/schemas/reservation.py`.
- [x] T014 [US2] Implementar `ReservationService.create_reservation` con validaciones de negocio en `src/services/reservation_service.py`.
- [x] T015 [US2] Implementar endpoint `POST /api/reservations` en `src/api/routes_reservations.py`.
- [x] T016 [US2] Escribir y ejecutar pruebas de integración para escenarios BDD de solapamiento y límites en `tests/test_reservations.py`.

**Checkpoint**: US2 completamente funcional con reglas de conflicto y límites validados.

---

## Phase 5: User Story 3 - Cancelación Oportuna de Reserva (Priority: P3)

**Goal**: Permitir cancelar una reserva confirmada si restan al menos 30 minutos antes del inicio.

- [x] T017 [US3] Implementar `ReservationService.cancel_reservation` con regla de ventana temporal en `src/services/reservation_service.py`.
- [x] T018 [US3] Implementar endpoint `POST /api/reservations/{id}/cancel` en `src/api/routes_reservations.py`.
- [x] T019 [US3] Escribir y ejecutar pruebas de integración para cancelación oportuna y tardía en `tests/test_cancellation.py`.

**Checkpoint**: Todas las historias de usuario implementadas y testeadas.

---

## Phase 6: Polish & Verification

**Purpose**: Verificación cruzada integral y preparación para convergencia.

- [x] T020 Ejecutar suite completa con `pytest` y verificar 100% de tests aprobados (12/12 passing).
- [x] T021 Verificar cumplimiento de la Constitución (separación de capas, tipado estricto, manejo de excepciones).
