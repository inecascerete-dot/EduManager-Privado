-- ============================================================
-- Migración 003 — Períodos académicos e Indicadores de desempeño
-- ============================================================

-- ── Secuencias ────────────────────────────────────────────────────────────────
CREATE SEQUENCE IF NOT EXISTS seq_id_periodo    START 1 INCREMENT 1;
CREATE SEQUENCE IF NOT EXISTS seq_id_indicador  START 1 INCREMENT 1;

-- ── Tabla: periodos_academicos ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS periodos_academicos (
    id_periodo      VARCHAR(20)     PRIMARY KEY,
    ano_lectivo     INTEGER         NOT NULL,
    numero          SMALLINT        NOT NULL CHECK (numero BETWEEN 1 AND 4),
    nombre          VARCHAR(80)     NOT NULL,
    fecha_inicio    DATE,
    fecha_fin       DATE,
    porcentaje      NUMERIC(5,2)    NOT NULL DEFAULT 25.00
                                    CHECK (porcentaje > 0 AND porcentaje <= 100),
    CONSTRAINT uq_periodo_ano_num UNIQUE (ano_lectivo, numero),
    CONSTRAINT chk_fechas_periodo CHECK (
        fecha_inicio IS NULL OR fecha_fin IS NULL OR fecha_inicio <= fecha_fin
    )
);

-- ── Tabla: indicadores_desempeno ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS indicadores_desempeno (
    id_indicador    VARCHAR(20)     PRIMARY KEY,
    ano_lectivo     INTEGER         NOT NULL,
    id_grado        VARCHAR(20)     NOT NULL REFERENCES grados(id_grado) ON DELETE CASCADE,
    id_asignatura   VARCHAR(20)     NOT NULL REFERENCES asignaturas(id_asignatura) ON DELETE CASCADE,
    numero_periodo  SMALLINT        NOT NULL CHECK (numero_periodo BETWEEN 1 AND 4),
    descripcion     TEXT            NOT NULL,
    tipo            VARCHAR(40)     NOT NULL DEFAULT 'Cognitivo'
                                    CHECK (tipo IN ('Cognitivo','Procedimental','Actitudinal'))
);

COMMENT ON TABLE periodos_academicos   IS 'Períodos académicos por año lectivo con peso porcentual.';
COMMENT ON TABLE indicadores_desempeno IS 'Indicadores / aprendizajes esperados por grado, asignatura y período.';
