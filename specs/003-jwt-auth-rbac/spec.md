# Feature Specification: Autenticación JWT, Flujo "Mis Reservas" (/me) y RBAC

**Feature Branch**: `003-jwt-auth-rbac`  
**Created**: 2026-10-26  
**Status**: Specified & Ready for Planning  
**Input**: User description: "Implementar autenticación con JWT, eliminación de ingreso manual de IDs en reserva (reserva en 1 clic e inferencia desde token), flujo 'Mis Reservas' (/api/reservations/me), control de acceso basado en roles (Estudiante vs Administrador) y vistas diferenciadas en el frontend para ambos tipos de usuarios con login integrado."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autenticación con JWT y Control de Sesión (Priority: P1)

Como usuario del sistema (estudiante o administrador), quiero iniciar sesión con mis credenciales institucionales y recibir un token JWT firmado para mantener mi sesión activa y autenticada en el frontend.

**Why this priority**: Es la base criptográfica indispensable para suprimir el ingreso manual de credenciales en cada reserva y para habilitar el control de acceso por roles (RBAC).

**Independent Test**: Puede probarse enviando credenciales a `POST /api/auth/login`, comprobando que devuelva un access token JWT válido con claims de identidad y rol, y que credenciales inválidas retornen `401 Unauthorized`.

**Acceptance Scenarios**:
1. **Given** un usuario registrado con contraseña válida, **When** solicita login mediante `POST /api/auth/login`, **Then** el sistema responde con HTTP 200 y un token JWT con `sub`, `email`, `role` y `full_name`.
2. **Given** una contraseña incorrecta o un usuario no existente, **When** solicita login, **Then** el sistema retorna HTTP 401 con mensaje descriptivo de credenciales no válidas.
3. **Given** un token JWT válido, **When** se consulta `GET /api/auth/me`, **Then** retorna el perfil del usuario autenticado.

---

### User Story 2 - Flujo "Mis Reservas" (/me) y Reserva en 1 Clic (Priority: P2)

Como estudiante autenticado, quiero reservar un puesto de cómputo en 1 solo clic (sin escribir mi código ni correo manualmente) y consultar automáticamente la lista de todas mis reservas activas y pasadas en la pestaña "Mis Reservas".

**Why this priority**: Elimina fricción de uso y errores de digitación, garantizando que el usuario solo pueda reservar a su propio nombre y revisar su historial.

**Independent Test**: Iniciar sesión como estudiante, abrir el modal de reserva (los datos del estudiante aparecen ya pre-llenados/bloqueados), confirmar la reserva, y verificar que aparezca inmediatamente en `GET /api/reservations/me`.

**Acceptance Scenarios**:
1. **Given** un estudiante autenticado y un puesto disponible, **When** pulsa "Confirmar Turno", **Then** el backend extrae su identidad directamente del token JWT, persiste la reserva y la asocia a su ID.
2. **Given** un estudiante con reservas creadas, **When** ingresa a la pestaña "Mis Reservas", **Then** el frontend invoca `GET /api/reservations/me` y despliega todas sus tarjetas con su estado actual (CONFIRMED, CANCELLED).
3. **Given** una reserva propia activa que inicia en más de 30 minutos, **When** el estudiante hace clic en "Cancelar Reserva" desde su tarjeta, **Then** la reserva se cancela y el puesto se libera.

---

### User Story 3 - Panel de Administrador / Encargado de Laboratorio (Priority: P3)

Como administrador del laboratorio, quiero acceder a una vista administrativa especial donde pueda ver todas las reservas de la jornada, cancelar reservas por emergencia técnica (sin restricción de 30 minutos) y bloquear/desbloquear puestos de cómputo (conmutar a Mantenimiento).

**Why this priority**: Permite a los encargados gestionar la operatividad física del laboratorio, suspender puestos averiados y atender imprevistos institucionales.

