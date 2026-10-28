# Implementation Plan: Autenticación JWT, Flujo "Mis Reservas" (/me) y RBAC

**Branch**: `003-jwt-auth-rbac` | **Date**: 2026-10-26 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/003-jwt-auth-rbac/spec.md`

## Summary

Incorporar autenticación sin estado mediante JSON Web Tokens (JWT) y control de acceso basado en roles (`STUDENT` y `ADMIN`). El sistema elimina el ingreso manual de identificadores de estudiante en el frontend gracias a la inferencia segura desde los claims del token en `POST /api/reservations`, implementa el endpoint `GET /api/reservations/me` para la autogestión de turnos personales y expone un panel de administración con privilegios para supervisión de todas las reservas y control operativo de puestos de cómputo.

## Technical Context

**Language/Version**: Python 3.11+  
**Dependencies**: `pyjwt` (HS256), `bcrypt` (salting y hashing seguro de contraseñas), FastAPI, SQLAlchemy 2.0 async, Pydantic v2.  
**Security Architecture**:
- Algoritmo de firma: HMAC-SHA256 con clave secreta configurable.
- Formato de Authorization: Cabecera estándar `Authorization: Bearer <token>`.
- Entidad `User`: `id`, `username` (código de estudiante / admin ID), `email`, `hashed_password`, `full_name`, `role` (`STUDENT` | `ADMIN`), `is_active`.
- Control de Inferencia: El endpoint de reserva ya no exige `student_id` ni `student_email` en el payload JSON; estos se extraen criptográficamente del token.
- Control de Cancelación: Estudiantes solo pueden cancelar sus propias reservas con $\ge 30$ min de antelación. Administradores pueden cancelar cualquier reserva en cualquier momento.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Requisito de la Constitución | Estado | Evidencia de Cumplimiento |
| :--- | :--- | :---: | :--- |
| **I. Arquitectura Modular** | Capa de seguridad desacoplada | **PASS** | `src/core/security.py` centraliza JWT y hashing. |
| **II. TDD & Aislamiento** | Tests de autenticación y RBAC | **PASS** | `tests/test_auth_rbac.py` verifica 401, 403, 1-click booking y /me. |
| **III. Tipado y Pydantic** | Validación de tokens y login | **PASS** | Esquemas `TokenResponse`, `UserResponse`, `LoginRequest`. |
| **IV. Contratos de Error** | Códigos 401 y 403 semánticos | **PASS** | `AuthenticationError` (401) y `PermissionDeniedError` (403). |
| **VI. Interfaz Web y UX** | Login integrado y vistas por rol | **PASS** | Modal de login con accesos rápidos demo para estudiante y admin. |
| **VII. JWT y RBAC** | Criptografía y protección de turnos | **PASS** | Bcrypt para claves, tokens firmados y verificación de propiedad. |

## Project Structure

```text
src/
├── core/
│   ├── security.py          # Encriptación bcrypt, generación y decodificación de JWT
│   └── exceptions.py        # AuthenticationError (401) y PermissionDeniedError (403)
├── models/
│   └── user.py              # Modelo SQLAlchemy User (STUDENT | ADMIN)
├── schemas/
│   ├── auth.py              # Esquemas Login, Token, UserResponse
│   └── reservation.py       # ReservationCreate simplificado (workstation_id, start_time, end_time)
├── services/
│   ├── auth_service.py      # Lógica de login, hash y verificación
│   └── reservation_service.py # Inferencia de usuario, /me y bypass de cancelación para admin
├── api/
│   ├── deps.py              # Inyección get_current_user y require_admin
│   ├── routes_auth.py       # Endpoints /api/auth/login y /api/auth/me
│   ├── routes_reservations.py # Endpoint /me, listado admin y cancelación por rol
│   └── routes_workstations.py # Endpoint PATCH /api/workstations/{id}/status (Admin)
└── static/
    ├── index.html           # Modal de Login, barra de sesión y vista Admin
    ├── css/style.css        # Estilos para badges de rol, botones rápidos y tarjetas admin
    └── js/app.js            # Gestión de JWT en localStorage, 1-click booking y vistas por rol

tests/
├── test_auth_rbac.py        # Tests completos de autenticación, RBAC y flujo /me
```
