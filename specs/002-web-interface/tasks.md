# Tasks: Interfaz Web Interactiva (LabReserve Frontend)

Feature: `002-web-interface`  
Spec: [spec.md](./spec.md) | Plan: [plan.md](./plan.md)

## Phase 1: Setup (Infraestructura Frontend y Endpoint Demo)

**Purpose**: Habilitar el servicio de archivos estáticos y endpoint de datos de prueba.

- [x] T001 Crear estructura de directorios `src/static/css/` y `src/static/js/`.
- [x] T002 Implementar endpoint de demostración `POST /api/demo/seed` en `src/api/routes_demo.py` para sembrar laboratorios y puestos iniciales.
- [x] T003 Montar `StaticFiles` y servir la SPA en `src/main.py`.

---

## Phase 2: Diseño y Maquetación (UI / Glassmorphism Design System)

**Purpose**: Estructura semántica HTML y estilos modernos acordes al principio de estética premium.

- [x] T004 [US1, US2, US3] Crear `src/static/index.html` con estructura semántica: barra de navegación, selector de laboratorio, controles de intervalo temporal, cuadrícula interactiva de puestos, modal de reserva rápida, panel de gestión de turnos y contenedor de toasts flotantes.
- [x] T005 Crear `src/static/css/style.css` implementando paleta de colores HSL/Hex moderna, tema oscuro profundo, efectos de glassmorphism, tarjetas reactivas, estados de puestos (disponible, ocupado, mantenimiento) y microanimaciones fluidas.

---

## Phase 3: Interactividad y Consumo de API REST (JavaScript SPA)

**Purpose**: Lógica cliente en `src/static/js/app.js` comunicándose con los endpoints REST.

- [x] T006 [US1] Implementar carga dinámica de laboratorios en el selector y consulta de disponibilidad horaria mediante `fetch()`.
- [x] T007 [US1] Implementar renderizado de puestos de cómputo en la cuadrícula con badges de estado y listeners de selección.
- [x] T008 [US2] Implementar modal de reserva interactiva con validación de inputs y envío a `POST /api/reservations`.
- [x] T009 [US3] Implementar panel para consultar reservas por ID y cancelar turnos con retroalimentación visual clara.
- [x] T010 [US4] Implementar botón de carga de datos demo que invoca `POST /api/demo/seed` y refresca la interfaz automáticamente.
- [x] T011 Implementar sistema de toasts y banners para mostrar retroalimentación de éxito y mensajes de error estructurados del backend (400, 404, 409).

---

## Phase 4: Verificación y Convergencia

**Purpose**: Pruebas automáticas y cierre de requerimientos.

- [x] T012 Escribir tests de integración en `tests/test_frontend.py` para verificar entrega de `index.html`, `style.css`, `app.js` y el endpoint `/api/demo/seed`.
- [x] T013 Ejecutar `uv run pytest -v` asegurando 100% de tests aprobados (15/15 passing).
- [x] T014 Validar convergencia y generar reporte final `convergence.md`.
