# Tasks: Autenticación JWT, Flujo "Mis Reservas" (/me) y RBAC

Feature: `003-jwt-auth-rbac`  
Spec: [spec.md](./spec.md) | Plan: [plan.md](./plan.md)

## Phase 1: Setup & Foundational (Criptografía, Modelo User y Excepciones)

- [x] T001 Implementar módulo criptográfico en `src/core/security.py` (bcrypt + PyJWT).
- [x] T002 Agregar `AuthenticationError` (401) y `PermissionDeniedError` (403) en `src/core/exceptions.py`.
- [x] T003 Crear modelo `User` en `src/models/user.py` y registrar en `src/models/__init__.py`.
- [x] T004 Crear esquemas Pydantic `LoginRequest`, `TokenResponse`, `UserResponse` en `src/schemas/auth.py`.
- [x] T005 Configurar dependencias de inyección de usuario en `src/api/deps.py` (`get_current_user`, `require_admin`, `get_optional_user`).

---

## Phase 2: User Story 1 (P1) - Login y Autenticación JWT

- [x] T006 [US1] Implementar `AuthService` en `src/services/auth_service.py` y endpoints `POST /api/auth/login` y `GET /api/auth/me` en `src/api/routes_auth.py`.
- [x] T007 [US1] Sembrar usuarios de prueba (`STUDENT` y `ADMIN`) en `src/api/routes_demo.py`.

---

## Phase 3: User Story 2 (P2) - Flujo "Mis Reservas" y Reserva en 1 Clic

- [x] T008 [US2] Actualizar `src/services/reservation_service.py` y `src/api/routes_reservations.py` para:
  - Inyectar identidad del token en `create_reservation` sin exigir `student_id` ni `student_email` en el cuerpo de la petición.
  - Exponer `GET /api/reservations/me` para listar reservas del estudiante emisor del token.
  - Permitir al estudiante cancelar su propia reserva con $\ge 30$ minutos de antelación.

---

## Phase 4: User Story 3 (P3) - Panel Administrador y RBAC

- [x] T009 [US3] Implementar `GET /api/reservations` con filtro de fecha para administradores (`require_admin`).
- [x] T010 [US3] Permitir al administrador cancelar cualquier reserva sin restricción de 30 minutos (anulación por emergencia).
- [x] T011 [US3] Implementar `PATCH /api/workstations/{id}/status` para alternar estado de puestos entre `AVAILABLE` y `MAINTENANCE` (requiere `require_admin`).

---

## Phase 5: Interfaz Web y Experiencia de Usuario (Frontend)

- [x] T012 Actualizar `src/static/index.html` con barra de sesión (usuario, rol, botón de Login/Logout), modal de autenticación con botones de acceso rápido para Estudiante y Administrador, y pestaña del "Panel Admin".
- [x] T013 Actualizar `src/static/css/style.css` con estilos para el modal de login, badges de rol (STUDENT / ADMIN) y tarjetas del panel de administración.
- [x] T014 Actualizar `src/static/js/app.js` para:
  - Gestionar el token JWT en `localStorage`.
  - Renderizar la vista correspondiente al rol autenticado (pestaña "Mis Reservas" para estudiante, "Panel Admin" para administrador).
  - Reserva en 1 clic en el modal sin pedir datos de estudiante (pre-cargados del token).
  - Listar y cancelar reservas automáticamente en "Mis Reservas".
  - Control de estaciones y listado de todas las reservas en "Panel Admin".

---

## Phase 6: Pruebas y Convergencia

- [x] T015 Escribir suite de pruebas de autenticación y RBAC en `tests/test_auth_rbac.py`.
- [x] T016 Actualizar pruebas existentes en `tests/` para usar autenticación adecuada.
- [x] T017 Ejecutar `uv run pytest -v` (18/18 pruebas aprobadas con 100% de éxito).
- [x] T018 Emitir reporte de convergencia en `specs/003-jwt-auth-rbac/convergence.md`.
