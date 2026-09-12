-- ============================================================
-- Migración 004 — Escala de valoración y Calificaciones
-- ============================================================

-- ── Secuencia ─────────────────────────────────────────────────────────────────
CREATE SEQUENCE IF NOT EXISTS seq_id_calificacion START 1 INCREMENT 1;

-- ── Tabla: escala_valoracion ──────────────────────────────────────────────────
-- Niveles de desempeño configurables (rangos numéricos → etiqueta)
CREATE TABLE IF NOT EXISTS escala_valoracion (
    id_nivel    VARCHAR(20)     PRIMARY KEY,     -- 'BAJO','BASICO','ALTO','SUPERIOR'
    nombre      VARCHAR(40)     NOT NULL,
    valor_min   NUMERIC(4,2)    NOT NULL,
    valor_max   NUMERIC(4,2)    NOT NULL,
    descripcion TEXT,
    orden       SMALLINT        NOT NULL DEFAULT 1,
    CONSTRAINT chk_ev_rango CHECK (valor_min < valor_max)
);

-- Datos por defecto (escala colombiana 0–5)
INSERT INTO escala_valoracion (id_nivel, nombre, valor_min, valor_max, descripcion, orden)
VALUES
    ('BAJO',     'Desempeño Bajo',     0.00, 2.99, 'El estudiante no alcanza los desempeños básicos.', 1),
    ('BASICO',   'Desempeño Básico',   3.00, 3.89, 'El estudiante supera los desempeños mínimos.', 2),
    ('ALTO',     'Desempeño Alto',     3.90, 4.59, 'El estudiante supera satisfactoriamente los desempeños.', 3),
    ('SUPERIOR', 'Desempeño Superior', 4.60, 5.00, 'El estudiante supera ampliamente los desempeños.', 4)
ON CONFLICT (id_nivel) DO NOTHING;

-- ── Tabla: calificaciones ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS calificaciones (
    id_calificacion VARCHAR(20)     PRIMARY KEY,
    id_matricula    INTEGER         NOT NULL
                                    REFERENCES matriculas(id_matricula) ON DELETE CASCADE,
    id_asignatura   VARCHAR(20)     NOT NULL
                                    REFERENCES asignaturas(id_asignatura) ON DELETE CASCADE,
    numero_periodo  SMALLINT        NOT NULL CHECK (numero_periodo BETWEEN 1 AND 4),
    ano_lectivo     INTEGER         NOT NULL,
    valor           NUMERIC(4,2)    NOT NULL CHECK (valor >= 0 AND valor <= 10),
    observacion     TEXT,
    fecha_registro  TIMESTAMPTZ     NOT NULL DEFAULT now(),
    CONSTRAINT uq_calificacion UNIQUE (id_matricula, id_asignatura, numero_periodo)
);

COMMENT ON TABLE escala_valoracion IS 'Rangos numéricos → niveles de desempeño (Bajo/Básico/Alto/Superior).';
COMMENT ON TABLE calificaciones     IS 'Una nota por estudiante × asignatura × período académico.';
