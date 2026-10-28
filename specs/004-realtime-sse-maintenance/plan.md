# Implementation Plan: Sincronización en Tiempo Real (SSE) y Control de Mantenimiento

**Branch**: `004-realtime-sse-maintenance` | **Date**: 2026-10-26 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/004-realtime-sse-maintenance/spec.md`

## Summary

Implementar un sistema de difusión en tiempo real basado en Server-Sent Events (SSE) para notificar inmediatamente a todos los clientes web cuando un puesto de cómputo es ocupado, liberado o cuando cambia su estado operativo, previniendo condiciones de carrera y errores 409 Conflict. Asimismo, corregir la visibilidad de los puestos en mantenimiento (mostrándolos en color ámbar/amarillo) y habilitar la conmutación bidireccional de mantenimiento (`AVAILABLE` $\leftrightarrow$ `MAINTENANCE`) para los administradores.

## Technical Context

**Language/Version**: Python 3.11+  
**Architecture & Protocols**:
- Servidor: Streaming HTTP asíncrono con `StreamingResponse` y `media_type="text/event-stream"`.
- Gestor de Difusión: `EventBroadcaster` singleton en `src/core/events.py` utilizando `asyncio.Queue` por cliente conectado.
- Eventos transmitidos:
  - `workstation_occupied`: Emitido al registrar una reserva en `ReservationService.create_reservation`.
  - `workstation_freed`: Emitido al cancelar una reserva en `ReservationService.cancel_reservation`.
  - `workstation_status_changed`: Emitido al alternar mantenimiento en `routes_workstations.py`.
- Cliente: `EventSource` estándar de HTML5/JavaScript en `src/static/js/app.js` con reconexión automática y actualización reactiva del DOM.
- Visibilidad de Mantenimiento: Corrección de la consulta en `LaboratoryService.check_availability` para incluir estaciones en `MAINTENANCE` con campo `status` explícito en `WorkstationAvailabilityResponse`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Requisito de la Constitución | Estado | Evidencia de Cumplimiento |
| :--- | :--- | :---: | :--- |
| **I. Arquitectura Modular** | Eventos desacoplados del transporte | **PASS** | `src/core/events.py` gestiona la difusión independiente de las rutas. |
| **II. TDD & Aislamiento** | Tests de SSE y alternancia de estado | **PASS** | `tests/test_realtime_and_maintenance.py` verifica SSE y alternancia. |
| **III. Tipado y Pydantic** | Campo `status` en esquema de disponibilidad | **PASS** | `WorkstationAvailabilityResponse.status: str = "AVAILABLE"`. |
| **VI. Interfaz Web y UX** | Indicador en vivo y tarjetas ámbar | **PASS** | Badge "En Vivo" y tarjeta amarilla para PCs en mantenimiento. |
| **VIII. Sincronización SSE** | Actualización sin recargar la página | **PASS** | Flujo SSE permanente y actualización reactiva de colores. |

## Project Structure

```text
src/
├── core/
│   └── events.py            # EventBroadcaster con colas asyncio y generador SSE
├── api/
│   ├── routes_events.py     # Endpoint GET /api/events (StreamingResponse)
│   └── routes_workstations.py # PATCH con soporte bidireccional y emisión de eventos
├── schemas/
│   └── reservation.py       # Campo status en WorkstationAvailabilityResponse
├── services/
│   ├── laboratory_service.py # Inclusión de puestos en mantenimiento en disponibilidad
│   └── reservation_service.py# Emisión de eventos workstation_occupied y workstation_freed
└── static/
    ├── index.html           # Badge de conexión en vivo "🟢 En Vivo"
    ├── css/style.css        # Estilos ámbar reforzados para .badge-maintenance y .ws-card.maintenance
    └── js/app.js            # Cliente EventSource y botones de activación/desactivación de mantenimiento

tests/
├── test_realtime_and_maintenance.py # Pruebas unitarias/integración de SSE y visibilidad de mantenimiento
```
