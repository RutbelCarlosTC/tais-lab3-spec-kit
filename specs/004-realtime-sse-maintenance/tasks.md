# Tasks: Sincronización en Tiempo Real (SSE) y Control de Mantenimiento

Feature: `004-realtime-sse-maintenance`  
Spec: [spec.md](./spec.md) | Plan: [plan.md](./plan.md)

## Phase 1: Setup & Foundational (Event Broadcaster & SSE Streaming)

- [x] T001 Implementar `EventBroadcaster` singleton en `src/core/events.py` utilizando `asyncio.Queue` y formateo estándar SSE.
- [x] T002 Crear endpoint `GET /api/events` en `src/api/routes_events.py` retornando `StreamingResponse(media_type="text/event-stream")` y registrarlo en `src/main.py`.

---

## Phase 2: User Story 1 (P1) - Visibilidad y Alternancia de Mantenimiento

- [x] T003 [US1] Modificar `LaboratoryService.check_availability` en `src/services/laboratory_service.py` para incluir puestos en mantenimiento y no excluirlos de la respuesta.
- [x] T004 [US1] Agregar campo `status: str = "AVAILABLE"` a `WorkstationAvailabilityResponse` en `src/schemas/reservation.py`.
- [x] T005 [US1] Actualizar `src/api/routes_workstations.py` para admitir alternancia bidireccional (`AVAILABLE` $\leftrightarrow$ `MAINTENANCE`) y emitir evento `workstation_status_changed`.

---

## Phase 3: User Story 2 (P2) - Difusión en Tiempo Real de Eventos de Reservas

- [x] T006 [US2] Emitir evento `workstation_occupied` en `ReservationService.create_reservation` ante una nueva reserva confirmada.
- [x] T007 [US2] Emitir evento `workstation_freed` en `ReservationService.cancel_reservation` ante una cancelación de turno.

---

## Phase 4: User Story 3 (P3) - Frontend Reactivo y Controles de UI

- [x] T008 [US3] Agregar badge de conexión SSE en `src/static/index.html` ("🟢 En Vivo").
- [x] T009 [US3] Actualizar estilos CSS en `src/static/css/style.css` para visibilidad de puestos amarillos/ámbar y controles admin.
- [x] T010 [US3] Conectar `EventSource('/api/events')` en `src/static/js/app.js` para actualización reactiva en tiempo real sin recargar página.
- [x] T011 [US3] Implementar botones en el frontend para que el Administrador active y desactive el mantenimiento de cualquier puesto.

---

## Phase 5: Pruebas y Convergencia

- [x] T012 Escribir tests en `tests/test_realtime_and_maintenance.py` verificando streaming SSE, visibilidad de puestos en mantenimiento y alternancia bidireccional.
- [x] T013 Ejecutar `uv run pytest -v` (100% de tests en verde).
- [x] T014 Generar reporte de convergencia en `specs/004-realtime-sse-maintenance/convergence.md`.
