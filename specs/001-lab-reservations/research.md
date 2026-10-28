# Research & Design Decisions: Sistema de Reservas de Laboratorios

## Decision 1: Detección de Solapamiento Temporal (Interval Scheduling)

- **Problema:** ¿Cómo determinar si dos reservas $[S_1, E_1)$ y $[S_2, E_2)$ entran en conflicto?
- **Decisión:** Dos intervalos se intersecan si y solo si:
  $$\max(S_1, S_2) < \min(E_1, E_2) \iff S_1 < E_2 \land S_2 < E_1$$
  En SQL/SQLAlchemy se implementa en la cláusula WHERE:
  ```python
  Reservation.start_time < new_end_time and Reservation.end_time > new_start_time
  ```
- **Trade-off:** La verificación a nivel de consulta con filtro sobre `workstation_id` y `status == 'CONFIRMED'` es eficiente y aprovecha índices compuestos `(workstation_id, status, start_time, end_time)`.

## Decision 2: Validación de Ventana de Cancelación (30 minutos)

- **Problema:** Asegurar que la cancelación solo ocurra si faltan 30 minutos o más para el `start_time`.
- **Decisión:** 
  ```python
  current_time = datetime.now(timezone.utc)
  if reservation.start_time - current_time < timedelta(minutes=30):
      raise CancellationWindowExpiredError("No es posible cancelar con menos de 30 minutos de anticipación")
  ```
- **Trade-off:** Para testing determinista, el servicio admite inyectar una fecha/hora de referencia (`current_time: datetime | None = None`).

## Decision 3: Persistencia Asíncrona con SQLAlchemy 2.0 y SQLite

- **Problema:** Evitar bloqueo en el loop de eventos de FastAPI mientras se mantiene simplicidad de despliegue sin requerir un servidor PostgreSQL externo para laboratorios locales.
- **Decisión:** Utilizar `aiosqlite` como driver para SQLAlchemy async (`AsyncSession`, `async_sessionmaker`).
- **Trade-off:** Permite pruebas ultra rápidas en memoria (`sqlite+aiosqlite:///:memory:`) y base de datos persistente en archivo simple para desarrollo.
