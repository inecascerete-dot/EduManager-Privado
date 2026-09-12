-- ============================================================
-- Migración 005 — Nivel de grado y datos de boletín
-- ============================================================

-- ── Agregar columna nivel a grados ────────────────────────────────────────────
ALTER TABLE grados
    ADD COLUMN IF NOT EXISTS nivel VARCHAR(20) NOT NULL DEFAULT 'PRIMARIA'
        CHECK (nivel IN ('PREESCOLAR','PRIMARIA','BACHILLERATO'));

-- Ajustar nivel según los grados existentes
UPDATE grados SET nivel = 'PREESCOLAR'   WHERE id_grado = 'GRA-PR';
UPDATE grados SET nivel = 'PRIMARIA'     WHERE id_grado IN ('GRA-01','GRA-02','GRA-03','GRA-04','GRA-05');
UPDATE grados SET nivel = 'BACHILLERATO' WHERE id_grado IN ('GRA-06','GRA-07','GRA-08','GRA-09','GRA-10','GRA-11');

-- ── Tabla: boletin_datos ──────────────────────────────────────────────────────
-- Inasistencias y observaciones por estudiante y período
CREATE TABLE IF NOT EXISTS boletin_datos (
    id_matricula    INTEGER     NOT NULL REFERENCES matriculas(id_matricula) ON DELETE CASCADE,
    numero_periodo  SMALLINT    NOT NULL CHECK (numero_periodo BETWEEN 1 AND 4),
    inasistencias   SMALLINT    NOT NULL DEFAULT 0 CHECK (inasistencias >= 0),
    observaciones   TEXT        NOT NULL DEFAULT '',
    PRIMARY KEY (id_matricula, numero_periodo)
);

COMMENT ON TABLE boletin_datos IS 'Inasistencias y observaciones del período para cada matrícula.';
