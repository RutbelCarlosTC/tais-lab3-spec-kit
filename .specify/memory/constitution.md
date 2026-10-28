<!--
Sync Impact Report:
- Version change: 1.2.0 -> 1.3.0
- Amendment: Added Principle VIII for Real-Time Event Synchronization (SSE) and Workstation Operational Visibility.
  1. Separation of Concerns & Modular Architecture
  2. Test-Driven Development (TDD) and Test Isolation
  3. Strict Typing and Schema Validation (Pydantic v2)
  4. Explicit Error Contracts and HTTP Statuses
  5. Simplicity & YAGNI
  6. Modern, Responsive Web Interface (Rich Aesthetics, Glassmorphism, Real-Time Feedback)
  7. Stateless JWT Authentication, Ownership Security & RBAC
  8. Real-Time Event Synchronization (SSE) & Workstation Operational Visibility (NEW)
-->

# LabReserve Constitution

## Core Principles

### I. Modular Architecture & Clean Separation
Every component MUST have a single, well-defined responsibility:
- `models`: Pure database persistence definitions (SQLAlchemy 2.0 async).
- `schemas`: Strict data transfer objects, request/response validation (Pydantic v2).
- `services`: Pure domain business logic, independent of HTTP transport.
- `api`: REST HTTP controllers, dependency injection, routing, and status code translation.
- `frontend`: Decoupled presentation layer communicating exclusively via HTTP/JSON and SSE.
Direct database access from API route handlers or client-side is STRICTLY PROHIBITED.

### II. Test-Driven Development (TDD) (NON-NEGOTIABLE)
Quality is validated through executable specifications:
- All domain rules (limits, overlap detection, cancellation window, authorization checks) MUST be covered by unit tests.
- Tests MUST run asynchronously with an isolated SQLite in-memory database per test run.
- No feature is considered complete until all tests pass with 100% green status.

### III. Strict Typing & Schema Validation
All inputs and outputs MUST be explicitly typed:
- No dynamic typing (`Any`) in public service methods or API endpoints.
- Pydantic v2 models MUST validate formats (ISO-8601 timestamps, email formats, positive durations).

### IV. Explicit Error Contracts & HTTP Semantics
Failure modes MUST be predictable and informative:
- Business rule violations MUST raise custom domain exceptions.
- Global exception handlers MUST map domain exceptions to standard JSON error objects with clear HTTP status codes (400, 401, 403, 404, 409, 422).

### V. Simplicity & YAGNI
Do not add speculative abstractions. Implement the minimal sufficient solution that satisfies the specification criteria and passes convergence tests.

### VI. Modern Web Interface & User Experience
The client-side presentation layer MUST adhere to modern aesthetic and functional guidelines:
- **Design System:** Sleek dark mode / glassmorphism, curated palette (indigo, cyan, emerald, amber), modern typography (Inter/Outfit via Google Fonts), smooth transitions and micro-interactions.
- **Zero-Friction Serving:** Integrated directly into the FastAPI server as static assets.

### VII. Stateless JWT Authentication, Ownership Security & RBAC
- Stateless JSON Web Tokens (JWT) signed using HMAC-SHA256.
- Role-based authorization (`STUDENT` vs `ADMIN`). Passwords hashed with bcrypt.
- Students can only manage their own reservations. Admins have oversight and emergency bypass capabilities.

### VIII. Real-Time Event Synchronization (SSE) & Workstation Visibility (NEW)
Concurrency issues (such as two students seeing the same PC as green simultaneously) MUST be eliminated via real-time reactive updates:
- **Server-Sent Events (SSE):** The backend MUST broadcast domain lifecycle events (`workstation_occupied`, `workstation_freed`, `workstation_status_changed`) over a persistent HTTP streaming endpoint (`/api/events`).
- **Reactive UI:** Connected web clients MUST subscribe to the event stream via native `EventSource` and update workstation states (green $\leftrightarrow$ red $\leftrightarrow$ yellow) in real time without full page reloads.
- **Complete Operational Visibility:** Workstations in maintenance (`MAINTENANCE`) MUST NOT be hidden from queries; they MUST be returned with explicit status and rendered in amber/yellow in the grid, allowing administrators to easily toggle maintenance ON or OFF.

## Technology Stack Constraints

- Runtime: Python 3.11+
- Package & Environment Manager: `uv`
- Web Framework: FastAPI (REST API + Static SPA + Streaming SSE)
- Event Broadcasting: Asynchronous in-memory Pub/Sub (`asyncio.Queue`)
- Authentication: PyJWT + bcrypt
- ORM / Persistence: SQLAlchemy 2.0 (asyncio + aiosqlite)
- Data Validation: Pydantic v2
- Test Runner: Pytest + `pytest-asyncio` + `httpx`
- Frontend: HTML5 Semántico, Vanilla CSS3 (Glassmorphism), Vanilla Modern JavaScript (ES6+ async/await, EventSource SSE)

## Governance

- The Constitution supersedes ad-hoc coding decisions.
- Amendments to this constitution require a version bump following semantic versioning rules.

**Version**: 1.3.0 | **Ratified**: 2026-10-26 | **Last Amended**: 2026-10-26
