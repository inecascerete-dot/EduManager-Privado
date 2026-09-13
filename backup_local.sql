--
-- PostgreSQL database dump
--

\restrict N7Csz7tLHqQynggNLE4aPbVcvwnpXPO1VVusXSWxbnkNqHnfzzkVN4zui3pCZ9F

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: generar_folio_matricula(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generar_folio_matricula(ano integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
    DECLARE
      consecutivo INTEGER;
      folio TEXT;
    BEGIN
      SELECT COALESCE(MAX(CAST(SPLIT_PART(folio_matricula, '-', 3) AS INTEGER)), 0) + 1
        INTO consecutivo
        FROM matriculas
        WHERE ano_lectivo = ano;
      folio := 'MAT-' || ano || '-' || LPAD(consecutivo::TEXT, 4, '0');
      RETURN folio;
    END;
    $$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: acudientes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.acudientes (
    id_acudiente character varying(20) NOT NULL,
    id_tipo_documento integer,
    numero_documento character varying(20) NOT NULL,
    primer_nombre character varying(50) NOT NULL,
    segundo_nombre character varying(50),
    primer_apellido character varying(50) NOT NULL,
    segundo_apellido character varying(50),
    fecha_nacimiento date,
    id_departamento_nacimiento integer,
    id_municipio_nacimiento integer,
    telefono_principal character varying(20),
    correo_electronico character varying(150),
    ocupacion character varying(100),
    id_sector integer,
    direccion_residencia character varying(200),
    observaciones text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: asignacion_docente; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.asignacion_docente (
    id_asignacion text NOT NULL,
    id_curso text NOT NULL,
    id_personal text NOT NULL,
    id_asignatura text NOT NULL,
    ano_lectivo integer NOT NULL
);


--
-- Name: asignaturas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.asignaturas (
    id_asignatura text NOT NULL,
    nombre text NOT NULL,
    area_conocimiento text NOT NULL,
    descripcion text,
    nivel character varying(20) DEFAULT 'TODOS'::character varying,
    CONSTRAINT chk_asignatura_nivel CHECK (((nivel)::text = ANY (ARRAY[('PREESCOLAR'::character varying)::text, ('PRIMARIA'::character varying)::text, ('SECUNDARIA'::character varying)::text, ('MEDIA'::character varying)::text, ('TODOS'::character varying)::text])))
);


--
-- Name: boletin_datos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.boletin_datos (
    id_matricula integer NOT NULL,
    numero_periodo smallint NOT NULL,
    inasistencias smallint DEFAULT 0 NOT NULL,
    observaciones text DEFAULT ''::text NOT NULL,
    CONSTRAINT boletin_datos_inasistencias_check CHECK ((inasistencias >= 0)),
    CONSTRAINT boletin_datos_numero_periodo_check CHECK (((numero_periodo >= 1) AND (numero_periodo <= 4)))
);


--
-- Name: TABLE boletin_datos; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.boletin_datos IS 'Inasistencias y observaciones del período para cada matrícula.';


--
-- Name: calificaciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.calificaciones (
    id_calificacion character varying(20) NOT NULL,
    id_matricula integer NOT NULL,
    id_asignatura character varying(20) NOT NULL,
    numero_periodo smallint NOT NULL,
    ano_lectivo integer NOT NULL,
    valor numeric(4,2) NOT NULL,
    observacion text,
    fecha_registro timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT calificaciones_numero_periodo_check CHECK (((numero_periodo >= 1) AND (numero_periodo <= 4))),
    CONSTRAINT calificaciones_valor_check CHECK (((valor >= (0)::numeric) AND (valor <= (10)::numeric)))
);


--
-- Name: TABLE calificaciones; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.calificaciones IS 'Una nota por estudiante × asignatura × período académico.';


--
-- Name: cursos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cursos (
    id_curso text NOT NULL,
    id_grado text,
    grupo text NOT NULL,
    id_sede text,
    id_jornada text
);


--
-- Name: departamentos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.departamentos (
    id_departamento integer NOT NULL,
    codigo_dane character varying(2) NOT NULL,
    nombre character varying(100) NOT NULL
);


--
-- Name: departamentos_id_departamento_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.departamentos_id_departamento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: departamentos_id_departamento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.departamentos_id_departamento_seq OWNED BY public.departamentos.id_departamento;


--
-- Name: direcciones_grupo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.direcciones_grupo (
    id_direccion_grupo text NOT NULL,
    id_curso text NOT NULL,
    id_personal text NOT NULL,
    ano_lectivo integer NOT NULL
);


--
-- Name: documentos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.documentos (
    id integer NOT NULL,
    estudiante_id text NOT NULL,
    tipo_documento character varying(100) NOT NULL,
    nombre_archivo character varying(255) NOT NULL,
    drive_id character varying(255),
    drive_url text,
    carpeta_drive character varying(255),
    fecha_subida timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    usuario character varying(100),
    observaciones text
);


--
-- Name: documentos_acudientes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.documentos_acudientes (
    id integer NOT NULL,
    id_acudiente text NOT NULL,
    tipo_documento text,
    nombre_archivo text,
    drive_file_id text,
    url text,
    id_carpeta text,
    fecha_subida timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    subido_por text DEFAULT 'Sistema'::text
);


--
-- Name: documentos_acudientes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.documentos_acudientes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: documentos_acudientes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.documentos_acudientes_id_seq OWNED BY public.documentos_acudientes.id;


--
-- Name: documentos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.documentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: documentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.documentos_id_seq OWNED BY public.documentos.id;


--
-- Name: escala_valoracion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.escala_valoracion (
    id_nivel character varying(20) NOT NULL,
    nombre character varying(40) NOT NULL,
    valor_min numeric(4,2) NOT NULL,
    valor_max numeric(4,2) NOT NULL,
    descripcion text,
    orden smallint DEFAULT 1 NOT NULL,
    CONSTRAINT chk_ev_rango CHECK ((valor_min < valor_max))
);


--
-- Name: TABLE escala_valoracion; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.escala_valoracion IS 'Rangos numéricos → niveles de desempeño (Bajo/Básico/Alto/Superior).';


--
-- Name: estudiantes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estudiantes (
    id_estudiante text NOT NULL,
    tipo_documento text,
    numero_documento text,
    lugar_expedicion text,
    fecha_nacimiento date,
    genero text,
    grupo_sanguineo_rh text,
    eps text,
    sisben_grupo text,
    caracterizacion_poblacional text,
    direccion_residencia text,
    barrio_vereda text,
    estrato text,
    telefono_contacto text,
    primer_apellido text NOT NULL,
    segundo_apellido text,
    primer_nombre text NOT NULL,
    segundo_nombre text,
    foto_url text,
    id_municipio integer,
    id_sector integer
);


--
-- Name: COLUMN estudiantes.foto_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.estudiantes.foto_url IS 'Nombre del archivo de foto almacenado en assets/, ej: EST-205_foto.jpg';


--
-- Name: estudiantes_documentos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estudiantes_documentos (
    id_documento integer NOT NULL,
    id_estudiante character varying(20) NOT NULL,
    tipo_documento character varying(100) NOT NULL,
    nombre_archivo character varying(255) NOT NULL,
    ruta_archivo character varying(500) NOT NULL,
    fecha_subida timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    observaciones text
);


--
-- Name: estudiantes_documentos_id_documento_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estudiantes_documentos_id_documento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estudiantes_documentos_id_documento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estudiantes_documentos_id_documento_seq OWNED BY public.estudiantes_documentos.id_documento;


--
-- Name: grados; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grados (
    id_grado text NOT NULL,
    nombre_grado text NOT NULL,
    nivel character varying(20) DEFAULT 'PRIMARIA'::character varying NOT NULL,
    orden smallint DEFAULT 99 NOT NULL,
    CONSTRAINT grados_nivel_check CHECK (((nivel)::text = ANY (ARRAY[('PREESCOLAR'::character varying)::text, ('PRIMARIA'::character varying)::text, ('SECUNDARIA'::character varying)::text, ('MEDIA'::character varying)::text])))
);


--
-- Name: COLUMN grados.orden; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.grados.orden IS 'Orden de aparición en selectores (menor primero).';


--
-- Name: indicadores_desempeno; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.indicadores_desempeno (
    id_indicador character varying(20) NOT NULL,
    ano_lectivo integer NOT NULL,
    id_grado character varying(20) NOT NULL,
    id_asignatura character varying(20) NOT NULL,
    numero_periodo smallint NOT NULL,
    descripcion text NOT NULL,
    tipo character varying(40) DEFAULT 'Cognitivo'::character varying NOT NULL,
    CONSTRAINT indicadores_desempeno_numero_periodo_check CHECK (((numero_periodo >= 1) AND (numero_periodo <= 4))),
    CONSTRAINT indicadores_desempeno_tipo_check CHECK (((tipo)::text = ANY (ARRAY[('Cognitivo'::character varying)::text, ('Procedimental'::character varying)::text, ('Actitudinal'::character varying)::text])))
);


--
-- Name: TABLE indicadores_desempeno; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.indicadores_desempeno IS 'Indicadores / aprendizajes esperados por grado, asignatura y período.';


--
-- Name: instituciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.instituciones (
    id_institucion text NOT NULL,
    nit_dane text,
    nombre_institucion text NOT NULL,
    resolucion_aprobacion text,
    mision text,
    vision text,
    logo_url text,
    direccion_principal text,
    telefono_principal text,
    email_institucional text,
    nombre_rector text,
    correo_rector text,
    himno_url text,
    eslogan text DEFAULT ''::text NOT NULL,
    escudo_url text DEFAULT ''::text NOT NULL,
    id_departamento integer,
    id_municipio integer
);


--
-- Name: COLUMN instituciones.eslogan; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.instituciones.eslogan IS 'Lema o eslogan institucional, aparece en boletines y encabezados.';


--
-- Name: COLUMN instituciones.escudo_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.instituciones.escudo_url IS 'Nombre del archivo del escudo/imagen secundaria en assets/.';


--
-- Name: jornadas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jornadas (
    id_jornada text NOT NULL,
    id_institucion text,
    nombre_jornada text NOT NULL
);


--
-- Name: matriculas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.matriculas (
    id_matricula integer NOT NULL,
    id_estudiante text,
    id_acudiente text,
    folio_matricula text,
    ano_lectivo integer,
    fecha_matricula date DEFAULT CURRENT_DATE,
    parentesco text,
    sede text,
    jornada text,
    estado text DEFAULT 'Matriculado'::text,
    id_curso text,
    id_institucion text,
    observaciones text
);


--
-- Name: matriculas_id_matricula_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.matriculas_id_matricula_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: matriculas_id_matricula_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.matriculas_id_matricula_seq OWNED BY public.matriculas.id_matricula;


--
-- Name: municipios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.municipios (
    id_municipio integer NOT NULL,
    codigo_dane character varying(5) NOT NULL,
    nombre character varying(150) NOT NULL,
    id_departamento integer NOT NULL
);


--
-- Name: municipios_id_municipio_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.municipios_id_municipio_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: municipios_id_municipio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.municipios_id_municipio_seq OWNED BY public.municipios.id_municipio;


--
-- Name: periodos_academicos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.periodos_academicos (
    id_periodo character varying(20) NOT NULL,
    ano_lectivo integer NOT NULL,
    numero smallint NOT NULL,
    nombre character varying(80) NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    porcentaje numeric(5,2) DEFAULT 25.00 NOT NULL,
    CONSTRAINT chk_fechas_periodo CHECK (((fecha_inicio IS NULL) OR (fecha_fin IS NULL) OR (fecha_inicio <= fecha_fin))),
    CONSTRAINT periodos_academicos_numero_check CHECK (((numero >= 1) AND (numero <= 4))),
    CONSTRAINT periodos_academicos_porcentaje_check CHECK (((porcentaje > (0)::numeric) AND (porcentaje <= (100)::numeric)))
);


--
-- Name: TABLE periodos_academicos; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.periodos_academicos IS 'Períodos académicos por año lectivo con peso porcentual.';


--
-- Name: personal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personal (
    id_personal text NOT NULL,
    numero_documento text NOT NULL,
    nombres text NOT NULL,
    apellidos text NOT NULL,
    telefono text,
    correo_electronico text,
    cargo text,
    escalafon_grado text,
    decreto_nombramiento text,
    tipo_vinculacion text,
    foto_url text,
    estado_laboral text,
    fecha_estado_laboral date
);


--
-- Name: plan_estudio; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.plan_estudio (
    id_plan text NOT NULL,
    id_grado text NOT NULL,
    id_asignatura text NOT NULL,
    horas_semana integer DEFAULT 1 NOT NULL
);


--
-- Name: sectores; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sectores (
    id_sector integer NOT NULL,
    id_municipio integer NOT NULL,
    nombre_sector character varying(120) NOT NULL,
    tipo character varying(30) NOT NULL,
    activo boolean DEFAULT true,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    observacion text,
    CONSTRAINT sectores_tipo_sector_check CHECK (((tipo)::text = ANY ((ARRAY['Barrio'::character varying, 'Vereda'::character varying, 'Corregimiento'::character varying, 'Caserío'::character varying, 'Centro poblado'::character varying, 'Urbanización'::character varying, 'Condominio'::character varying, 'Sector'::character varying, 'Otro'::character varying])::text[])))
);


--
-- Name: sectores_id_sector_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sectores_id_sector_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sectores_id_sector_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sectores_id_sector_seq OWNED BY public.sectores.id_sector;


--
-- Name: sedes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sedes (
    id_sede text NOT NULL,
    id_institucion text,
    nombre_sede text NOT NULL,
    direccion text,
    telefono_sede text
);


--
-- Name: seq_id_asignacion_docente; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_asignacion_docente
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seq_id_asignatura; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_asignatura
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seq_id_calificacion; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_calificacion
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seq_id_direccion_grupo; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_direccion_grupo
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seq_id_estudiante; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_estudiante
    START WITH 205
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seq_id_indicador; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_indicador
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seq_id_periodo; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_periodo
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seq_id_plan_estudio; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_plan_estudio
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seq_id_sede; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seq_id_sede
    START WITH 2
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipos_documento; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipos_documento (
    id_tipo_documento integer NOT NULL,
    codigo character varying(10) NOT NULL,
    descripcion character varying(80) NOT NULL,
    activo boolean DEFAULT true
);


--
-- Name: tipos_documento_id_tipo_documento_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tipos_documento_id_tipo_documento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipos_documento_id_tipo_documento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tipos_documento_id_tipo_documento_seq OWNED BY public.tipos_documento.id_tipo_documento;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id_usuario integer NOT NULL,
    usuario character varying(50) NOT NULL,
    password_hash text NOT NULL,
    rol character varying(30) NOT NULL,
    estado character varying(15) DEFAULT 'ACTIVO'::character varying NOT NULL,
    id_docente integer,
    id_estudiante integer,
    id_acudiente integer,
    ultimo_acceso timestamp without time zone,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_id_usuario_seq OWNED BY public.usuarios.id_usuario;


--
-- Name: departamentos id_departamento; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departamentos ALTER COLUMN id_departamento SET DEFAULT nextval('public.departamentos_id_departamento_seq'::regclass);


--
-- Name: documentos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documentos ALTER COLUMN id SET DEFAULT nextval('public.documentos_id_seq'::regclass);


--
-- Name: documentos_acudientes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documentos_acudientes ALTER COLUMN id SET DEFAULT nextval('public.documentos_acudientes_id_seq'::regclass);


--
-- Name: estudiantes_documentos id_documento; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estudiantes_documentos ALTER COLUMN id_documento SET DEFAULT nextval('public.estudiantes_documentos_id_documento_seq'::regclass);


--
-- Name: matriculas id_matricula; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.matriculas ALTER COLUMN id_matricula SET DEFAULT nextval('public.matriculas_id_matricula_seq'::regclass);


--
-- Name: municipios id_municipio; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios ALTER COLUMN id_municipio SET DEFAULT nextval('public.municipios_id_municipio_seq'::regclass);


--
-- Name: sectores id_sector; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sectores ALTER COLUMN id_sector SET DEFAULT nextval('public.sectores_id_sector_seq'::regclass);


--
-- Name: tipos_documento id_tipo_documento; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_documento ALTER COLUMN id_tipo_documento SET DEFAULT nextval('public.tipos_documento_id_tipo_documento_seq'::regclass);


--
-- Name: usuarios id_usuario; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuarios_id_usuario_seq'::regclass);


--
-- Data for Name: acudientes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.acudientes (id_acudiente, id_tipo_documento, numero_documento, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nacimiento, id_departamento_nacimiento, id_municipio_nacimiento, telefono_principal, correo_electronico, ocupacion, id_sector, direccion_residencia, observaciones, fecha_registro) FROM stdin;
ACU-001	7	1067968457	MAROLY	PAOLA	DIAZ	CADAVID	1999-11-16	10	433	3152835846	piojito@gmail.com	ingeniera ambiental	2	CALLE 32A #36A-40	Madre soltera con poco tiempo para atender situaciones del acudido por el trabajo	2026-08-04 10:59:27.934096
ACU-002	3	78712335	DELIO	ANTONIO	DIAZ	MEJIA	1992-03-14	10	429	3105274086	inecascerete@gmail.com	INGENIERO	2	CALLE 32		2026-08-27 19:52:21.044271
ACU-003	3	15418148	FBDFBGFDBGFB	GBGFBGFBGFB	GBFGBGFBGF	GBGFBGFBG	1988-08-18	10	433	3152385846	inecascerete@gmail.com	fomag	2	CALLE 32		2026-08-27 20:09:20.56058
\.


--
-- Data for Name: asignacion_docente; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asignacion_docente (id_asignacion, id_curso, id_personal, id_asignatura, ano_lectivo) FROM stdin;
\.


--
-- Data for Name: asignaturas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asignaturas (id_asignatura, nombre, area_conocimiento, descripcion, nivel) FROM stdin;
ASG-002	Español	Lenguaje y Literatura	\N	TODOS
ASG-003	Ciencias Naturales	Ciencias Naturales	\N	TODOS
\.


--
-- Data for Name: boletin_datos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.boletin_datos (id_matricula, numero_periodo, inasistencias, observaciones) FROM stdin;
\.


--
-- Data for Name: calificaciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.calificaciones (id_calificacion, id_matricula, id_asignatura, numero_periodo, ano_lectivo, valor, observacion, fecha_registro) FROM stdin;
\.


--
-- Data for Name: cursos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cursos (id_curso, id_grado, grupo, id_sede, id_jornada) FROM stdin;
CUR-1201-M	GRA-12	01	SED-PRINCIPAL	JOR-MANANA
CUR-101-T	GRA-01	01	SED-PRINCIPAL	JOR-TARDE
CUR-201-T	GRA-02	01	SED-PRINCIPAL	JOR-TARDE
CUR-301-T	GRA-03	01	SED-PRINCIPAL	JOR-TARDE
CUR-302-T	GRA-03	02	SED-PRINCIPAL	JOR-TARDE
CUR-401-T	GRA-04	01	SED-PRINCIPAL	JOR-TARDE
CUR-402-T	GRA-04	02	SED-PRINCIPAL	JOR-TARDE
CUR-502-T	GRA-05	02	SED-PRINCIPAL	JOR-TARDE
CUR-501-T	GRA-05	01	SED-PRINCIPAL	JOR-TARDE
\.


--
-- Data for Name: departamentos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.departamentos (id_departamento, codigo_dane, nombre) FROM stdin;
1	05	ANTIOQUIA
2	08	ATLÁNTICO
3	11	BOGOTÁ, D.C.
4	13	BOLÍVAR
5	15	BOYACÁ
6	17	CALDAS
7	18	CAQUETÁ
8	19	CAUCA
9	20	CESAR
10	23	CÓRDOBA
11	25	CUNDINAMARCA
12	27	CHOCÓ
13	41	HUILA
14	44	LA GUAJIRA
15	47	MAGDALENA
16	50	META
17	52	NARIÑO
18	54	NORTE DE SANTANDER
19	63	QUINDÍO
20	66	RISARALDA
21	68	SANTANDER
22	70	SUCRE
23	73	TOLIMA
24	76	VALLE DEL CAUCA
25	81	ARAUCA
26	85	CASANARE
27	86	PUTUMAYO
28	88	ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA
29	91	AMAZONAS
30	94	GUAINÍA
31	95	GUAVIARE
32	97	VAUPÉS
33	99	VICHADA
\.


--
-- Data for Name: direcciones_grupo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.direcciones_grupo (id_direccion_grupo, id_curso, id_personal, ano_lectivo) FROM stdin;
\.


--
-- Data for Name: documentos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.documentos (id, estudiante_id, tipo_documento, nombre_archivo, drive_id, drive_url, carpeta_drive, fecha_subida, usuario, observaciones) FROM stdin;
1	EST-214	Tarjeta de Identidad	Certificado2025_Tuya.pdf	17ui8aJk_HlK1JeOyk8YNZDwR0iQGfLbF	https://drive.google.com/file/d/17ui8aJk_HlK1JeOyk8YNZDwR0iQGfLbF/view?usp=drivesdk	1vsoRqE3KBE0rIvNiw7U9chusvBXrYnac	2026-07-30 14:26:28.128122	Sistema	
2	EST-214	Otro	simat hoy.pdf	1YcygtBSuF3ynxtOyE6qNMQgRLFWBCwvc	https://drive.google.com/file/d/1YcygtBSuF3ynxtOyE6qNMQgRLFWBCwvc/view?usp=drivesdk	1vsoRqE3KBE0rIvNiw7U9chusvBXrYnac	2026-07-30 14:45:08.875434	Sistema	
3	EST-214	Foto	ESCUDO.jpg	1fvJ2olb8BNoLY8KdcBCxTMbAUeYJ5xpO	https://drive.google.com/file/d/1fvJ2olb8BNoLY8KdcBCxTMbAUeYJ5xpO/view?usp=drivesdk	1vsoRqE3KBE0rIvNiw7U9chusvBXrYnac	2026-07-31 16:05:51.011788	Sistema	
4	EST-218	Registro Civil	Certificado Electoral.pdf	1d71CxVc9VpZZlHMVycDr2SO3tw7XlZPY	https://drive.google.com/file/d/1d71CxVc9VpZZlHMVycDr2SO3tw7XlZPY/view?usp=drivesdk	1RLm_6JvGssXYyNOBhf_VvO4jkvCrjU1p	2026-08-13 14:25:36.993228	Sistema	
5	EST-220	Registro Civil	pago certificado 78712335.pdf	1ziIhGDAYlqDBGth15MnyKKyTBlZHhFBJ	https://drive.google.com/file/d/1ziIhGDAYlqDBGth15MnyKKyTBlZHhFBJ/view?usp=drivesdk	1YD8mLnPVugmY5vrpVhrkGir10GGHgkJX	2026-08-27 09:31:43.604741	Sistema	
6	EST-220	Observador	FORMATO COMIION x.pdf	1GeGSUZgJyafnjobg1CBNfv-aP0eM9yBO	https://drive.google.com/file/d/1GeGSUZgJyafnjobg1CBNfv-aP0eM9yBO/view?usp=drivesdk	1YD8mLnPVugmY5vrpVhrkGir10GGHgkJX	2026-08-27 09:32:06.113585	Sistema	
7	EST-00223	EPS	Listado_Notificacion_Pendientes_0403.pdf	1BUzBJMLgRvPoDXXw9YHq1WKQs0onnsxh	https://drive.google.com/file/d/1BUzBJMLgRvPoDXXw9YHq1WKQs0onnsxh/view?usp=drivesdk	1i2dsifZFNStMtar7BIuq_NdpqEK2CkAl	2026-09-01 10:47:13.911058	Sistema	
\.


--
-- Data for Name: documentos_acudientes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.documentos_acudientes (id, id_acudiente, tipo_documento, nombre_archivo, drive_file_id, url, id_carpeta, fecha_subida, subido_por) FROM stdin;
1	ACU-001	Cedula	registro_extendido (2).pdf	1DY1Kis9HTIZ9d6OkYC4HBpof2RTGkSvz	https://drive.google.com/file/d/1DY1Kis9HTIZ9d6OkYC4HBpof2RTGkSvz/view?usp=drivesdk	1QITzAFIdEvP1wHRX92YRimYF_EMleADj	2026-08-27 17:42:44.04381	Sistema
2	ACU-001	Registro	78712335_56.pdf	1ELB7OBZDa3WAcqgi0Cqcw4z7xcwkIHwc	https://drive.google.com/file/d/1ELB7OBZDa3WAcqgi0Cqcw4z7xcwkIHwc/view?usp=drivesdk	1QITzAFIdEvP1wHRX92YRimYF_EMleADj	2026-08-27 17:48:21.758643	Sistema
3	ACU-003	CEDULA	Boletin 0°.pdf	1kNBu5L9EeybvSaKRUWLTidPCjjH699HD	https://drive.google.com/file/d/1kNBu5L9EeybvSaKRUWLTidPCjjH699HD/view?usp=drivesdk	1ntUyb8fLrY4Rm-vQfAxkAzBoT0TV3-u9	2026-08-27 20:10:41.040965	Sistema
4	ACU-002	Cedula	78712335_55.pdf	13SUIpD3v1jx-GXo9fbkdqbgl6x_Dc98u	https://drive.google.com/file/d/13SUIpD3v1jx-GXo9fbkdqbgl6x_Dc98u/view?usp=drivesdk	15EgEIG76iLC7rZD59YBsjVGSFDhR8m1f	2026-09-01 12:46:02.509682	Sistema
\.


--
-- Data for Name: escala_valoracion; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.escala_valoracion (id_nivel, nombre, valor_min, valor_max, descripcion, orden) FROM stdin;
BAJO	Desempeño Bajo	0.00	2.99	No alcanza los mínimos.	1
BASICO	Desempeño Básico	3.00	3.99	Supera los mínimos.	2
ALTO	Desempeño Alto	4.00	4.49	Supera satisfactoriamente.	3
SUPERIOR	Desempeño Superior	4.50	5.00	Supera ampliamente.	4
\.


--
-- Data for Name: estudiantes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estudiantes (id_estudiante, tipo_documento, numero_documento, lugar_expedicion, fecha_nacimiento, genero, grupo_sanguineo_rh, eps, sisben_grupo, caracterizacion_poblacional, direccion_residencia, barrio_vereda, estrato, telefono_contacto, primer_apellido, segundo_apellido, primer_nombre, segundo_nombre, foto_url, id_municipio, id_sector) FROM stdin;
EST-204	TI	1651616196	MONTERIA	2015-01-01	Masculino	O+	FOMAG	A2	Víctima del conflicto	CDJCVJDBVBD	LOS CAÑOS	1	261616169	TORRES	PAEZ	JUAN	ANTONIO	\N	\N	\N
EST-00227	CC	3152835846	Montería	2000-08-18	Masculino	O+			Ninguna	CALLE 32A #36A-40	SANTA MARIA	3	312565822365	PEREZ	PITALUA	JUAN	JOSE	EST-00227_foto.jpeg	433	6
EST-219	TI	025727832758	vdsvdsvsdv	2015-01-01	Masculino	O+	sdvvsdvsdv	A1	Palenquero	dvsdvsdvsd  dsv c  d	vdsvdsvds	2	1282587327537	DSVDSVSDV	DSVDSVDSV	DVSDVDFSV SDF	DVDSVDSVSDV	https://drive.google.com/uc?id=1kxu7uVwbPgeDqJWR38ejBsy0sXkpdoAx&export=download	\N	\N
EST-00228	CC	3152835846	Montería	2026-08-30	Masculino	O+	FOMAG	A21	Ninguna	CALLE 32A #36A-40	SANTA MARIA	3	312565822365	PEREZ	PITALUA	JUAN	JOSE	EST-00228_foto.jpeg	433	6
EST-00229	TI	525.05	Montería	2026-08-30	Masculino	O+	fomag	A21	Discapacidad	GFHGFHGFHGFH	LAS PALMAS	1	25432543	CALLE 32A #36A-40	INECAS-CERETE	545KH,KHJ,	,KJ,KJ,KJ,KJ	\N	433	2
EST-218	CC	78712335	Montería	2005-01-31	Masculino	A+	fomag	A1	Ninguna	Oscar Valentin Lopez Doria	zenumbio@hotmail.com	4	312565822365	DIAZ	MEJIA	DELIO	ANTONIO	https://drive.google.com/uc?id=1J6otNDV_7gdfMvidgSGazVAoS9NQWuZx&export=view	576	5
EST-214	TI	1067968457	monteria	2005-01-04	Femenino	O-	salu total	D21	Indígena	Calle 32A#36A-40	Limonar	1	3152385846	DIAZ	CADAVID	MAROLY	PAOLA	https://drive.google.com/uc?id=1It05V26COkmxodS0UyNyNk8Mw_-lxEOr&export=download	433	3
EST-221	CC	1062961690	MONTERIA	2006-05-26	Masculino	A+	FOMAG	C12	Palenquero	CALLE 32A #36A-40	EL LIMONAR	4	3175184618	DIAZ	CADAVID	LUIS	DANIEL	https://drive.google.com/uc?id=13Ztnd2HcvKFs1jvTyjW_a7elQ37BO5Qy&export=view	433	10
EST-220	TI	45252353	svfdvfdv	2015-01-01	Masculino	O+	SALUD TOTAL	A2	Palenquero	dfdsfsdf	dsfdfdsf	4	353563543453	DFGSDFDSF	DFDSFDSF	DGFDGDSG	DFDSFDSFDS	https://drive.google.com/uc?id=1B2HE_Izk9mODqwuese0ZRR7tQFcA4fRa&export=view	433	2
EST-00223	TI	78697301	Montería	2015-01-01	Masculino	O+	FOMAG	A21	Víctima del conflicto	CALLE 32A #36A-40	\N	\N	\N	DIAZ	MEJIA	ERIBERTO	TERCERO	EST-00223_foto.png	433	4
EST-222	TI	25432543	hthtrh	2015-01-01	Masculino	O+	ghrthrthrth	A1	Ninguna	hthtrhrt	hrthrthtrh	1	15818518918	thtrhtrh	htrhtrh	ththtrh	trhtrhtr	EST-222_foto.png	\N	\N
EST-00224	TI	78697301	Montería	2015-01-01	Masculino	O+	FOMAG	D20	Palenquero	CALLE 32A #36A-40	\N	\N	\N	CORDOBA	MONTERIA	CADAVID	CERETE	\N	433	7
EST-00225	CC	34979000	Montería	2015-01-05	Femenino	O+	FOMAG	D20	Indígena	CALLE 32A #36A-40		4	3023810763	DIAZ	MEJIA	BEATRIZ	LEONOR	EST-00225_foto.jpeg	433	7
EST-00226	CC	2532533	Montería	2026-08-30	Masculino	O+	DGFDSGD	D16	Rom	DVFDSVFDSVDF		1	257237525725	GFHFGHGFHFGH	GFHGFHGFHGFH	GFHGFHGFHGF	GHGFHGFHGF	EST-00226_foto.jpeg	433	2
\.


--
-- Data for Name: estudiantes_documentos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estudiantes_documentos (id_documento, id_estudiante, tipo_documento, nombre_archivo, ruta_archivo, fecha_subida, observaciones) FROM stdin;
\.


--
-- Data for Name: grados; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grados (id_grado, nombre_grado, nivel, orden) FROM stdin;
GRA-01	Primero	PRIMARIA	1
GRA-02	Segundo	PRIMARIA	2
GRA-03	Tercero	PRIMARIA	3
GRA-04	Cuarto	PRIMARIA	4
GRA-05	Quinto	PRIMARIA	5
GRA-PR	Transición	PREESCOLAR	4
GRA-12	Maternal	PREESCOLAR	1
GRA-06	Sexto	SECUNDARIA	6
GRA-07	Séptimo	SECUNDARIA	7
GRA-08	Octavo	SECUNDARIA	8
GRA-09	Noveno	SECUNDARIA	9
GRA-10	Décimo	MEDIA	10
GRA-11	Once	MEDIA	11
GRA-14	Jardin	PREESCOLAR	3
GRA-13	Prejardin	PREESCOLAR	2
\.


--
-- Data for Name: indicadores_desempeno; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.indicadores_desempeno (id_indicador, ano_lectivo, id_grado, id_asignatura, numero_periodo, descripcion, tipo) FROM stdin;
\.


--
-- Data for Name: instituciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.instituciones (id_institucion, nit_dane, nombre_institucion, resolucion_aprobacion, mision, vision, logo_url, direccion_principal, telefono_principal, email_institucional, nombre_rector, correo_rector, himno_url, eslogan, escudo_url, id_departamento, id_municipio) FROM stdin;
INST-DICA	12316200013	Institución educativa Cañito de los Sábalos	0007016 19 Dic de 2001	La Institución Educativa Cañito de los Sábalos, propende por la formación integral del estudiante, como una persona   sensible, solidaria, preservadora y constructora del conocimiento, con elementos necesarios para la convivencia pacífica, armónica con el ambiente y la sociedad, en pro del desarrollo sostenible mejorando su calidad de vida y la de la comunidad.	La Institución Educativa Cañito de los Sábalos se proyecta, al 2028, como una institución con infraestructura educativa apropiada, aplicando procesos administrativos de calidad y un modelo educativo Inter estructurante, líder en educación   con proyectos de transformación social del entorno inmediato y promocionando bachilleres con buen nivel de competencias cognitivas, valorativas, praxicas y humana	logo_INST-DICA.png	Dirección:  Calle 6A   Cra. 13 B – 13 	3126639930	ee_13216200013101@hotmail.com	Oscar Valentin Lopez Doria	zenumbio@hotmail.com	\N	EDUCAMOS PARA LA VIDA	instituciones/INST-DICA/escudo.png	10	433
\.


--
-- Data for Name: jornadas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jornadas (id_jornada, id_institucion, nombre_jornada) FROM stdin;
JOR-MANANA	INST-DICA	Mañana
JOR-TARDE	INST-DICA	Tarde
JOR-UNICA	INST-DICA	Única
\.


--
-- Data for Name: matriculas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.matriculas (id_matricula, id_estudiante, id_acudiente, folio_matricula, ano_lectivo, fecha_matricula, parentesco, sede, jornada, estado, id_curso, id_institucion, observaciones) FROM stdin;
5	EST-220	ACU-001	MAT-2026-0001	2026	2026-08-27	Hermana	Cañito de los Sabalos	Tarde	Matriculado	CUR-502-T	INST-DICA	\N
6	EST-00223	ACU-003	MAT-2026-0002	2026	2026-09-01	Madre	Cañito de los Sabalos	Tarde	Matriculado	CUR-101-T	INST-DICA	
\.


--
-- Data for Name: municipios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.municipios (id_municipio, codigo_dane, nombre, id_departamento) FROM stdin;
1	05001	MEDELLÍN	1
2	05002	ABEJORRAL	1
3	05004	ABRIAQUÍ	1
4	05021	ALEJANDRÍA	1
5	05030	AMAGÁ	1
6	05031	AMALFI	1
7	05034	ANDES	1
8	05036	ANGELÓPOLIS	1
9	05038	ANGOSTURA	1
10	05040	ANORÍ	1
11	05042	SANTA FÉ DE ANTIOQUIA	1
12	05044	ANZÁ	1
13	05045	APARTADÓ	1
14	05051	ARBOLETES	1
15	05055	ARGELIA	1
16	05059	ARMENIA	1
17	05079	BARBOSA	1
18	05086	BELMIRA	1
19	05088	BELLO	1
20	05091	BETANIA	1
21	05093	BETULIA	1
22	05101	CIUDAD BOLÍVAR	1
23	05107	BRICEÑO	1
24	05113	BURITICÁ	1
25	05120	CÁCERES	1
26	05125	CAICEDO	1
27	05129	CALDAS	1
28	05134	CAMPAMENTO	1
29	05138	CAÑASGORDAS	1
30	05142	CARACOLÍ	1
31	05145	CARAMANTA	1
32	05147	CAREPA	1
33	05148	EL CARMEN DE VIBORAL	1
34	05150	CAROLINA	1
35	05154	CAUCASIA	1
36	05172	CHIGORODÓ	1
37	05190	CISNEROS	1
38	05197	COCORNÁ	1
39	05206	CONCEPCIÓN	1
40	05209	CONCORDIA	1
41	05212	COPACABANA	1
42	05234	DABEIBA	1
43	05237	DONMATÍAS	1
44	05240	EBÉJICO	1
45	05250	EL BAGRE	1
46	05264	ENTRERRÍOS	1
47	05266	ENVIGADO	1
48	05282	FREDONIA	1
49	05284	FRONTINO	1
50	05306	GIRALDO	1
51	05308	GIRARDOTA	1
52	05310	GÓMEZ PLATA	1
53	05313	GRANADA	1
54	05315	GUADALUPE	1
55	05318	GUARNE	1
56	05321	GUATAPÉ	1
57	05347	HELICONIA	1
58	05353	HISPANIA	1
59	05360	ITAGÜÍ	1
60	05361	ITUANGO	1
61	05364	JARDÍN	1
62	05368	JERICÓ	1
63	05376	LA CEJA	1
64	05380	LA ESTRELLA	1
65	05390	LA PINTADA	1
66	05400	LA UNIÓN	1
67	05411	LIBORINA	1
68	05425	MACEO	1
69	05440	MARINILLA	1
70	05467	MONTEBELLO	1
71	05475	MURINDÓ	1
72	05480	MUTATÁ	1
73	05483	NARIÑO	1
74	05490	NECOCLÍ	1
75	05495	NECHÍ	1
76	05501	OLAYA	1
77	05541	PEÑOL	1
78	05543	PEQUE	1
79	05576	PUEBLORRICO	1
80	05579	PUERTO BERRÍO	1
81	05585	PUERTO NARE	1
82	05591	PUERTO TRIUNFO	1
83	05604	REMEDIOS	1
84	05607	RETIRO	1
85	05615	RIONEGRO	1
86	05628	SABANALARGA	1
87	05631	SABANETA	1
88	05642	SALGAR	1
89	05647	SAN ANDRÉS DE CUERQUÍA	1
90	05649	SAN CARLOS	1
91	05652	SAN FRANCISCO	1
92	05656	SAN JERÓNIMO	1
93	05658	SAN JOSÉ DE LA MONTAÑA	1
94	05659	SAN JUAN DE URABÁ	1
95	05660	SAN LUIS	1
96	05664	SAN PEDRO DE LOS MILAGROS	1
97	05665	SAN PEDRO DE URABÁ	1
98	05667	SAN RAFAEL	1
99	05670	SAN ROQUE	1
100	05674	SAN VICENTE FERRER	1
101	05679	SANTA BÁRBARA	1
102	05686	SANTA ROSA DE OSOS	1
103	05690	SANTO DOMINGO	1
104	05697	EL SANTUARIO	1
105	05736	SEGOVIA	1
106	05756	SONSÓN	1
107	05761	SOPETRÁN	1
108	05789	TÁMESIS	1
109	05790	TARAZÁ	1
110	05792	TARSO	1
111	05809	TITIRIBÍ	1
112	05819	TOLEDO	1
113	05837	TURBO	1
114	05842	URAMITA	1
115	05847	URRAO	1
116	05854	VALDIVIA	1
117	05856	VALPARAÍSO	1
118	05858	VEGACHÍ	1
119	05861	VENECIA	1
120	05873	VIGÍA DEL FUERTE	1
121	05885	YALÍ	1
122	05887	YARUMAL	1
123	05890	YOLOMBÓ	1
124	05893	YONDÓ	1
125	05895	ZARAGOZA	1
126	08001	BARRANQUILLA	2
127	08078	BARANOA	2
128	08137	CAMPO DE LA CRUZ	2
129	08141	CANDELARIA	2
130	08296	GALAPA	2
131	08372	JUAN DE ACOSTA	2
132	08421	LURUACO	2
133	08433	MALAMBO	2
134	08436	MANATÍ	2
135	08520	PALMAR DE VARELA	2
136	08549	PIOJÓ	2
137	08558	POLONUEVO	2
138	08560	PONEDERA	2
139	08573	PUERTO COLOMBIA	2
140	08606	REPELÓN	2
141	08634	SABANAGRANDE	2
142	08638	SABANALARGA	2
143	08675	SANTA LUCÍA	2
144	08685	SANTO TOMÁS	2
145	08758	SOLEDAD	2
146	08770	SUAN	2
147	08832	TUBARÁ	2
148	08849	USIACURÍ	2
149	11001	BOGOTÁ, D.C.	3
150	13001	CARTAGENA DE INDIAS	4
151	13006	ACHÍ	4
152	13030	ALTOS DEL ROSARIO	4
153	13042	ARENAL	4
154	13052	ARJONA	4
155	13062	ARROYOHONDO	4
156	13074	BARRANCO DE LOBA	4
157	13140	CALAMAR	4
158	13160	CANTAGALLO	4
159	13188	CICUCO	4
160	13212	CÓRDOBA	4
161	13222	CLEMENCIA	4
162	13244	EL CARMEN DE BOLÍVAR	4
163	13248	EL GUAMO	4
164	13268	EL PEÑÓN	4
165	13300	HATILLO DE LOBA	4
166	13430	MAGANGUÉ	4
167	13433	MAHATES	4
168	13440	MARGARITA	4
169	13442	MARÍA LA BAJA	4
170	13458	MONTECRISTO	4
171	13468	SANTA CRUZ DE MOMPOX	4
172	13473	MORALES	4
173	13490	NOROSÍ	4
174	13549	PINILLOS	4
175	13580	REGIDOR	4
176	13600	RÍO VIEJO	4
177	13620	SAN CRISTÓBAL	4
178	13647	SAN ESTANISLAO	4
179	13650	SAN FERNANDO	4
180	13654	SAN JACINTO	4
181	13655	SAN JACINTO DEL CAUCA	4
182	13657	SAN JUAN NEPOMUCENO	4
183	13667	SAN MARTÍN DE LOBA	4
184	13670	SAN PABLO	4
185	13673	SANTA CATALINA	4
186	13683	SANTA ROSA	4
187	13688	SANTA ROSA DEL SUR	4
188	13744	SIMITÍ	4
189	13760	SOPLAVIENTO	4
190	13780	TALAIGUA NUEVO	4
191	13810	TIQUISIO	4
192	13836	TURBACO	4
193	13838	TURBANÁ	4
194	13873	VILLANUEVA	4
195	13894	ZAMBRANO	4
196	15001	TUNJA	5
197	15022	ALMEIDA	5
198	15047	AQUITANIA	5
199	15051	ARCABUCO	5
200	15087	BELÉN	5
201	15090	BERBEO	5
202	15092	BETÉITIVA	5
203	15097	BOAVITA	5
204	15104	BOYACÁ	5
205	15106	BRICEÑO	5
206	15109	BUENAVISTA	5
207	15114	BUSBANZÁ	5
208	15131	CALDAS	5
209	15135	CAMPOHERMOSO	5
210	15162	CERINZA	5
211	15172	CHINAVITA	5
212	15176	CHIQUINQUIRÁ	5
213	15180	CHISCAS	5
214	15183	CHITA	5
215	15185	CHITARAQUE	5
216	15187	CHIVATÁ	5
217	15189	CIÉNEGA	5
218	15204	CÓMBITA	5
219	15212	COPER	5
220	15215	CORRALES	5
221	15218	COVARACHÍA	5
222	15223	CUBARÁ	5
223	15224	CUCAITA	5
224	15226	CUÍTIVA	5
225	15232	CHÍQUIZA	5
226	15236	CHIVOR	5
227	15238	DUITAMA	5
228	15244	EL COCUY	5
229	15248	EL ESPINO	5
230	15272	FIRAVITOBA	5
231	15276	FLORESTA	5
232	15293	GACHANTIVÁ	5
233	15296	GÁMEZA	5
234	15299	GARAGOA	5
235	15317	GUACAMAYAS	5
236	15322	GUATEQUE	5
237	15325	GUAYATÁ	5
238	15332	GÜICÁN DE LA SIERRA	5
239	15362	IZA	5
240	15367	JENESANO	5
241	15368	JERICÓ	5
242	15377	LABRANZAGRANDE	5
243	15380	LA CAPILLA	5
244	15401	LA VICTORIA	5
245	15403	LA UVITA	5
246	15407	VILLA DE LEYVA	5
247	15425	MACANAL	5
248	15442	MARIPÍ	5
249	15455	MIRAFLORES	5
250	15464	MONGUA	5
251	15466	MONGUÍ	5
252	15469	MONIQUIRÁ	5
253	15476	MOTAVITA	5
254	15480	MUZO	5
255	15491	NOBSA	5
256	15494	NUEVO COLÓN	5
257	15500	OICATÁ	5
258	15507	OTANCHE	5
259	15511	PACHAVITA	5
260	15514	PÁEZ	5
261	15516	PAIPA	5
262	15518	PAJARITO	5
263	15522	PANQUEBA	5
264	15531	PAUNA	5
265	15533	PAYA	5
266	15537	PAZ DE RÍO	5
267	15542	PESCA	5
268	15550	PISBA	5
269	15572	PUERTO BOYACÁ	5
270	15580	QUÍPAMA	5
271	15599	RAMIRIQUÍ	5
272	15600	RÁQUIRA	5
273	15621	RONDÓN	5
274	15632	SABOYÁ	5
275	15638	SÁCHICA	5
276	15646	SAMACÁ	5
277	15660	SAN EDUARDO	5
278	15664	SAN JOSÉ DE PARE	5
279	15667	SAN LUIS DE GACENO	5
280	15673	SAN MATEO	5
281	15676	SAN MIGUEL DE SEMA	5
282	15681	SAN PABLO DE BORBUR	5
283	15686	SANTANA	5
284	15690	SANTA MARÍA	5
285	15693	SANTA ROSA DE VITERBO	5
286	15696	SANTA SOFÍA	5
287	15720	SATIVANORTE	5
288	15723	SATIVASUR	5
289	15740	SIACHOQUE	5
290	15753	SOATÁ	5
291	15755	SOCOTÁ	5
292	15757	SOCHA	5
293	15759	SOGAMOSO	5
294	15761	SOMONDOCO	5
295	15762	SORA	5
296	15763	SOTAQUIRÁ	5
297	15764	SORACÁ	5
298	15774	SUSACÓN	5
299	15776	SUTAMARCHÁN	5
300	15778	SUTATENZA	5
301	15790	TASCO	5
302	15798	TENZA	5
303	15804	TIBANÁ	5
304	15806	TIBASOSA	5
305	15808	TINJACÁ	5
306	15810	TIPACOQUE	5
307	15814	TOCA	5
308	15816	TOGÜÍ	5
309	15820	TÓPAGA	5
310	15822	TOTA	5
311	15832	TUNUNGUÁ	5
312	15835	TURMEQUÉ	5
313	15837	TUTA	5
314	15839	TUTAZÁ	5
315	15842	ÚMBITA	5
316	15861	VENTAQUEMADA	5
317	15879	VIRACACHÁ	5
318	15897	ZETAQUIRA	5
319	17001	MANIZALES	6
320	17013	AGUADAS	6
321	17042	ANSERMA	6
322	17050	ARANZAZU	6
323	17088	BELALCÁZAR	6
324	17174	CHINCHINÁ	6
325	17272	FILADELFIA	6
326	17380	LA DORADA	6
327	17388	LA MERCED	6
328	17433	MANZANARES	6
329	17442	MARMATO	6
330	17444	MARQUETALIA	6
331	17446	MARULANDA	6
332	17486	NEIRA	6
333	17495	NORCASIA	6
334	17513	PÁCORA	6
335	17524	PALESTINA	6
336	17541	PENSILVANIA	6
337	17614	RIOSUCIO	6
338	17616	RISARALDA	6
339	17653	SALAMINA	6
340	17662	SAMANÁ	6
341	17665	SAN JOSÉ	6
342	17777	SUPÍA	6
343	17867	VICTORIA	6
344	17873	VILLAMARÍA	6
345	17877	VITERBO	6
346	18001	FLORENCIA	7
347	18029	ALBANIA	7
348	18094	BELÉN DE LOS ANDAQUÍES	7
349	18150	CARTAGENA DEL CHAIRÁ	7
350	18205	CURILLO	7
351	18247	EL DONCELLO	7
352	18256	EL PAUJÍL	7
353	18410	LA MONTAÑITA	7
354	18460	MILÁN	7
355	18479	MORELIA	7
356	18592	PUERTO RICO	7
357	18610	SAN JOSÉ DEL FRAGUA	7
358	18753	SAN VICENTE DEL CAGUÁN	7
359	18756	SOLANO	7
360	18785	SOLITA	7
361	18860	VALPARAÍSO	7
362	19001	POPAYÁN	8
363	19022	ALMAGUER	8
364	19050	ARGELIA	8
365	19075	BALBOA	8
366	19100	BOLÍVAR	8
367	19110	BUENOS AIRES	8
368	19130	CAJIBÍO	8
369	19137	CALDONO	8
370	19142	CALOTO	8
371	19212	CORINTO	8
372	19256	EL TAMBO	8
373	19290	FLORENCIA	8
374	19300	GUACHENÉ	8
375	19318	GUAPI	8
376	19355	INZÁ	8
377	19364	JAMBALÓ	8
378	19392	LA SIERRA	8
379	19397	LA VEGA	8
380	19418	LÓPEZ DE MICAY	8
381	19450	MERCADERES	8
382	19455	MIRANDA	8
383	19473	MORALES	8
384	19513	PADILLA	8
385	19517	PÁEZ	8
386	19532	PATÍA	8
387	19533	PIAMONTE	8
388	19548	PIENDAMÓ - TUNÍA	8
389	19573	PUERTO TEJADA	8
390	19585	PURACÉ	8
391	19622	ROSAS	8
392	19693	SAN SEBASTIÁN	8
393	19698	SANTANDER DE QUILICHAO	8
394	19701	SANTA ROSA	8
395	19743	SILVIA	8
396	19760	SOTARÁ PAISPAMBA	8
397	19780	SUÁREZ	8
398	19785	SUCRE	8
399	19807	TIMBÍO	8
400	19809	TIMBIQUÍ	8
401	19821	TORIBÍO	8
402	19824	TOTORÓ	8
403	19845	VILLA RICA	8
404	20001	VALLEDUPAR	9
405	20011	AGUACHICA	9
406	20013	AGUSTÍN CODAZZI	9
407	20032	ASTREA	9
408	20045	BECERRIL	9
409	20060	BOSCONIA	9
410	20175	CHIMICHAGUA	9
411	20178	CHIRIGUANÁ	9
412	20228	CURUMANÍ	9
413	20238	EL COPEY	9
414	20250	EL PASO	9
415	20295	GAMARRA	9
416	20310	GONZÁLEZ	9
417	20383	LA GLORIA	9
418	20400	LA JAGUA DE IBIRICO	9
419	20443	MANAURE BALCÓN DEL CESAR	9
420	20517	PAILITAS	9
421	20550	PELAYA	9
422	20570	PUEBLO BELLO	9
423	20614	RÍO DE ORO	9
424	20621	LA PAZ	9
425	20710	SAN ALBERTO	9
426	20750	SAN DIEGO	9
427	20770	SAN MARTÍN	9
428	20787	TAMALAMEQUE	9
429	23001	MONTERÍA	10
430	23068	AYAPEL	10
431	23079	BUENAVISTA	10
432	23090	CANALETE	10
433	23162	CERETÉ	10
434	23168	CHIMÁ	10
435	23182	CHINÚ	10
436	23189	CIÉNAGA DE ORO	10
437	23300	COTORRA	10
438	23350	LA APARTADA	10
439	23417	LORICA	10
440	23419	LOS CÓRDOBAS	10
441	23464	MOMIL	10
442	23466	MONTELÍBANO	10
443	23500	MOÑITOS	10
444	23555	PLANETA RICA	10
445	23570	PUEBLO NUEVO	10
446	23574	PUERTO ESCONDIDO	10
447	23580	PUERTO LIBERTADOR	10
448	23586	PURÍSIMA DE LA CONCEPCIÓN	10
449	23660	SAHAGÚN	10
450	23670	SAN ANDRÉS DE SOTAVENTO	10
451	23672	SAN ANTERO	10
452	23675	SAN BERNARDO DEL VIENTO	10
453	23678	SAN CARLOS	10
454	23682	SAN JOSÉ DE URÉ	10
455	23686	SAN PELAYO	10
456	23807	TIERRALTA	10
457	23815	TUCHÍN	10
458	23855	VALENCIA	10
459	25001	AGUA DE DIOS	11
460	25019	ALBÁN	11
461	25035	ANAPOIMA	11
462	25040	ANOLAIMA	11
463	25053	ARBELÁEZ	11
464	25086	BELTRÁN	11
465	25095	BITUIMA	11
466	25099	BOJACÁ	11
467	25120	CABRERA	11
468	25123	CACHIPAY	11
469	25126	CAJICÁ	11
470	25148	CAPARRAPÍ	11
471	25151	CÁQUEZA	11
472	25154	CARMEN DE CARUPA	11
473	25168	CHAGUANÍ	11
474	25175	CHÍA	11
475	25178	CHIPAQUE	11
476	25181	CHOACHÍ	11
477	25183	CHOCONTÁ	11
478	25200	COGUA	11
479	25214	COTA	11
480	25224	CUCUNUBÁ	11
481	25245	EL COLEGIO	11
482	25258	EL PEÑÓN	11
483	25260	EL ROSAL	11
484	25269	FACATATIVÁ	11
485	25279	FÓMEQUE	11
486	25281	FOSCA	11
487	25286	FUNZA	11
488	25288	FÚQUENE	11
489	25290	FUSAGASUGÁ	11
490	25293	GACHALÁ	11
491	25295	GACHANCIPÁ	11
492	25297	GACHETÁ	11
493	25299	GAMA	11
494	25307	GIRARDOT	11
495	25312	GRANADA	11
496	25317	GUACHETÁ	11
497	25320	GUADUAS	11
498	25322	GUASCA	11
499	25324	GUATAQUÍ	11
500	25326	GUATAVITA	11
501	25328	GUAYABAL DE SÍQUIMA	11
502	25335	GUAYABETAL	11
503	25339	GUTIÉRREZ	11
504	25368	JERUSALÉN	11
505	25372	JUNÍN	11
506	25377	LA CALERA	11
507	25386	LA MESA	11
508	25394	LA PALMA	11
509	25398	LA PEÑA	11
510	25402	LA VEGA	11
511	25407	LENGUAZAQUE	11
512	25426	MACHETÁ	11
513	25430	MADRID	11
514	25436	MANTA	11
515	25438	MEDINA	11
516	25473	MOSQUERA	11
517	25483	NARIÑO	11
518	25486	NEMOCÓN	11
519	25488	NILO	11
520	25489	NIMAIMA	11
521	25491	NOCAIMA	11
522	25506	VENECIA	11
523	25513	PACHO	11
524	25518	PAIME	11
525	25524	PANDI	11
526	25530	PARATEBUENO	11
527	25535	PASCA	11
528	25572	PUERTO SALGAR	11
529	25580	PULÍ	11
530	25592	QUEBRADANEGRA	11
531	25594	QUETAME	11
532	25596	QUIPILE	11
533	25599	APULO	11
534	25612	RICAURTE	11
535	25645	SAN ANTONIO DEL TEQUENDAMA	11
536	25649	SAN BERNARDO	11
537	25653	SAN CAYETANO	11
538	25658	SAN FRANCISCO	11
539	25662	SAN JUAN DE RIOSECO	11
540	25718	SASAIMA	11
541	25736	SESQUILÉ	11
542	25740	SIBATÉ	11
543	25743	SILVANIA	11
544	25745	SIMIJACA	11
545	25754	SOACHA	11
546	25758	SOPÓ	11
547	25769	SUBACHOQUE	11
548	25772	SUESCA	11
549	25777	SUPATÁ	11
550	25779	SUSA	11
551	25781	SUTATAUSA	11
552	25785	TABIO	11
553	25793	TAUSA	11
554	25797	TENA	11
555	25799	TENJO	11
556	25805	TIBACUY	11
557	25807	TIBIRITA	11
558	25815	TOCAIMA	11
559	25817	TOCANCIPÁ	11
560	25823	TOPAIPÍ	11
561	25839	UBALÁ	11
562	25841	UBAQUE	11
563	25843	VILLA DE SAN DIEGO DE UBATÉ	11
564	25845	UNE	11
565	25851	ÚTICA	11
566	25862	VERGARA	11
567	25867	VIANÍ	11
568	25871	VILLAGÓMEZ	11
569	25873	VILLAPINZÓN	11
570	25875	VILLETA	11
571	25878	VIOTÁ	11
572	25885	YACOPÍ	11
573	25898	ZIPACÓN	11
574	25899	ZIPAQUIRÁ	11
575	27001	QUIBDÓ	12
576	27006	ACANDÍ	12
577	27025	ALTO BAUDÓ	12
578	27050	ATRATO	12
579	27073	BAGADÓ	12
580	27075	BAHÍA SOLANO	12
581	27077	BAJO BAUDÓ	12
582	27099	BOJAYÁ	12
583	27135	EL CANTÓN DEL SAN PABLO	12
584	27150	CARMEN DEL DARIÉN	12
585	27160	CÉRTEGUI	12
586	27205	CONDOTO	12
587	27245	EL CARMEN DE ATRATO	12
588	27250	EL LITORAL DEL SAN JUAN	12
589	27361	ISTMINA	12
590	27372	JURADÓ	12
591	27413	LLORÓ	12
592	27425	MEDIO ATRATO	12
593	27430	MEDIO BAUDÓ	12
594	27450	MEDIO SAN JUAN	12
595	27491	NÓVITA	12
596	27495	NUQUÍ	12
597	27580	RÍO IRÓ	12
598	27600	RÍO QUITO	12
599	27615	RIOSUCIO	12
600	27660	SAN JOSÉ DEL PALMAR	12
601	27745	SIPÍ	12
602	27787	TADÓ	12
603	27800	UNGUÍA	12
604	27810	UNIÓN PANAMERICANA	12
605	41001	NEIVA	13
606	41006	ACEVEDO	13
607	41013	AGRADO	13
608	41016	AIPE	13
609	41020	ALGECIRAS	13
610	41026	ALTAMIRA	13
611	41078	BARAYA	13
612	41132	CAMPOALEGRE	13
613	41206	COLOMBIA	13
614	41244	ELÍAS	13
615	41298	GARZÓN	13
616	41306	GIGANTE	13
617	41319	GUADALUPE	13
618	41349	HOBO	13
619	41357	ÍQUIRA	13
620	41359	ISNOS	13
621	41378	LA ARGENTINA	13
622	41396	LA PLATA	13
623	41483	NÁTAGA	13
624	41503	OPORAPA	13
625	41518	PAICOL	13
626	41524	PALERMO	13
627	41530	PALESTINA	13
628	41548	PITAL	13
629	41551	PITALITO	13
630	41615	RIVERA	13
631	41660	SALADOBLANCO	13
632	41668	SAN AGUSTÍN	13
633	41676	SANTA MARÍA	13
634	41770	SUAZA	13
635	41791	TARQUI	13
636	41797	TESALIA	13
637	41799	TELLO	13
638	41801	TERUEL	13
639	41807	TIMANÁ	13
640	41872	VILLAVIEJA	13
641	41885	YAGUARÁ	13
642	44001	RIOHACHA	14
643	44035	ALBANIA	14
644	44078	BARRANCAS	14
645	44090	DIBULLA	14
646	44098	DISTRACCIÓN	14
647	44110	EL MOLINO	14
648	44279	FONSECA	14
649	44378	HATONUEVO	14
650	44420	LA JAGUA DEL PILAR	14
651	44430	MAICAO	14
652	44560	MANAURE	14
653	44650	SAN JUAN DEL CESAR	14
654	44847	URIBIA	14
655	44855	URUMITA	14
656	44874	VILLANUEVA	14
657	47001	SANTA MARTA	15
658	47030	ALGARROBO	15
659	47053	ARACATACA	15
660	47058	ARIGUANÍ	15
661	47161	CERRO DE SAN ANTONIO	15
662	47170	CHIVOLO	15
663	47189	CIÉNAGA	15
664	47205	CONCORDIA	15
665	47245	EL BANCO	15
666	47258	EL PIÑÓN	15
667	47268	EL RETÉN	15
668	47288	FUNDACIÓN	15
669	47318	GUAMAL	15
670	47460	NUEVA GRANADA	15
671	47541	PEDRAZA	15
672	47545	PIJIÑO DEL CARMEN	15
673	47551	PIVIJAY	15
674	47555	PLATO	15
675	47570	PUEBLOVIEJO	15
676	47605	REMOLINO	15
677	47660	SABANAS DE SAN ÁNGEL	15
678	47675	SALAMINA	15
679	47692	SAN SEBASTIÁN DE BUENAVISTA	15
680	47703	SAN ZENÓN	15
681	47707	SANTA ANA	15
682	47720	SANTA BÁRBARA DE PINTO	15
683	47745	SITIONUEVO	15
684	47798	TENERIFE	15
685	47960	ZAPAYÁN	15
686	47980	ZONA BANANERA	15
687	50001	VILLAVICENCIO	16
688	50006	ACACÍAS	16
689	50110	BARRANCA DE UPÍA	16
690	50124	CABUYARO	16
691	50150	CASTILLA LA NUEVA	16
692	50223	CUBARRAL	16
693	50226	CUMARAL	16
694	50245	EL CALVARIO	16
695	50251	EL CASTILLO	16
696	50270	EL DORADO	16
697	50287	FUENTE DE ORO	16
698	50313	GRANADA	16
699	50318	GUAMAL	16
700	50325	MAPIRIPÁN	16
701	50330	MESETAS	16
702	50350	LA MACARENA	16
703	50370	URIBE	16
704	50400	LEJANÍAS	16
705	50450	PUERTO CONCORDIA	16
706	50568	PUERTO GAITÁN	16
707	50573	PUERTO LÓPEZ	16
708	50577	PUERTO LLERAS	16
709	50590	PUERTO RICO	16
710	50606	RESTREPO	16
711	50680	SAN CARLOS DE GUAROA	16
712	50683	SAN JUAN DE ARAMA	16
713	50686	SAN JUANITO	16
714	50689	SAN MARTÍN	16
715	50711	VISTAHERMOSA	16
716	52001	PASTO	17
717	52019	ALBÁN	17
718	52022	ALDANA	17
719	52036	ANCUYA	17
720	52051	ARBOLEDA	17
721	52079	BARBACOAS	17
722	52083	BELÉN	17
723	52110	BUESACO	17
724	52203	COLÓN	17
725	52207	CONSACÁ	17
726	52210	CONTADERO	17
727	52215	CÓRDOBA	17
728	52224	CUASPUD CARLOSAMA	17
729	52227	CUMBAL	17
730	52233	CUMBITARA	17
731	52240	CHACHAGÜÍ	17
732	52250	EL CHARCO	17
733	52254	EL PEÑOL	17
734	52256	EL ROSARIO	17
735	52258	EL TABLÓN DE GÓMEZ	17
736	52260	EL TAMBO	17
737	52287	FUNES	17
738	52317	GUACHUCAL	17
739	52320	GUAITARILLA	17
740	52323	GUALMATÁN	17
741	52352	ILES	17
742	52354	IMUÉS	17
743	52356	IPIALES	17
744	52378	LA CRUZ	17
745	52381	LA FLORIDA	17
746	52385	LA LLANADA	17
747	52390	LA TOLA	17
748	52399	LA UNIÓN	17
749	52405	LEIVA	17
750	52411	LINARES	17
751	52418	LOS ANDES	17
752	52427	MAGÜÍ	17
753	52435	MALLAMA	17
754	52473	MOSQUERA	17
755	52480	NARIÑO	17
756	52490	OLAYA HERRERA	17
757	52506	OSPINA	17
758	52520	FRANCISCO PIZARRO	17
759	52540	POLICARPA	17
760	52560	POTOSÍ	17
761	52565	PROVIDENCIA	17
762	52573	PUERRES	17
763	52585	PUPIALES	17
764	52612	RICAURTE	17
765	52621	ROBERTO PAYÁN	17
766	52678	SAMANIEGO	17
767	52683	SANDONÁ	17
768	52685	SAN BERNARDO	17
769	52687	SAN LORENZO	17
770	52693	SAN PABLO	17
771	52694	SAN PEDRO DE CARTAGO	17
772	52696	SANTA BÁRBARA	17
773	52699	SANTACRUZ	17
774	52720	SAPUYES	17
775	52786	TAMINANGO	17
776	52788	TANGUA	17
777	52835	SAN ANDRÉS DE TUMACO	17
778	52838	TÚQUERRES	17
779	52885	YACUANQUER	17
780	54001	SAN JOSÉ DE CÚCUTA	18
781	54003	ÁBREGO	18
782	54051	ARBOLEDAS	18
783	54099	BOCHALEMA	18
784	54109	BUCARASICA	18
785	54125	CÁCOTA	18
786	54128	CÁCHIRA	18
787	54172	CHINÁCOTA	18
788	54174	CHITAGÁ	18
789	54206	CONVENCIÓN	18
790	54223	CUCUTILLA	18
791	54239	DURANIA	18
792	54245	EL CARMEN	18
793	54250	EL TARRA	18
794	54261	EL ZULIA	18
795	54313	GRAMALOTE	18
796	54344	HACARÍ	18
797	54347	HERRÁN	18
798	54377	LABATECA	18
799	54385	LA ESPERANZA	18
800	54398	LA PLAYA	18
801	54405	LOS PATIOS	18
802	54418	LOURDES	18
803	54480	MUTISCUA	18
804	54498	OCAÑA	18
805	54518	PAMPLONA	18
806	54520	PAMPLONITA	18
807	54553	PUERTO SANTANDER	18
808	54599	RAGONVALIA	18
809	54660	SALAZAR	18
810	54670	SAN CALIXTO	18
811	54673	SAN CAYETANO	18
812	54680	SANTIAGO	18
813	54720	SARDINATA	18
814	54743	SILOS	18
815	54800	TEORAMA	18
816	54810	TIBÚ	18
817	54820	TOLEDO	18
818	54871	VILLA CARO	18
819	54874	VILLA DEL ROSARIO	18
820	63001	ARMENIA	19
821	63111	BUENAVISTA	19
822	63130	CALARCÁ	19
823	63190	CIRCASIA	19
824	63212	CÓRDOBA	19
825	63272	FILANDIA	19
826	63302	GÉNOVA	19
827	63401	LA TEBAIDA	19
828	63470	MONTENEGRO	19
829	63548	PIJAO	19
830	63594	QUIMBAYA	19
831	63690	SALENTO	19
832	66001	PEREIRA	20
833	66045	APÍA	20
834	66075	BALBOA	20
835	66088	BELÉN DE UMBRÍA	20
836	66170	DOSQUEBRADAS	20
837	66318	GUÁTICA	20
838	66383	LA CELIA	20
839	66400	LA VIRGINIA	20
840	66440	MARSELLA	20
841	66456	MISTRATÓ	20
842	66572	PUEBLO RICO	20
843	66594	QUINCHÍA	20
844	66682	SANTA ROSA DE CABAL	20
845	66687	SANTUARIO	20
846	68001	BUCARAMANGA	21
847	68013	AGUADA	21
848	68020	ALBANIA	21
849	68051	ARATOCA	21
850	68077	BARBOSA	21
851	68079	BARICHARA	21
852	68081	BARRANCABERMEJA	21
853	68092	BETULIA	21
854	68101	BOLÍVAR	21
855	68121	CABRERA	21
856	68132	CALIFORNIA	21
857	68147	CAPITANEJO	21
858	68152	CARCASÍ	21
859	68160	CEPITÁ	21
860	68162	CERRITO	21
861	68167	CHARALÁ	21
862	68169	CHARTA	21
863	68176	CHIMA	21
864	68179	CHIPATÁ	21
865	68190	CIMITARRA	21
866	68207	CONCEPCIÓN	21
867	68209	CONFINES	21
868	68211	CONTRATACIÓN	21
869	68217	COROMORO	21
870	68229	CURITÍ	21
871	68235	EL CARMEN DE CHUCURÍ	21
872	68245	EL GUACAMAYO	21
873	68250	EL PEÑÓN	21
874	68255	EL PLAYÓN	21
875	68264	ENCINO	21
876	68266	ENCISO	21
877	68271	FLORIÁN	21
878	68276	FLORIDABLANCA	21
879	68296	GALÁN	21
880	68298	GÁMBITA	21
881	68307	GIRÓN	21
882	68318	GUACA	21
883	68320	GUADALUPE	21
884	68322	GUAPOTÁ	21
885	68324	GUAVATÁ	21
886	68327	GÜEPSA	21
887	68344	HATO	21
888	68368	JESÚS MARÍA	21
889	68370	JORDÁN	21
890	68377	LA BELLEZA	21
891	68385	LANDÁZURI	21
892	68397	LA PAZ	21
893	68406	LEBRIJA	21
894	68418	LOS SANTOS	21
895	68425	MACARAVITA	21
896	68432	MÁLAGA	21
897	68444	MATANZA	21
898	68464	MOGOTES	21
899	68468	MOLAGAVITA	21
900	68498	OCAMONTE	21
901	68500	OIBA	21
902	68502	ONZAGA	21
903	68522	PALMAR	21
904	68524	PALMAS DEL SOCORRO	21
905	68533	PÁRAMO	21
906	68547	PIEDECUESTA	21
907	68549	PINCHOTE	21
908	68572	PUENTE NACIONAL	21
909	68573	PUERTO PARRA	21
910	68575	PUERTO WILCHES	21
911	68615	RIONEGRO	21
912	68655	SABANA DE TORRES	21
913	68669	SAN ANDRÉS	21
914	68673	SAN BENITO	21
915	68679	SAN GIL	21
916	68682	SAN JOAQUÍN	21
917	68684	SAN JOSÉ DE MIRANDA	21
918	68686	SAN MIGUEL	21
919	68689	SAN VICENTE DE CHUCURÍ	21
920	68705	SANTA BÁRBARA	21
921	68720	SANTA HELENA DEL OPÓN	21
922	68745	SIMACOTA	21
923	68755	SOCORRO	21
924	68770	SUAITA	21
925	68773	SUCRE	21
926	68780	SURATÁ	21
927	68820	TONA	21
928	68855	VALLE DE SAN JOSÉ	21
929	68861	VÉLEZ	21
930	68867	VETAS	21
931	68872	VILLANUEVA	21
932	68895	ZAPATOCA	21
933	70001	SINCELEJO	22
934	70110	BUENAVISTA	22
935	70124	CAIMITO	22
936	70204	COLOSÓ	22
937	70215	COROZAL	22
938	70221	COVEÑAS	22
939	70230	CHALÁN	22
940	70233	EL ROBLE	22
941	70235	GALERAS	22
942	70265	GUARANDA	22
943	70400	LA UNIÓN	22
944	70418	LOS PALMITOS	22
945	70429	MAJAGUAL	22
946	70473	MORROA	22
947	70508	OVEJAS	22
948	70523	PALMITO	22
949	70670	SAMPUÉS	22
950	70678	SAN BENITO ABAD	22
951	70702	SAN JUAN DE BETULIA	22
952	70708	SAN MARCOS	22
953	70713	SAN ONOFRE	22
954	70717	SAN PEDRO	22
955	70742	SAN LUIS DE SINCÉ	22
956	70771	SUCRE	22
957	70820	SANTIAGO DE TOLÚ	22
958	70823	SAN JOSÉ DE TOLUVIEJO	22
959	73001	IBAGUÉ	23
960	73024	ALPUJARRA	23
961	73026	ALVARADO	23
962	73030	AMBALEMA	23
963	73043	ANZOÁTEGUI	23
964	73055	ARMERO	23
965	73067	ATACO	23
966	73124	CAJAMARCA	23
967	73148	CARMEN DE APICALÁ	23
968	73152	CASABIANCA	23
969	73168	CHAPARRAL	23
970	73200	COELLO	23
971	73217	COYAIMA	23
972	73226	CUNDAY	23
973	73236	DOLORES	23
974	73268	ESPINAL	23
975	73270	FALAN	23
976	73275	FLANDES	23
977	73283	FRESNO	23
978	73319	GUAMO	23
979	73347	HERVEO	23
980	73349	HONDA	23
981	73352	ICONONZO	23
982	73408	LÉRIDA	23
983	73411	LÍBANO	23
984	73443	SAN SEBASTIÁN DE MARIQUITA	23
985	73449	MELGAR	23
986	73461	MURILLO	23
987	73483	NATAGAIMA	23
988	73504	ORTEGA	23
989	73520	PALOCABILDO	23
990	73547	PIEDRAS	23
991	73555	PLANADAS	23
992	73563	PRADO	23
993	73585	PURIFICACIÓN	23
994	73616	RIOBLANCO	23
995	73622	RONCESVALLES	23
996	73624	ROVIRA	23
997	73671	SALDAÑA	23
998	73675	SAN ANTONIO	23
999	73678	SAN LUIS	23
1000	73686	SANTA ISABEL	23
1001	73770	SUÁREZ	23
1002	73854	VALLE DE SAN JUAN	23
1003	73861	VENADILLO	23
1004	73870	VILLAHERMOSA	23
1005	73873	VILLARRICA	23
1006	76001	CALI	24
1007	76020	ALCALÁ	24
1008	76036	ANDALUCÍA	24
1009	76041	ANSERMANUEVO	24
1010	76054	ARGELIA	24
1011	76100	BOLÍVAR	24
1012	76109	BUENAVENTURA	24
1013	76111	GUADALAJARA DE BUGA	24
1014	76113	BUGALAGRANDE	24
1015	76122	CAICEDONIA	24
1016	76126	CALIMA	24
1017	76130	CANDELARIA	24
1018	76147	CARTAGO	24
1019	76233	DAGUA	24
1020	76243	EL ÁGUILA	24
1021	76246	EL CAIRO	24
1022	76248	EL CERRITO	24
1023	76250	EL DOVIO	24
1024	76275	FLORIDA	24
1025	76306	GINEBRA	24
1026	76318	GUACARÍ	24
1027	76364	JAMUNDÍ	24
1028	76377	LA CUMBRE	24
1029	76400	LA UNIÓN	24
1030	76403	LA VICTORIA	24
1031	76497	OBANDO	24
1032	76520	PALMIRA	24
1033	76563	PRADERA	24
1034	76606	RESTREPO	24
1035	76616	RIOFRÍO	24
1036	76622	ROLDANILLO	24
1037	76670	SAN PEDRO	24
1038	76736	SEVILLA	24
1039	76823	TORO	24
1040	76828	TRUJILLO	24
1041	76834	TULUÁ	24
1042	76845	ULLOA	24
1043	76863	VERSALLES	24
1044	76869	VIJES	24
1045	76890	YOTOCO	24
1046	76892	YUMBO	24
1047	76895	ZARZAL	24
1048	81001	ARAUCA	25
1049	81065	ARAUQUITA	25
1050	81220	CRAVO NORTE	25
1051	81300	FORTUL	25
1052	81591	PUERTO RONDÓN	25
1053	81736	SARAVENA	25
1054	81794	TAME	25
1055	85001	YOPAL	26
1056	85010	AGUAZUL	26
1057	85015	CHÁMEZA	26
1058	85125	HATO COROZAL	26
1059	85136	LA SALINA	26
1060	85139	MANÍ	26
1061	85162	MONTERREY	26
1062	85225	NUNCHÍA	26
1063	85230	OROCUÉ	26
1064	85250	PAZ DE ARIPORO	26
1065	85263	PORE	26
1066	85279	RECETOR	26
1067	85300	SABANALARGA	26
1068	85315	SÁCAMA	26
1069	85325	SAN LUIS DE PALENQUE	26
1070	85400	TÁMARA	26
1071	85410	TAURAMENA	26
1072	85430	TRINIDAD	26
1073	85440	VILLANUEVA	26
1074	86001	MOCOA	27
1075	86219	COLÓN	27
1076	86320	ORITO	27
1077	86568	PUERTO ASÍS	27
1078	86569	PUERTO CAICEDO	27
1079	86571	PUERTO GUZMÁN	27
1080	86573	PUERTO LEGUÍZAMO	27
1081	86749	SIBUNDOY	27
1082	86755	SAN FRANCISCO	27
1083	86757	SAN MIGUEL	27
1084	86760	SANTIAGO	27
1085	86865	VALLE DEL GUAMUEZ	27
1086	86885	VILLAGARZÓN	27
1087	88001	SAN ANDRÉS	28
1088	88564	PROVIDENCIA	28
1089	91001	LETICIA	29
1090	91263	EL ENCANTO	29
1091	91405	LA CHORRERA	29
1092	91407	LA PEDRERA	29
1093	91430	LA VICTORIA	29
1094	91460	MIRITÍ - PARANÁ	29
1095	91530	PUERTO ALEGRÍA	29
1096	91536	PUERTO ARICA	29
1097	91540	PUERTO NARIÑO	29
1098	91669	PUERTO SANTANDER	29
1099	91798	TARAPACÁ	29
1100	94001	INÍRIDA	30
1101	94343	BARRANCOMINAS	30
1102	94883	SAN FELIPE	30
1103	94884	PUERTO COLOMBIA	30
1104	94885	LA GUADALUPE	30
1105	94886	CACAHUAL	30
1106	94887	PANA PANA	30
1107	94888	MORICHAL	30
1108	95001	SAN JOSÉ DEL GUAVIARE	31
1109	95015	CALAMAR	31
1110	95025	EL RETORNO	31
1111	95200	MIRAFLORES	31
1112	97001	MITÚ	32
1113	97161	CARURÚ	32
1114	97511	PACOA	32
1115	97666	TARAIRA	32
1116	97777	PAPUNAHUA	32
1117	97889	YAVARATÉ	32
1118	99001	PUERTO CARREÑO	33
1119	99524	LA PRIMAVERA	33
1120	99624	SANTA ROSALÍA	33
1121	99773	CUMARIBO	33
\.


--
-- Data for Name: periodos_academicos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.periodos_academicos (id_periodo, ano_lectivo, numero, nombre, fecha_inicio, fecha_fin, porcentaje) FROM stdin;
PPER-001	2026	1	Primer Período	2026-02-01	2026-03-31	25.00
PPER-002	2026	2	Segundo Período	2026-04-01	2026-06-30	25.00
PPER-003	2026	3	Tercer Período	2026-07-15	2026-09-30	25.00
PPER-005	2026	4	Cuarto Período	2026-10-01	2026-11-30	25.00
\.


--
-- Data for Name: personal; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.personal (id_personal, numero_documento, nombres, apellidos, telefono, correo_electronico, cargo, escalafon_grado, decreto_nombramiento, tipo_vinculacion, foto_url, estado_laboral, fecha_estado_laboral) FROM stdin;
\.


--
-- Data for Name: plan_estudio; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.plan_estudio (id_plan, id_grado, id_asignatura, horas_semana) FROM stdin;
PE-001	GRA-06	ASG-003	5
PE-002	GRA-06	ASG-002	4
\.


--
-- Data for Name: sectores; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sectores (id_sector, id_municipio, nombre_sector, tipo, activo, fecha_creacion, observacion) FROM stdin;
1	1	LAS PALMAS	Barrio	t	2026-08-03 13:32:52.334681	
2	433	LAS PALMAS	Barrio	t	2026-08-12 13:39:38.358261	
3	433	EL CAÑITO	Barrio	t	2026-08-12 13:40:16.130988	Lugar de nuestra sede principal
4	433	LOS NOGALES	Barrio	t	2026-08-12 13:47:28.303441	
5	576	EL LOCO	Barrio	t	2026-08-19 19:44:38.626337	
6	433	SANTA MARIA	Barrio	t	2026-08-19 20:44:12.102455	
7	433	LA LUCHA	Vereda	t	2026-08-19 20:49:16.909484	
8	433	EL NOBAL	Barrio	t	2026-08-19 20:51:34.448593	
9	433	NUEVO HORIZONTE	Vereda	t	2026-08-19 20:55:31.350621	
10	433	DGFDGFDG	Barrio	t	2026-08-19 20:59:03.388969	
\.


--
-- Data for Name: sedes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sedes (id_sede, id_institucion, nombre_sede, direccion, telefono_sede) FROM stdin;
SED-PRINCIPAL	INST-DICA	Cañito de los Sabalos	Barrio el Cañito	3126639930
SED-003	INST-DICA	Santa Maria	\N	3105274086
\.


--
-- Data for Name: tipos_documento; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tipos_documento (id_tipo_documento, codigo, descripcion, activo) FROM stdin;
1	RC	Registro Civil	t
2	TI	Tarjeta de Identidad	t
3	CC	Cédula de Ciudadanía	t
4	CE	Cédula de Extranjería	t
5	PPT	Permiso por Protección Temporal	t
6	PEP	Permiso Especial de Permanencia	t
7	PAS	Pasaporte	t
8	NIT	NIT	t
9	NUIP	Número Único de Identificación Personal	t
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id_usuario, usuario, password_hash, rol, estado, id_docente, id_estudiante, id_acudiente, ultimo_acceso, fecha_creacion) FROM stdin;
1	admin	$2b$12$CiBEXbfgKHOUyNKWQ1SRe.qF9oyENw02HplxUkVFrA24OXjbw7DBO	ADMIN	ACTIVO	\N	\N	\N	2026-09-08 19:29:07.76773	2026-07-14 09:14:14.234929
4	Delio Diaz	$2b$12$Q4d0D0lBmX2WV2eSduuN5uJppVPkf90CXrQYNb6Zox7bPfjCg.xbO	DOCENTE	ACTIVO	\N	\N	\N	2026-07-28 22:16:40.666738	2026-07-14 21:47:03.019462
2		$2b$12$sZBkkNO9E/rdc3jTZJsoaeykDaotccFF4aZ/0g0YBKA8gwt1VVJX6	ADMIN	INACTIVO	\N	\N	\N	\N	2026-07-14 21:39:10.796314
\.


--
-- Name: departamentos_id_departamento_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.departamentos_id_departamento_seq', 33, true);


--
-- Name: documentos_acudientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.documentos_acudientes_id_seq', 4, true);


--
-- Name: documentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.documentos_id_seq', 7, true);


--
-- Name: estudiantes_documentos_id_documento_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estudiantes_documentos_id_documento_seq', 1, false);


--
-- Name: matriculas_id_matricula_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.matriculas_id_matricula_seq', 6, true);


--
-- Name: municipios_id_municipio_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.municipios_id_municipio_seq', 1121, true);


--
-- Name: sectores_id_sector_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sectores_id_sector_seq', 10, true);


--
-- Name: seq_id_asignacion_docente; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_asignacion_docente', 1, true);


--
-- Name: seq_id_asignatura; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_asignatura', 3, true);


--
-- Name: seq_id_calificacion; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_calificacion', 1, false);


--
-- Name: seq_id_direccion_grupo; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_direccion_grupo', 2, true);


--
-- Name: seq_id_estudiante; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_estudiante', 276, true);


--
-- Name: seq_id_indicador; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_indicador', 1, true);


--
-- Name: seq_id_periodo; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_periodo', 5, true);


--
-- Name: seq_id_plan_estudio; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_plan_estudio', 2, true);


--
-- Name: seq_id_sede; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seq_id_sede', 3, true);


--
-- Name: tipos_documento_id_tipo_documento_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tipos_documento_id_tipo_documento_seq', 9, true);


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_id_usuario_seq', 4, true);


--
-- Name: acudientes acudientes_numero_documento_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acudientes
    ADD CONSTRAINT acudientes_numero_documento_key UNIQUE (numero_documento);


--
-- Name: acudientes acudientes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acudientes
    ADD CONSTRAINT acudientes_pkey PRIMARY KEY (id_acudiente);


--
-- Name: asignacion_docente asignacion_docente_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_docente
    ADD CONSTRAINT asignacion_docente_pkey PRIMARY KEY (id_asignacion);


--
-- Name: asignaturas asignaturas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignaturas
    ADD CONSTRAINT asignaturas_pkey PRIMARY KEY (id_asignatura);


--
-- Name: boletin_datos boletin_datos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.boletin_datos
    ADD CONSTRAINT boletin_datos_pkey PRIMARY KEY (id_matricula, numero_periodo);


--
-- Name: calificaciones calificaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calificaciones
    ADD CONSTRAINT calificaciones_pkey PRIMARY KEY (id_calificacion);


--
-- Name: cursos cursos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cursos
    ADD CONSTRAINT cursos_pkey PRIMARY KEY (id_curso);


--
-- Name: departamentos departamentos_codigo_dane_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departamentos
    ADD CONSTRAINT departamentos_codigo_dane_key UNIQUE (codigo_dane);


--
-- Name: departamentos departamentos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departamentos
    ADD CONSTRAINT departamentos_pkey PRIMARY KEY (id_departamento);


--
-- Name: direcciones_grupo direcciones_grupo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direcciones_grupo
    ADD CONSTRAINT direcciones_grupo_pkey PRIMARY KEY (id_direccion_grupo);


--
-- Name: documentos_acudientes documentos_acudientes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documentos_acudientes
    ADD CONSTRAINT documentos_acudientes_pkey PRIMARY KEY (id);


--
-- Name: documentos documentos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documentos
    ADD CONSTRAINT documentos_pkey PRIMARY KEY (id);


--
-- Name: escala_valoracion escala_valoracion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.escala_valoracion
    ADD CONSTRAINT escala_valoracion_pkey PRIMARY KEY (id_nivel);


--
-- Name: estudiantes_documentos estudiantes_documentos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estudiantes_documentos
    ADD CONSTRAINT estudiantes_documentos_pkey PRIMARY KEY (id_documento);


--
-- Name: estudiantes estudiantes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estudiantes
    ADD CONSTRAINT estudiantes_pkey PRIMARY KEY (id_estudiante);


--
-- Name: grados grados_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grados
    ADD CONSTRAINT grados_pkey PRIMARY KEY (id_grado);


--
-- Name: indicadores_desempeno indicadores_desempeno_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicadores_desempeno
    ADD CONSTRAINT indicadores_desempeno_pkey PRIMARY KEY (id_indicador);


--
-- Name: instituciones instituciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones
    ADD CONSTRAINT instituciones_pkey PRIMARY KEY (id_institucion);


--
-- Name: jornadas jornadas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jornadas
    ADD CONSTRAINT jornadas_pkey PRIMARY KEY (id_jornada);


--
-- Name: matriculas matriculas_folio_matricula_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.matriculas
    ADD CONSTRAINT matriculas_folio_matricula_key UNIQUE (folio_matricula);


--
-- Name: matriculas matriculas_id_estudiante_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.matriculas
    ADD CONSTRAINT matriculas_id_estudiante_key UNIQUE (id_estudiante);


--
-- Name: matriculas matriculas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.matriculas
    ADD CONSTRAINT matriculas_pkey PRIMARY KEY (id_matricula);


--
-- Name: municipios municipios_codigo_dane_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT municipios_codigo_dane_key UNIQUE (codigo_dane);


--
-- Name: municipios municipios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT municipios_pkey PRIMARY KEY (id_municipio);


--
-- Name: periodos_academicos periodos_academicos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.periodos_academicos
    ADD CONSTRAINT periodos_academicos_pkey PRIMARY KEY (id_periodo);


--
-- Name: personal personal_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personal
    ADD CONSTRAINT personal_pkey PRIMARY KEY (id_personal);


--
-- Name: plan_estudio plan_estudio_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plan_estudio
    ADD CONSTRAINT plan_estudio_pkey PRIMARY KEY (id_plan);


--
-- Name: sectores sectores_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sectores
    ADD CONSTRAINT sectores_pkey PRIMARY KEY (id_sector);


--
-- Name: sedes sedes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sedes
    ADD CONSTRAINT sedes_pkey PRIMARY KEY (id_sede);


--
-- Name: tipos_documento tipos_documento_codigo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_documento
    ADD CONSTRAINT tipos_documento_codigo_key UNIQUE (codigo);


--
-- Name: tipos_documento tipos_documento_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_documento
    ADD CONSTRAINT tipos_documento_pkey PRIMARY KEY (id_tipo_documento);


--
-- Name: asignacion_docente uq_asig_curso_asg_ano; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_docente
    ADD CONSTRAINT uq_asig_curso_asg_ano UNIQUE (id_curso, id_asignatura, ano_lectivo);


--
-- Name: calificaciones uq_calificacion; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calificaciones
    ADD CONSTRAINT uq_calificacion UNIQUE (id_matricula, id_asignatura, numero_periodo);


--
-- Name: direcciones_grupo uq_curso_ano; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direcciones_grupo
    ADD CONSTRAINT uq_curso_ano UNIQUE (id_curso, ano_lectivo);


--
-- Name: periodos_academicos uq_periodo_ano_num; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.periodos_academicos
    ADD CONSTRAINT uq_periodo_ano_num UNIQUE (ano_lectivo, numero);


--
-- Name: direcciones_grupo uq_personal_ano; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direcciones_grupo
    ADD CONSTRAINT uq_personal_ano UNIQUE (id_personal, ano_lectivo);


--
-- Name: plan_estudio uq_plan_grado_asg; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plan_estudio
    ADD CONSTRAINT uq_plan_grado_asg UNIQUE (id_grado, id_asignatura);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- Name: usuarios usuarios_usuario_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_usuario_key UNIQUE (usuario);


--
-- Name: idx_asig_doc_ano; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asig_doc_ano ON public.asignacion_docente USING btree (ano_lectivo);


--
-- Name: idx_asig_doc_curso; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asig_doc_curso ON public.asignacion_docente USING btree (id_curso);


--
-- Name: idx_asig_doc_personal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asig_doc_personal ON public.asignacion_docente USING btree (id_personal);


--
-- Name: idx_dg_ano_lectivo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dg_ano_lectivo ON public.direcciones_grupo USING btree (ano_lectivo);


--
-- Name: idx_dg_personal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dg_personal ON public.direcciones_grupo USING btree (id_personal);


--
-- Name: idx_plan_grado; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plan_grado ON public.plan_estudio USING btree (id_grado);


--
-- Name: idx_sector_municipio; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sector_municipio ON public.sectores USING btree (id_municipio);


--
-- Name: idx_sector_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sector_nombre ON public.sectores USING btree (nombre_sector);


--
-- Name: uk_sector; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uk_sector ON public.sectores USING btree (id_municipio, nombre_sector, tipo);


--
-- Name: acudientes acudientes_id_departamento_nacimiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acudientes
    ADD CONSTRAINT acudientes_id_departamento_nacimiento_fkey FOREIGN KEY (id_departamento_nacimiento) REFERENCES public.departamentos(id_departamento);


--
-- Name: acudientes acudientes_id_municipio_nacimiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acudientes
    ADD CONSTRAINT acudientes_id_municipio_nacimiento_fkey FOREIGN KEY (id_municipio_nacimiento) REFERENCES public.municipios(id_municipio);


--
-- Name: acudientes acudientes_id_sector_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acudientes
    ADD CONSTRAINT acudientes_id_sector_fkey FOREIGN KEY (id_sector) REFERENCES public.sectores(id_sector);


--
-- Name: acudientes acudientes_id_tipo_documento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acudientes
    ADD CONSTRAINT acudientes_id_tipo_documento_fkey FOREIGN KEY (id_tipo_documento) REFERENCES public.tipos_documento(id_tipo_documento);


--
-- Name: asignacion_docente asignacion_docente_id_asignatura_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_docente
    ADD CONSTRAINT asignacion_docente_id_asignatura_fkey FOREIGN KEY (id_asignatura) REFERENCES public.asignaturas(id_asignatura);


--
-- Name: asignacion_docente asignacion_docente_id_curso_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_docente
    ADD CONSTRAINT asignacion_docente_id_curso_fkey FOREIGN KEY (id_curso) REFERENCES public.cursos(id_curso);


--
-- Name: asignacion_docente asignacion_docente_id_personal_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_docente
    ADD CONSTRAINT asignacion_docente_id_personal_fkey FOREIGN KEY (id_personal) REFERENCES public.personal(id_personal);


--
-- Name: boletin_datos boletin_datos_id_matricula_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.boletin_datos
    ADD CONSTRAINT boletin_datos_id_matricula_fkey FOREIGN KEY (id_matricula) REFERENCES public.matriculas(id_matricula) ON DELETE CASCADE;


--
-- Name: calificaciones calificaciones_id_asignatura_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calificaciones
    ADD CONSTRAINT calificaciones_id_asignatura_fkey FOREIGN KEY (id_asignatura) REFERENCES public.asignaturas(id_asignatura) ON DELETE CASCADE;


--
-- Name: calificaciones calificaciones_id_matricula_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calificaciones
    ADD CONSTRAINT calificaciones_id_matricula_fkey FOREIGN KEY (id_matricula) REFERENCES public.matriculas(id_matricula) ON DELETE CASCADE;


--
-- Name: cursos cursos_id_grado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cursos
    ADD CONSTRAINT cursos_id_grado_fkey FOREIGN KEY (id_grado) REFERENCES public.grados(id_grado);


--
-- Name: cursos cursos_id_jornada_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cursos
    ADD CONSTRAINT cursos_id_jornada_fkey FOREIGN KEY (id_jornada) REFERENCES public.jornadas(id_jornada);


--
-- Name: cursos cursos_id_sede_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cursos
    ADD CONSTRAINT cursos_id_sede_fkey FOREIGN KEY (id_sede) REFERENCES public.sedes(id_sede);


--
-- Name: direcciones_grupo direcciones_grupo_id_curso_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direcciones_grupo
    ADD CONSTRAINT direcciones_grupo_id_curso_fkey FOREIGN KEY (id_curso) REFERENCES public.cursos(id_curso);


--
-- Name: direcciones_grupo direcciones_grupo_id_personal_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direcciones_grupo
    ADD CONSTRAINT direcciones_grupo_id_personal_fkey FOREIGN KEY (id_personal) REFERENCES public.personal(id_personal);


--
-- Name: estudiantes estudiantes_id_municipio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estudiantes
    ADD CONSTRAINT estudiantes_id_municipio_fkey FOREIGN KEY (id_municipio) REFERENCES public.municipios(id_municipio);


--
-- Name: estudiantes estudiantes_id_sector_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estudiantes
    ADD CONSTRAINT estudiantes_id_sector_fkey FOREIGN KEY (id_sector) REFERENCES public.sectores(id_sector);


--
-- Name: estudiantes_documentos fk_documento_estudiante; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estudiantes_documentos
    ADD CONSTRAINT fk_documento_estudiante FOREIGN KEY (id_estudiante) REFERENCES public.estudiantes(id_estudiante) ON DELETE CASCADE;


--
-- Name: documentos fk_documentos_estudiante; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documentos
    ADD CONSTRAINT fk_documentos_estudiante FOREIGN KEY (estudiante_id) REFERENCES public.estudiantes(id_estudiante);


--
-- Name: indicadores_desempeno fk_ind_grado; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicadores_desempeno
    ADD CONSTRAINT fk_ind_grado FOREIGN KEY (id_grado) REFERENCES public.grados(id_grado) ON DELETE CASCADE;


--
-- Name: instituciones fk_instituciones_departamento; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones
    ADD CONSTRAINT fk_instituciones_departamento FOREIGN KEY (id_departamento) REFERENCES public.departamentos(id_departamento);


--
-- Name: instituciones fk_instituciones_municipio; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones
    ADD CONSTRAINT fk_instituciones_municipio FOREIGN KEY (id_municipio) REFERENCES public.municipios(id_municipio);


--
-- Name: matriculas fk_matriculas_acudiente; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.matriculas
    ADD CONSTRAINT fk_matriculas_acudiente FOREIGN KEY (id_acudiente) REFERENCES public.acudientes(id_acudiente);


--
-- Name: municipios fk_municipio_departamento; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT fk_municipio_departamento FOREIGN KEY (id_departamento) REFERENCES public.departamentos(id_departamento);


--
-- Name: sectores fk_sector_municipio; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sectores
    ADD CONSTRAINT fk_sector_municipio FOREIGN KEY (id_municipio) REFERENCES public.municipios(id_municipio) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: indicadores_desempeno indicadores_desempeno_id_asignatura_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicadores_desempeno
    ADD CONSTRAINT indicadores_desempeno_id_asignatura_fkey FOREIGN KEY (id_asignatura) REFERENCES public.asignaturas(id_asignatura) ON DELETE CASCADE;


--
-- Name: jornadas jornadas_id_institucion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jornadas
    ADD CONSTRAINT jornadas_id_institucion_fkey FOREIGN KEY (id_institucion) REFERENCES public.instituciones(id_institucion);


--
-- Name: matriculas matriculas_id_curso_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.matriculas
    ADD CONSTRAINT matriculas_id_curso_fkey FOREIGN KEY (id_curso) REFERENCES public.cursos(id_curso);


--
-- Name: matriculas matriculas_id_estudiante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.matriculas
    ADD CONSTRAINT matriculas_id_estudiante_fkey FOREIGN KEY (id_estudiante) REFERENCES public.estudiantes(id_estudiante);


--
-- Name: matriculas matriculas_id_institucion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.matriculas
    ADD CONSTRAINT matriculas_id_institucion_fkey FOREIGN KEY (id_institucion) REFERENCES public.instituciones(id_institucion);


--
-- Name: plan_estudio plan_estudio_id_asignatura_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plan_estudio
    ADD CONSTRAINT plan_estudio_id_asignatura_fkey FOREIGN KEY (id_asignatura) REFERENCES public.asignaturas(id_asignatura);


--
-- Name: plan_estudio plan_estudio_id_grado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plan_estudio
    ADD CONSTRAINT plan_estudio_id_grado_fkey FOREIGN KEY (id_grado) REFERENCES public.grados(id_grado);


--
-- Name: sedes sedes_id_institucion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sedes
    ADD CONSTRAINT sedes_id_institucion_fkey FOREIGN KEY (id_institucion) REFERENCES public.instituciones(id_institucion);


--
-- PostgreSQL database dump complete
--

\unrestrict N7Csz7tLHqQynggNLE4aPbVcvwnpXPO1VVusXSWxbnkNqHnfzzkVN4zui3pCZ9F

