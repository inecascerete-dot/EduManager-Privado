-- ============================================================
-- Migración 006 — Eslogan + Escudo en instituciones / CRUD Grados
-- ============================================================

-- ── Nuevas columnas en instituciones ──────────────────────────────────────────
ALTER TABLE instituciones
    ADD COLUMN IF NOT EXISTS eslogan    TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS escudo_url TEXT NOT NULL DEFAULT '';

-- ── Columna orden en grados (para control de secuencia en menús) ──────────────
ALTER TABLE grados
    ADD COLUMN IF NOT EXISTS orden SMALLINT NOT NULL DEFAULT 99;

-- Asignar orden a los grados existentes
UPDATE grados SET orden =  0 WHERE id_grado = 'GRA-PR';
UPDATE grados SET orden =  1 WHERE id_grado = 'GRA-01';
UPDATE grados SET orden =  2 WHERE id_grado = 'GRA-02';
UPDATE grados SET orden =  3 WHERE id_grado = 'GRA-03';
UPDATE grados SET orden =  4 WHERE id_grado = 'GRA-04';
UPDATE grados SET orden =  5 WHERE id_grado = 'GRA-05';
UPDATE grados SET orden =  6 WHERE id_grado = 'GRA-06';
UPDATE grados SET orden =  7 WHERE id_grado = 'GRA-07';
UPDATE grados SET orden =  8 WHERE id_grado = 'GRA-08';
UPDATE grados SET orden =  9 WHERE id_grado = 'GRA-09';
UPDATE grados SET orden = 10 WHERE id_grado = 'GRA-10';
UPDATE grados SET orden = 11 WHERE id_grado = 'GRA-11';

COMMENT ON COLUMN grados.orden IS 'Orden de aparición en selectores (menor primero).';
COMMENT ON COLUMN instituciones.eslogan IS 'Lema o eslogan institucional, aparece en boletines y encabezados.';
COMMENT ON COLUMN instituciones.escudo_url IS 'Nombre del archivo del escudo/imagen secundaria en assets/.';
