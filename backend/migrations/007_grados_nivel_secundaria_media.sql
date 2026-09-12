-- Migración 007: Desglosa BACHILLERATO en SECUNDARIA (6-9) y MEDIA (10-11)
-- Fecha: 2026-07
--
-- IMPORTANTE: los UPDATE deben ejecutarse ANTES de añadir el nuevo CHECK
-- para evitar que falle la validación sobre filas con nivel='BACHILLERATO'.

-- 1. Eliminar la restricción CHECK existente (permite BACHILLERATO)
ALTER TABLE grados DROP CONSTRAINT IF EXISTS grados_nivel_check;

-- 2. Reclasificar los grados de bachillerato ANTES de añadir el nuevo check
--    GRA-06 a GRA-09 → Básica Secundaria
UPDATE grados
SET nivel = 'SECUNDARIA'
WHERE nivel = 'BACHILLERATO'
  AND id_grado ~ '^GRA-0[6-9]$';

--    GRA-10 y GRA-11 → Media
UPDATE grados
SET nivel = 'MEDIA'
WHERE nivel = 'BACHILLERATO'
  AND id_grado IN ('GRA-10', 'GRA-11');

--    Cualquier otro BACHILLERATO remanente → Básica Secundaria (fallback seguro)
UPDATE grados
SET nivel = 'SECUNDARIA'
WHERE nivel = 'BACHILLERATO';

-- 3. Añadir el nuevo CHECK (ya no hay filas con BACHILLERATO)
ALTER TABLE grados
    ADD CONSTRAINT grados_nivel_check
    CHECK (nivel IN ('PREESCOLAR', 'PRIMARIA', 'SECUNDARIA', 'MEDIA'));
