# Feature Specification: Sincronización en Tiempo Real (SSE) y Control de Mantenimiento

**Feature Branch**: `004-realtime-sse-maintenance`  
**Created**: 2026-10-26  
**Status**: Specified & Ready for Planning  
**Input**: User description: "Permitir que el administrador pueda activar y desactivar la opción de mantenimiento de cualquier puesto de cómputo; corregir la visibilidad para que los puestos en mantenimiento aparezcan claramente en la cuadrícula identificados en color amarillo/ámbar; e implementar sincronización en tiempo real mediante Server-Sent Events (SSE) para que cuando un usuario confirme una reserva o cambie un estado, el servidor emita eventos y la cuadrícula de todos los clientes conectados cambie de color al instante sin recargar la página."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visibilidad y Alternancia Bidireccional de Mantenimiento (Priority: P1)

Como usuario del laboratorio, quiero ver todos los puestos de cómputo en el mapa, incluyendo aquellos que se encuentren en mantenimiento (destacados con color ámbar/amarillo y etiqueta "Mantenimiento"), y como Administrador quiero poder tanto activar como desactivar el mantenimiento de cualquier puesto con un solo clic.

**Why this priority**: Corrige la omisión de estaciones en mantenimiento en la consulta de disponibilidad y dota al administrador de control operativo total para habilitar o suspender computadoras averiadas o en soporte técnico.

**Independent Test**:
1. Consultar disponibilidad de un laboratorio con un puesto en mantenimiento y comprobar que figure en el JSON con `status == 'MAINTENANCE'`.
2. Como administrador, enviar `PATCH /api/workstations/{id}/status` con `{"status": "AVAILABLE"}` y verificar que el puesto pase de mantenimiento a disponible.

**Acceptance Scenarios**:
1. **Given** un laboratorio con un puesto configurado con `status = 'MAINTENANCE'`, **When** se consulta la disponibilidad de horarios, **Then** el puesto aparece en el mapa con tarjeta ámbar, badge "Mantenimiento" y acción de reserva inhabilitada para estudiantes.
2. **Given** un puesto en estado `MAINTENANCE`, **When** un Administrador hace clic en "✅ Quitar Mantenimiento", **Then** el sistema actualiza el estado a `AVAILABLE`, notifica al canal de eventos y el puesto se vuelve verde y reservable de inmediato.
3. **Given** un puesto en estado `AVAILABLE`, **When** un Administrador hace clic en "⚙️ Poner en Mantenimiento", **Then** el sistema actualiza el estado a `MAINTENANCE` e impide nuevas reservas.

---

### User Story 2 - Canal de Transmisión Server-Sent Events (SSE) (Priority: P2)

Como cliente web conectado, quiero mantener una conexión persistente unidireccional y liviana con el servidor mediante Server-Sent Events (SSE) a través de `/api/events`, para recibir notificaciones inmediatas sobre cambios de ocupación o cambios de estado de puestos.

**Why this priority**: Evita la concurrencia ciega donde dos usuarios ven el puesto disponible hasta que uno falla con 409 Conflict, brindando una experiencia colaborativa en tiempo real.

**Independent Test**: Abrir una conexión HTTP a `/api/events` (`text/event-stream`), generar una reserva en otra sesión y comprobar que el stream reciba el evento `workstation_occupied` con los datos del puesto y laboratorio.

**Acceptance Scenarios**:
1. **Given** un cliente conectado a `/api/events`, **When** un usuario confirma una reserva mediante `POST /api/reservations`, **Then** el servidor emite inmediatamente un evento SSE `workstation_occupied` con el `workstation_id` y `laboratory_id`.
2. **Given** un cliente conectado a `/api/events`, **When** una reserva es cancelada por un estudiante o administrador, **Then** el servidor emite un evento SSE `workstation_freed`.
3. **Given** un cliente conectado a `/api/events`, **When** un administrador cambia el estado de mantenimiento de un puesto, **Then** el servidor emite un evento SSE `workstation_status_changed`.

---

### User Story 3 - Cuadrícula Reactiva en el Frontend en Vivo (Priority: P3)

Como estudiante o usuario que se encuentra explorando el mapa de puestos, quiero que la cuadrícula se actualice automáticamente en mi pantalla (cambiando a rojo si alguien reserva, o a verde si se libera) sin tener que presionar "Consultar Disponibilidad" ni refrescar el navegador.

**Why this priority**: Cierra el ciclo de experiencia de usuario resolviendo el problema de concurrencia y conflicto 409 de raíz.

**Acceptance Scenarios**:
1. **Given** dos navegadores abiertos en el mismo laboratorio y horario con el puesto WS-01 en verde, **When** el primer usuario reserva el puesto WS-01, **Then** en la pantalla del segundo usuario la tarjeta del puesto WS-01 pasa automáticamente a color rojo con badge "Ocupado" y botón inhabilitado.
2. **Given** un usuario visualizando el mapa, **When** el administrador activa o desactiva mantenimiento en un puesto, **Then** la tarjeta cambia a amarillo ("Mantenimiento") o verde ("Disponible") en tiempo real con un badge parpadeante de sincronización en vivo.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-RT-01**: `LaboratoryService.check_availability` DEBE incluir todas las estaciones del laboratorio (incluyendo aquellas con `status == 'MAINTENANCE'`) e informar su `status` operativo explícito en cada elemento de respuesta.
- **FR-RT-02**: El endpoint `PATCH /api/workstations/{id}/status` DEBE aceptar tanto `"AVAILABLE"` como `"MAINTENANCE"`.
- **FR-RT-03**: El backend DEBE implementar un gestor asíncrono de difusión de eventos (`EventBroadcaster`) con colas `asyncio.Queue` por cliente.
- **FR-RT-04**: El sistema DEBE exponer el endpoint de streaming `GET /api/events` con tipo MIME `text/event-stream`.
- **FR-RT-05**: El backend DEBE emitir eventos `workstation_occupied`, `workstation_freed` y `workstation_status_changed` ante mutaciones de reservas y puestos.
- **FR-RT-06**: La interfaz web DEBE suscribirse automáticamente al flujo SSE mediante `EventSource('/api/events')` e indicar el estado de sincronización en tiempo real con un badge ("🟢 En Vivo").
- **FR-RT-07**: El frontend DEBE proveer botones contextuales al Administrador para conmutar mantenimiento en ambos sentidos ("⚙️ Poner en Mantenimiento" y "✅ Quitar Mantenimiento").

---

## Success Criteria *(mandatory)*

- **SC-RT-01**: Latencia de propagación del evento SSE entre el servidor y los navegadores conectados menor a 150 milisegundos.
- **SC-RT-02**: Los puestos en mantenimiento se muestran visiblemente en la cuadrícula en color amarillo/ámbar (#F59E0B) tanto para estudiantes como administradores.
- **SC-RT-03**: Reconexión automática del flujo SSE en caso de desconexión transitoria de red.