**Independent Test**: Iniciar sesión como administrador, listar todas las reservas mediante `GET /api/reservations`, cancelar una reserva de cualquier estudiante y alternar el estado de un puesto de cómputo mediante `PATCH /api/workstations/{id}/status`.

**Acceptance Scenarios**:
1. **Given** un usuario autenticado con rol `ADMIN`, **When** accede a la plataforma, **Then** visualiza la pestaña "Panel de Administración" con la lista de todas las reservas registradas.
2. **Given** un administrador, **When** solicita cancelar una reserva de cualquier estudiante (incluso a menos de 30 minutos del inicio), **Then** el sistema procesa la cancelación por anulación administrativa.
3. **Given** un administrador, **When** cambia el estado de un puesto a `MAINTENANCE`, **Then** el puesto queda bloqueado para nuevas reservas y se muestra en color ámbar en el mapa.

---

### User Story 4 - Control de Acceso por Roles (RBAC) y Seguridad (Priority: P4)

Como administrador del sistema, quiero garantizar que los estudiantes no puedan invocar operaciones administrativas ni manipular turnos ajenos.

**Acceptance Scenarios**:
1. **Given** una solicitud a un endpoint protegido sin cabecera `Authorization: Bearer <token>`, **When** se evalúa la petición, **Then** el sistema responde con HTTP 401 Unauthorized.
2. **Given** un estudiante autenticado con rol `STUDENT`, **When** intenta llamar a un endpoint exclusivo de administración (ej. listar todas las reservas de todos los alumnos o cambiar estado de puestos), **Then** el sistema responde con HTTP 403 Forbidden.
3. **Given** un estudiante intentando cancelar una reserva que pertenece a otro alumno, **When** envía la solicitud, **Then** el sistema deniega la acción.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-AUTH-01**: El sistema DEBE almacenar contraseñas encriptadas con algoritmo seguro `bcrypt`.
- **FR-AUTH-02**: El sistema DEBE proveer el endpoint `POST /api/auth/login` que recibe credenciales y genera un JSON Web Token (JWT) firmado con algoritmo HS256.
- **FR-AUTH-03**: El sistema DEBE proveer el endpoint `GET /api/auth/me` para obtener el perfil del usuario autenticado.
- **FR-AUTH-04**: El sistema DEBE proveer el endpoint `GET /api/reservations/me` que retorna únicamente las reservas correspondientes al usuario emisor del token.
- **FR-AUTH-05**: El endpoint `POST /api/reservations` DEBE inferir el `student_id` y `student_email` a partir del token JWT autenticado.
- **FR-AUTH-06**: El endpoint `POST /api/reservations/{id}/cancel` DEBE permitir cancelar al titular si faltan $\ge 30$ minutos, o a un usuario con rol `ADMIN` en cualquier momento.
- **FR-AUTH-07**: El sistema DEBE exponer `GET /api/reservations` accesible exclusivamente por usuarios con rol `ADMIN`.
- **FR-AUTH-08**: El sistema DEBE exponer `PATCH /api/workstations/{id}/status` accesible exclusivamente por usuarios con rol `ADMIN` para alternar entre `AVAILABLE` y `MAINTENANCE`.
- **FR-AUTH-09**: La interfaz web DEBE incluir un modal/panel de login con opciones rápidas de demostración para "Estudiante Demo" y "Admin Demo", selector de vistas según el rol y botón para cerrar sesión.

---

## Success Criteria *(mandatory)*

- **SC-AUTH-01**: Flujo de reserva completado en 1 solo clic desde el modal sin ingreso manual de datos de estudiante.
- **SC-AUTH-02**: 100% de los accesos indebidos (sin token o con rol insuficiente) bloqueados con códigos 401 y 403.
- **SC-AUTH-03**: Carga instantánea de "Mis Reservas" al iniciar sesión como estudiante y del "Panel Admin" al iniciar sesión como administrador.
