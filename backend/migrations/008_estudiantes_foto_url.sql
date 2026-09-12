-- Migración 008: Añade columna foto_url a la tabla estudiantes
-- Fecha: 2026-07

ALTER TABLE estudiantes
    ADD COLUMN IF NOT EXISTS foto_url TEXT DEFAULT NULL;

COMMENT ON COLUMN estudiantes.foto_url IS
    'Nombre del archivo de foto almacenado en assets/, ej: EST-205_foto.jpg';
