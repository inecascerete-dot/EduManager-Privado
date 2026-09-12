-- Migración 009: agrega columna nivel a asignaturas
-- Valores: PREESCOLAR | PRIMARIA | SECUNDARIA | MEDIA | TODOS (todas las jornadas/niveles)

ALTER TABLE asignaturas
    ADD COLUMN IF NOT EXISTS nivel VARCHAR(20) DEFAULT 'TODOS';

UPDATE asignaturas SET nivel = 'TODOS' WHERE nivel IS NULL;

ALTER TABLE asignaturas
    DROP CONSTRAINT IF EXISTS chk_asignatura_nivel;

ALTER TABLE asignaturas
    ADD CONSTRAINT chk_asignatura_nivel
    CHECK (nivel IN ('PREESCOLAR','PRIMARIA','SECUNDARIA','MEDIA','TODOS'));
