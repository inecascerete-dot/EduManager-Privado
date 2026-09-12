-- Migración: Tabla de Direcciones de Grupo
-- Descripción: Registra qué docente es director de cada curso por año lectivo.
-- Un curso solo puede tener un director por año. Un docente solo puede dirigir
-- un grupo por año. Ambas restricciones se garantizan con constraints UNIQUE en BD.

-- Secuencia para generar IDs automáticos (DG-1, DG-2, ...)
CREATE SEQUENCE IF NOT EXISTS seq_id_direccion_grupo
    START WITH 1
    INCREMENT BY 1
    NO CYCLE;

-- Tabla principal
CREATE TABLE IF NOT EXISTS direcciones_grupo (
    id_direccion_grupo  TEXT     PRIMARY KEY,
    id_curso            TEXT     NOT NULL REFERENCES cursos(id_curso),
    id_personal         TEXT     NOT NULL REFERENCES personal(id_personal),
    ano_lectivo         INTEGER  NOT NULL,

    -- Un curso solo puede tener un director por año lectivo
    CONSTRAINT uq_curso_ano    UNIQUE (id_curso, ano_lectivo),

    -- Un docente solo puede ser director de un grupo por año lectivo
    CONSTRAINT uq_personal_ano UNIQUE (id_personal, ano_lectivo)
);

-- Índices para acelerar consultas frecuentes por año o por docente
CREATE INDEX IF NOT EXISTS idx_dg_ano_lectivo ON direcciones_grupo (ano_lectivo);
CREATE INDEX IF NOT EXISTS idx_dg_personal    ON direcciones_grupo (id_personal);
