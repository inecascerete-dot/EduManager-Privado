-- Migración 002: Asignaturas, Plan de Estudio y Asignación Docente
-- Descripción:
--   asignaturas       → catálogo de asignaturas de la institución
--   plan_estudio      → qué asignaturas se dictan en cada grado y cuántas horas/semana
--   asignacion_docente → qué docente dicta qué asignatura en qué curso/año

-- ── Secuencias ────────────────────────────────────────────────────────────────
CREATE SEQUENCE IF NOT EXISTS seq_id_asignatura           START WITH 1 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS seq_id_plan_estudio         START WITH 1 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS seq_id_asignacion_docente   START WITH 1 NO CYCLE;

-- ── Catálogo de asignaturas ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS asignaturas (
    id_asignatura     TEXT PRIMARY KEY,
    nombre            TEXT NOT NULL,
    area_conocimiento TEXT NOT NULL,
    descripcion       TEXT
);

-- ── Plan de estudio (asignaturas por grado) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS plan_estudio (
    id_plan           TEXT    PRIMARY KEY,
    id_grado          TEXT    NOT NULL REFERENCES grados(id_grado),
    id_asignatura     TEXT    NOT NULL REFERENCES asignaturas(id_asignatura),
    horas_semana      INTEGER NOT NULL DEFAULT 1,
    -- Una asignatura aparece solo una vez por grado
    CONSTRAINT uq_plan_grado_asg UNIQUE (id_grado, id_asignatura)
);

-- ── Asignación docente ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS asignacion_docente (
    id_asignacion     TEXT    PRIMARY KEY,
    id_curso          TEXT    NOT NULL REFERENCES cursos(id_curso),
    id_personal       TEXT    NOT NULL REFERENCES personal(id_personal),
    id_asignatura     TEXT    NOT NULL REFERENCES asignaturas(id_asignatura),
    ano_lectivo       INTEGER NOT NULL,
    -- Un docente distinto puede dictar la misma asignatura en grupos distintos,
    -- pero una asignatura solo puede tener un docente por curso y año.
    CONSTRAINT uq_asig_curso_asg_ano UNIQUE (id_curso, id_asignatura, ano_lectivo)
);

-- ── Índices ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_plan_grado          ON plan_estudio       (id_grado);
CREATE INDEX IF NOT EXISTS idx_asig_doc_curso      ON asignacion_docente (id_curso);
CREATE INDEX IF NOT EXISTS idx_asig_doc_personal   ON asignacion_docente (id_personal);
CREATE INDEX IF NOT EXISTS idx_asig_doc_ano        ON asignacion_docente (ano_lectivo);
