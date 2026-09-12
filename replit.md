# Dica Director Escolar

Sistema de gestión académica para instituciones educativas colombianas. Permite registrar y consultar estudiantes, personal docente y matrículas.

## Stack

- **Frontend/UI:** Streamlit (`app.py`)
- **Backend:** Python (`backend/db_manager.py`)
- **Base de datos:** PostgreSQL (Replit built-in)
- **Paquetes:** streamlit, psycopg2-binary, streamlit-searchbox

## Cómo ejecutar

```bash
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

O usar el workflow **"Start application"** en Replit.

## Estructura

```
app.py               # Interfaz Streamlit (menú, formularios, consultas)
backend/
  db_manager.py      # Funciones de conexión y CRUD PostgreSQL
  matriculas.py      # Lógica adicional de matrículas
  comunidad.py       # Módulo comunidad
assets/              # Fotos de personal
docs/                # Modelo de base de datos
```

## Base de datos

Usa las variables de entorno de Replit (`DATABASE_URL`, `PGHOST`, etc.) — no hay credenciales en el código.

Tablas principales: `instituciones`, `sedes`, `jornadas`, `grados`, `cursos`, `personal`, `estudiantes`, `acudientes`, `matriculas`.

## User preferences

- Idioma de la interfaz: Español (Colombia)
- La institución por defecto es `INST-DICA`
