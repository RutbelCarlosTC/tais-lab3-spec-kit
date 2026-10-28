# Implementation Plan: Interfaz Web Interactiva (LabReserve Frontend)

**Branch**: `002-web-interface` | **Date**: 2026-10-26 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/002-web-interface/spec.md`

## Summary

Desarrollar una aplicación web interactiva (Single Page Application - SPA) de alta fidelidad estética que consuma los endpoints REST de LabReserve. La interfaz se alojará en `src/static/` y será servida directamente por FastAPI, permitiendo consultar disponibilidad visualmente en tiempo real, reservar puestos mediante modales interactivos y gestionar o cancelar turnos con retroalimentación visual clara.

## Technical Context

**Language/Frontend**: HTML5 Semántico, Vanilla CSS3 Moderno (CSS Custom Properties, Glassmorphism, CSS Grid), Vanilla JavaScript ES6+ (Async/Await, Fetch API, DOM modular).  
**Backend Serving**: `fastapi.staticfiles.StaticFiles` montado en `src/main.py`.  
**Aesthetics & UX**:
- Tipografía moderna: Google Fonts (*Outfit* para encabezados, *Inter* para interfaz).
- Esquema de colores: Dark mode inmersivo (Slate `#0B0F19`, acentos Índigo `#6366F1`, Esmeralda `#10B981` para disponible, Carmesí `#F43F5E` para ocupado/cancelado, Ámbar `#F59E0B` para alertas).
- Efectos visuales: Glassmorphism (`backdrop-filter: blur(16px)`), sombras de profundidad, microanimaciones de entrada y feedback de botones.
- Componentes: Header con selector de laboratorio y hora, Cuadrícula reactiva de puestos, Modal de Reserva rápida, Pestaña de Gestión de Turnos y Toast de Notificaciones globales.
- Endpoint auxiliar para demo: `POST /api/demo/seed` para sembrar laboratorios y puestos con un solo clic.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Requisito de la Constitución | Estado | Evidencia de Cumplimiento |
| :--- | :--- | :---: | :--- |
| **I. Arquitectura Modular** | Separación entre presentación y backend | **PASS** | El frontend vive en `src/static/` y se comunica exclusivamente vía API HTTP. |
| **II. TDD & Aislamiento** | Verificación de rutas estáticas y endpoints | **PASS** | Nuevos tests en `tests/test_frontend.py` para asegurar que el frontend y el endpoint seed respondan 200 OK. |
| **III. Tipado y Pydantic** | Validación de respuestas de la API | **PASS** | El frontend consume directamente los esquemas ya validados en el backend. |
| **IV. Contratos de Error** | Códigos semánticos y mensajes legibles | **PASS** | El cliente JS intercepta errores 400, 404, 409 y despliega mensajes explicativos en pantalla. |
| **VI. Interfaz Web y UX** | Estética premium y carga sin fricción | **PASS** | Glassmorphism, diseño responsivo y sin necesidad de procesos de compilación adicionales. |

## Project Structure

```text
src/
├── main.py                  # Se añade el montaje de StaticFiles y ruta de inicio
├── api/
│   ├── routes_laboratories.py
│   ├── routes_reservations.py
│   └── routes_demo.py       # Endpoint POST /api/demo/seed para demostración
└── static/                  # Frontend SPA
    ├── index.html           # Estructura semántica de la interfaz
    ├── css/
    │   └── style.css        # Sistema de diseño, variables, glassmorphism y animaciones
    └── js/
        └── app.js           # Cliente API, renderizado de cuadrícula, modales y toasts

tests/
├── test_frontend.py         # Test de entrega de archivos estáticos y endpoint seed
```
