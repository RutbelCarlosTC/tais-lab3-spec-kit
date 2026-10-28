# Feature Specification: Sistema de Reservas de Laboratorios de Computo (LabReserve)

**Feature Branch**: `001-lab-reservations`  
**Created**: 2026-10-26  
**Status**: Specified & Ready for Planning  
**Input**: User description: "Desarrollo del módulo de gestión y reserva de puestos de trabajo en laboratorios de cómputo universitarios con reglas de disponibilidad, concurrencia, límites de tiempo y políticas de cancelación."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consulta de Disponibilidad de Puestos (Priority: P1)

Como estudiante universitario, quiero consultar los puestos de trabajo disponibles en un laboratorio específico para una fecha y ventana de tiempo determinada, para poder seleccionar un puesto desocupado antes de solicitar mi reserva.

**Why this priority**: Es la funcionalidad base de solo lectura (MVP). Sin la capacidad de saber qué puestos están libres u ocupados en un horario dado, ninguna reserva válida puede planificarse.

**Independent Test**: Puede probarse de forma independiente registrando laboratorios y puestos de prueba, y consultando la disponibilidad para un intervalo dado, verificando que se listen únicamente los puestos libres.

**Acceptance Scenarios**:
1. **Given** un laboratorio con 10 puestos y 2 reservas existentes entre 10:00 y 12:00, **When** un estudiante consulta disponibilidad para ese laboratorio de 10:00 a 12:00, **Then** el sistema responde con una lista de exactamente los 8 puestos libres.
2. **Given** un rango de horario con hora de fin menor o igual a la hora de inicio, **When** el estudiante consulta disponibilidad, **Then** el sistema rechaza la solicitud indicando que el intervalo de tiempo es inválido.
3. **Given** un identificador de laboratorio inexistente, **When** se consulta la disponibilidad, **Then** el sistema retorna un error indicando recurso no encontrado.

---

### User Story 2 - Creación de Reserva con Reglas de Negocio (Priority: P2)

Como estudiante universitario, quiero reservar un puesto de trabajo libre para una fecha y horario específicos, para asegurar mi lugar de estudio o práctica de laboratorio.

**Why this priority**: Es la acción transaccional principal del sistema donde se aplican las restricciones de negocio críticas para evitar acaparamientos y conflictos.

**Independent Test**: Puede probarse creando una reserva para un puesto libre dentro de los límites y verificando que quede persistida en estado "CONFIRMADA", y luego intentando solapar otra reserva para comprobar su rechazo.

**Acceptance Scenarios**:
1. **Given** un puesto libre y un estudiante sin reservas activas pendientes, **When** el estudiante solicita una reserva por una duración de 2 horas o menos, **Then** el sistema registra la reserva con estado `CONFIRMED` y devuelve su identificador único.
2. **Given** un puesto que ya tiene una reserva confirmada de 14:00 a 16:00, **When** otro estudiante intenta reservar ese mismo puesto de 15:00 a 17:00, **Then** el sistema rechaza la reserva por conflicto de horario (solapamiento).
3. **Given** una solicitud de reserva con una duración superior a 2 horas (ej. 3 horas), **When** el estudiante envía la solicitud, **Then** el sistema rechaza la reserva indicando que la duración máxima permitida es de 2 horas.
4. **Given** un estudiante que ya cuenta con una reserva activa en estado `CONFIRMED`, **When** intenta reservar un segundo puesto para el mismo o diferente horario, **Then** el sistema rechaza la solicitud informando que solo se permite 1 reserva activa por estudiante.

---

### User Story 3 - Cancelación Oportuna de Reserva (Priority: P3)

Como estudiante con una reserva activa, quiero poder cancelar mi reserva si mis planes cambian, para liberar el puesto para otros compañeros.

**Why this priority**: Fomenta el uso eficiente de los recursos y el reciclaje de puestos vacíos, aplicando una política de tiempo razonable.

**Independent Test**: Puede probarse cancelando una reserva programada a futuro y verificando que su estado cambie a `CANCELLED`, y que dicho puesto vuelva a figurar como disponible en las consultas.

**Acceptance Scenarios**:
1. **Given** una reserva confirmada que iniciará en más de 30 minutos a partir del momento actual, **When** el titular solicita la cancelación, **Then** el sistema actualiza el estado a `CANCELLED` y libera el puesto.
2. **Given** una reserva confirmada cuyo inicio está a menos de 30 minutos o que ya ha iniciado, **When** el titular intenta cancelarla, **Then** el sistema rechaza la cancelación indicando que el plazo permitido (mínimo 30 minutos antes del inicio) ha expirado.
3. **Given** una reserva que ya fue previamente cancelada, **When** se solicita cancelarla nuevamente, **Then** el sistema informa que la reserva no está en estado activo.

---

### Edge Cases

- **Reservas en el pasado:** El sistema rechaza cualquier intento de reservar en un horario anterior al momento actual.
- **Puestos fuera de servicio:** Los puestos marcados como `MAINTENANCE` o inactivos no pueden ser reservados bajo ninguna circunstancia.
- **Concurrencia exacta:** Dos solicitudes simultáneas para el mismo puesto y horario exacto deben resolverse atómicamente: una triunfa y la otra falla limpiamente sin corromper el estado.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir registrar y listar laboratorios y sus puestos de cómputo asociados.
- **FR-002**: El sistema DEBE permitir consultar la disponibilidad de puestos en un laboratorio para un rango `[start_time, end_time]` dado.
- **FR-003**: El sistema DEBE validar que `end_time > start_time` y que la duración total no supere los 120 minutos (2 horas).
- **FR-004**: El sistema DEBE rechazar reservas para fechas/horas pasadas.
- **FR-005**: El sistema DEBE impedir el solapamiento de dos reservas en el mismo puesto de trabajo para rangos de tiempo que intersecten.
- **FR-006**: El sistema DEBE garantizar que un estudiante (`student_id`) tenga como máximo una reserva en estado `CONFIRMED`.
- **FR-007**: El sistema DEBE permitir al titular cancelar su reserva únicamente si restan al menos 30 minutos antes del `start_time`.
- **FR-008**: El sistema DEBE responder con códigos y mensajes de error estructurados cuando una regla de negocio no se cumpla (409 Conflict, 400 Bad Request, 404 Not Found, 422 Unprocessable Entity).

### Key Entities

- **Laboratory**: Representa un espacio físico del campus (código, nombre, pabellón, capacidad total, estado activo).
- **Workstation**: Representa una estación de cómputo en un laboratorio (número/código de puesto, especificaciones, estado operativo `AVAILABLE` | `MAINTENANCE`).
- **Reservation**: Representa el turno asignado a un estudiante (id, workstation_id, student_id, student_email, start_time, end_time, status `CONFIRMED` | `CANCELLED` | `COMPLETED`, created_at).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La consulta de disponibilidad y cálculo de solapamientos se completa en menos de 50 milisegundos en pruebas de integración.
- **SC-002**: El 100% de las transacciones en conflicto de horario o violación de reglas de negocio son capturadas y rechazadas con mensajes legibles sin generar estados inconsistentes.
- **SC-003**: 100% de aprobación en la suite de pruebas unitarias y de integración que verifican los escenarios de aceptación BDD.

---

## Assumptions

- Cada estudiante se identifica de forma unívoca mediante su `student_id` (código de estudiante) y un correo institucional válido.
- La granularidad de las reservas es a nivel de minuto/hora exacta dentro del mismo día calendario.
- El sistema opera en la zona horaria local universitaria (UTC-5 / Lima/Arequipa).
