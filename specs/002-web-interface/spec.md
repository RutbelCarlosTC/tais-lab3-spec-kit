# Feature Specification: Interfaz Web Interactiva (LabReserve Frontend)

**Feature Branch**: `002-web-interface`  
**Created**: 2026-10-26  
**Status**: Specified & Ready for Planning  
**Input**: User description: "Modificar el proyecto para que cuente con una interfaz web (frontend) interactiva, moderna y estética que consuma el microservicio REST de reservas, permitiendo a los estudiantes explorar laboratorios, consultar disponibilidad visualmente, reservar turnos y cancelar reservas."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exploración y Mapa Visual de Puestos (Priority: P1)

Como estudiante o docente, quiero seleccionar un laboratorio y definir un intervalo de tiempo para visualizar un mapa/cuadrícula interactiva de estaciones de trabajo con código de colores (verde = disponible, rojo = ocupado, gris/ámbar = mantenimiento).

**Why this priority**: Es la interfaz base que traduce las respuestas JSON del endpoint `/api/laboratories/{id}/availability` en una experiencia de usuario clara e intuitiva.

**Independent Test**: Puede probarse abriendo el navegador, seleccionando un laboratorio y verificando que los puestos se rendericen dinámicamente con su estado respectivo.

**Acceptance Scenarios**:
1. **Given** un laboratorio con 1 puesto ocupado y 3 libres en el horario seleccionado, **When** el usuario hace clic en "Consultar Disponibilidad", **Then** la cuadrícula muestra 3 tarjetas verdes seleccionables y 1 tarjeta roja bloqueada con la etiqueta "Ocupado".
2. **Given** un intervalo donde la hora de fin es menor o igual a la de inicio, **When** el usuario intenta consultar, **Then** la interfaz muestra una alerta de validación antes de realizar la petición HTTP.

---

### User Story 2 - Flujo Interactivo de Reserva (Priority: P2)

Como estudiante, quiero hacer clic en una estación de trabajo disponible, ingresar mi código de estudiante y correo electrónico institucional, y confirmar la reserva recibiendo un comprobante visual inmediato con su código único de reserva.

**Why this priority**: Es la transacción central que conecta al usuario final con el endpoint `POST /api/reservations`.

**Independent Test**: Puede probarse seleccionando un puesto verde, completando el formulario modal y confirmando; el puesto debe cambiar inmediatamente a ocupado y desplegarse un toast/badge de confirmación.

**Acceptance Scenarios**:
1. **Given** un puesto libre y datos de estudiante válidos, **When** se envía el formulario de reserva, **Then** la interfaz invoca `POST /api/reservations`, muestra un banner de éxito con el ID de reserva y refresca la disponibilidad del laboratorio.
2. **Given** un estudiante que ya tiene una reserva activa previa, **When** intenta reservar otro puesto, **Then** la interfaz intercepta el código de error `409 ACTIVE_RESERVATION_LIMIT` y muestra una notificación clara explicando que ya cuenta con una reserva activa.

---

### User Story 3 - Consulta y Cancelación de Reserva (Priority: P3)

Como estudiante con una reserva realizada, quiero poder consultar el estado de mi reserva ingresando su identificador o mi código y cancelarla si mis planes cambian, siempre que falten más de 30 minutos.

**Why this priority**: Permite la autogestión de turnos y prueba la interacción con el endpoint `POST /api/reservations/{id}/cancel`.

**Independent Test**: Puede probarse buscando una reserva futura y haciendo clic en "Cancelar Reserva"; si la antelación es mayor a 30m, la reserva pasa a estado `CANCELLED` y el puesto se libera.

**Acceptance Scenarios**:
1. **Given** una reserva confirmada con inicio a más de 30 minutos en el futuro, **When** el usuario pulsa "Cancelar Reserva", **Then** el sistema cancela el turno y actualiza visualmente su estado a "Cancelada".
2. **Given** una reserva cuyo inicio está a menos de 30 minutos, **When** el usuario intenta cancelarla, **Then** la interfaz muestra un mensaje de advertencia explicando la política de antelación mínima de 30 minutos (`CANCELLATION_WINDOW_EXPIRED`).

---

### User Story 4 - Inicialización Rápida con Datos Demo (Priority: P4)

Como evaluador o docente, quiero contar con un botón de "Cargar Datos Demo" en la interfaz para poblar automáticamente laboratorios y puestos de prueba sin tener que ejecutar comandos cURL manuales.

**Why this priority**: Facilita enormemente la evaluación académica y demostración en vivo de la práctica.

**Acceptance Scenarios**:
1. **Given** una base de datos vacía, **When** el usuario hace clic en "Sembrar Datos de Demostración", **Then** el sistema registra dos laboratorios y 8 puestos de trabajo y los muestra de inmediato en pantalla.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-W01**: La interfaz DEBE servirse en la raíz del servidor (`/` o `/index.html`) a través de FastAPI StaticFiles.
- **FR-W02**: La interfaz DEBE comunicarse de forma asíncrona mediante `fetch()` con la API REST (`/api/laboratories` y `/api/reservations`).
- **FR-W03**: La interfaz DEBE renderizar una cuadrícula interactiva con los puestos de cómputo del laboratorio activo.
- **FR-W04**: La interfaz DEBE incluir un formulario modal o panel flotante para registrar nuevas reservas con validación de campos.
- **FR-W05**: La interfaz DEBE mostrar un sistema de notificaciones/toasts flotantes (éxito, conflicto, error de validación) que interprete las respuestas del backend.
- **FR-W06**: La interfaz DEBE incluir una sección o pestaña para consultar y cancelar reservas por ID.
- **FR-W07**: El frontend DEBE diseñarse con un estilo moderno, estético y responsivo (tema oscuro premium, glassmorphism, fuentes Inter/Outfit, badges dinámicos).

---

## Success Criteria *(mandatory)*

- **SC-W01**: Carga visual completa de la aplicación en menos de 200ms sin dependencias pesadas de empaquetado (webpack/vite opcional o cliente vanilla optimizado).
- **SC-W02**: Flujo de reserva completable en menos de 3 clics una vez definidos los horarios.
- **SC-W03**: Interfaz 100% responsiva y adaptable a dispositivos móviles y pantallas de escritorio.
