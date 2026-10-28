# Data Model: Sistema de Reservas de Laboratorios (LabReserve)

## Entidades y Relaciones

```mermaid
erDiagram
    LABORATORY ||--o{ WORKSTATION : contains
    WORKSTATION ||--o{ RESERVATION : receives

    LABORATORY {
        int id PK
        string code UK "Código único (ej. LAB-CS-101)"
        string name "Nombre descriptivo"
        string location "Pabellón / Aula"
        boolean is_active "Estado del laboratorio"
    }

    WORKSTATION {
        int id PK
        int laboratory_id FK
        string code "Número/código de puesto (ej. WS-01)"
        string description "Hardware / Observaciones"
        string status "AVAILABLE | MAINTENANCE"
    }

    RESERVATION {
        int id PK
        int workstation_id FK
        string student_id "Código universitario del estudiante"
        string student_email "Correo institucional"
        datetime start_time "Hora de inicio"
        datetime end_time "Hora de fin"
        string status "CONFIRMED | CANCELLED | COMPLETED"
        datetime created_at "Timestamp de creación"
    }
```

## Reglas de Invariante de Datos

1. **Unicidad de Puesto en Laboratorio:** `(laboratory_id, code)` debe ser único.
2. **Duración de Reserva:** `end_time - start_time <= 2 hours` y `end_time > start_time`.
3. **Restricción de Estado de Reserva:** Solo las reservas en estado `CONFIRMED` computan para:
   - Solapamiento de horario en un puesto.
   - Restricción de 1 reserva activa por estudiante.
