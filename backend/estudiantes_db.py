"""
==========================================================
MÓDULO: ESTUDIANTES (Base de datos)
Autor: Proyecto EduManager
==========================================================

Todas las consultas SQL relacionadas con estudiantes
deben vivir aquí.

NOTA DE MIGRACIÓN:
- Se conserva temporalmente barrio_vereda para datos antiguos.
- Los nuevos registros utilizan:
    id_municipio
    id_sector
- Las dos columnas están relacionadas mediante FK con:
    municipios
    sectores
"""

import streamlit as st

from psycopg2 import errors

from backend.db_manager import obtener_conexion_directa


# ==========================================================
# BÚSQUEDA DE ESTUDIANTES
# ==========================================================

def web_buscar_estudiante_dinamico(termino=""):
    """
    Busca estudiantes por código, documento o nombres/apellidos.

    IMPORTANTE:
    id_municipio e id_sector se agregan AL FINAL del SELECT
    para no alterar los índices que actualmente utiliza
    el módulo de matrícula y otras partes del sistema.
    """

    con = obtener_conexion_directa()

    if not con:
        return []

    try:

        with con.cursor() as cur:

            query_base = """
                SELECT
                    id_estudiante,
                    tipo_documento,
                    numero_documento,
                    lugar_expedicion,
                    fecha_nacimiento,
                    genero,
                    grupo_sanguineo_rh,
                    eps,
                    sisben_grupo,
                    caracterizacion_poblacional,
                    direccion_residencia,
                    barrio_vereda,
                    estrato,
                    telefono_contacto,
                    primer_apellido,
                    segundo_apellido,
                    primer_nombre,
                    segundo_nombre,
                    foto_url,
                    id_municipio,
                    id_sector
                FROM estudiantes
            """

            if termino:

                query = query_base + """
                    WHERE id_estudiante ILIKE %s
                       OR numero_documento ILIKE %s
                       OR primer_apellido ILIKE %s
                       OR segundo_apellido ILIKE %s
                    ORDER BY primer_apellido, primer_nombre;
                """

                t = f"%{termino}%"

                cur.execute(
                    query,
                    (t, t, t, t)
                )

            else:

                query = query_base + """
                    ORDER BY primer_apellido, primer_nombre;
                """

                cur.execute(query)

            return cur.fetchall()

    except Exception as e:

        st.error(
            f"Error al consultar estudiantes: {e}"
        )

        return []

    finally:

        con.close()


# ==========================================================
# REGISTRAR ESTUDIANTE
# ==========================================================

def web_registrar_estudiante(
    id_est, tipo_doc, num_doc, lug_exp, f_nac, genero, rh, 
    eps, sisben, caract, direccion, estrato, tel, 
    p_ape, s_ape, p_nom, s_nom, foto_url, id_municipio, id_sector, barrio_vereda=""
):
    con = obtener_conexion_directa()
    if not con:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        with con.cursor() as cursor:
            # Depuración: miremos qué id_sector está llegando realmente
            print(f"DEBUG -> El id_sector recibido es: {repr(id_sector)}")

            if not barrio_vereda or barrio_vereda.strip() == "":
                nombre_sector_automatico = "—"
                if id_sector:
                    # OJO AQUÍ: Si tu columna ID de la tabla sectores se llama 'id_sector' 
                    # en lugar de solo 'id', cámbialo en la siguiente línea:
                    query_sector = "SELECT nombre_sector FROM sectores WHERE id_sector = %s"
                    
                    cursor.execute(query_sector, (id_sector,))
                    resultado_sector = cursor.fetchone()
                    
                    print(f"DEBUG -> Resultado de la consulta sector: {resultado_sector}")
                    
                    if resultado_sector and resultado_sector[0]:
                        nombre_sector_automatico = resultado_sector[0]
                
                barrio_vereda = nombre_sector_automatico

            print(f"DEBUG -> El texto final que se guardará en barrio_vereda es: {repr(barrio_vereda)}")

            query = """
                INSERT INTO estudiantes (
                    id_estudiante, tipo_documento, numero_documento, lugar_expedicion, 
                    fecha_nacimiento, genero, grupo_sanguineo_rh, eps, sisben_grupo, 
                    caracterizacion_poblacional, direccion_residencia, barrio_vereda, 
                    estrato, telefono_contacto, primer_apellido, segundo_apellido, 
                    primer_nombre, segundo_nombre, foto_url, id_municipio, id_sector
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                id_est, tipo_doc, num_doc, lug_exp, f_nac, genero, rh, 
                eps, sisben, caract, direccion, barrio_vereda, estrato, tel, 
                p_ape, s_ape, p_nom, s_nom, foto_url, id_municipio, id_sector
            ))
            con.commit()
            return True, "Estudiante registrado con éxito."
            
    except Exception as e:
        con.rollback()
        return False, f"Error al registrar: {e}"
        
    finally:
        con.close()


# ==========================================================
# ACTUALIZAR ESTUDIANTE
# ==========================================================

def web_actualizar_estudiante(
    id_est,
    tipo_doc,
    num_doc,
    lug_exp,
    f_nac,
    genero,
    rh,
    eps,
    sisben,
    caract,
    direccion,
    id_municipio,
    id_sector,
    estrato,
    telefono,
    p_ape,
    s_ape,
    p_nom,
    s_nom,
):
    """
    Actualiza un estudiante existente.

    La ubicación se actualiza mediante:
        id_municipio
        id_sector

    barrio_vereda no se modifica para los nuevos registros.
    """

    con = obtener_conexion_directa()

    if not con:

        return (
            False,
            "No fue posible establecer conexión "
            "con la base de datos."
        )

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                UPDATE estudiantes
                SET
                    tipo_documento = %s,
                    numero_documento = %s,
                    lugar_expedicion = %s,
                    fecha_nacimiento = %s,
                    genero = %s,
                    grupo_sanguineo_rh = %s,
                    eps = %s,
                    sisben_grupo = %s,
                    caracterizacion_poblacional = %s,
                    direccion_residencia = %s,
                    id_municipio = %s,
                    id_sector = %s,
                    estrato = %s,
                    telefono_contacto = %s,
                    primer_apellido = %s,
                    segundo_apellido = %s,
                    primer_nombre = %s,
                    segundo_nombre = %s
                WHERE id_estudiante = %s;
                """,
                (
                    tipo_doc,
                    num_doc,
                    lug_exp,
                    f_nac,
                    genero,
                    rh,
                    eps,
                    sisben,
                    caract,
                    direccion,
                    id_municipio,
                    id_sector,
                    estrato,
                    telefono,
                    p_ape,
                    s_ape,
                    p_nom,
                    s_nom,
                    id_est,
                )
            )

            actualizados = cur.rowcount

        con.commit()

        if actualizados:

            return (
                True,
                f"Datos de '{p_nom} {p_ape}' "
                f"actualizados correctamente."
            )

        return (
            False,
            f"No se encontró el estudiante '{id_est}'."
        )

    except errors.UniqueViolation:

        con.rollback()

        return (
            False,
            "Ya existe otro estudiante "
            "con ese número de documento."
        )

    except Exception as e:

        con.rollback()

        return (
            False,
            f"Error inesperado: {e}"
        )

    finally:

        con.close()


# ==========================================================
# ACTUALIZAR FOTO
# ==========================================================

def web_actualizar_foto_estudiante(
    id_est,
    foto_url
):
    """
    Actualiza o borra la foto_url de un estudiante.
    """

    con = obtener_conexion_directa()

    if not con:

        return (
            False,
            "Sin conexión."
        )

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                UPDATE estudiantes
                SET foto_url = %s
                WHERE id_estudiante = %s;
                """,
                (
                    foto_url,
                    id_est
                )
            )

            if cur.rowcount == 0:

                con.rollback()

                return (
                    False,
                    f"No se encontró el estudiante "
                    f"'{id_est}'."
                )

        con.commit()

        return (
            True,
            "Foto actualizada correctamente."
        )

    except Exception as e:

        con.rollback()

        return (
            False,
            f"Error: {e}"
        )

    finally:

        con.close()


# ==========================================================
# GENERAR CÓDIGO DE ESTUDIANTE
# ==========================================================

def web_generar_codigo_estudiante():
    """
    Genera el siguiente código consecutivo:

        EST-00001
        EST-00002
        EST-00003
        ...
    """

    con = obtener_conexion_directa()

    if not con:
        return None

    try:

        with con.cursor() as cursor:

            cursor.execute(
                """
                SELECT COALESCE(
                    MAX(
                        CAST(
                            SUBSTRING(
                                id_estudiante
                                FROM 'EST-([0-9]+)$'
                            )
                            AS INTEGER
                        )
                    ),
                    0
                )
                FROM estudiantes
                WHERE id_estudiante ~ '^EST-[0-9]+$';
                """
            )

            resultado = cursor.fetchone()

            ultimo_numero = (
                resultado[0]
                if resultado and resultado[0] is not None
                else 0
            )

            siguiente_numero = ultimo_numero + 1

            return f"EST-{siguiente_numero:05d}"

    except Exception as e:

        print(
            f"Error al generar código de estudiante: {e}"
        )

        return None

    finally:

        con.close()

# ==========================================================
# CONSULTAR ESTUDIANTE POR CÓDIGO
# ==========================================================

def web_consultar_estudiante(codigo):
    """
    Consulta un estudiante por código.

    id_municipio e id_sector se devuelven al final
    para mantener compatibles los índices existentes.
    """

    con = obtener_conexion_directa()

    if not con:

        return None

    try:

        with con.cursor() as cursor:

            codigo_limpio = (
                str(codigo)
                .strip()
                .upper()
            )

            query = """
                SELECT
                    id_estudiante,
                    tipo_documento,
                    numero_documento,
                    lugar_expedicion,
                    fecha_nacimiento,
                    genero,
                    grupo_sanguineo_rh,
                    eps,
                    sisben_grupo,
                    caracterizacion_poblacional,
                    direccion_residencia,
                    barrio_vereda,
                    estrato,
                    telefono_contacto,
                    primer_apellido,
                    segundo_apellido,
                    primer_nombre,
                    segundo_nombre,
                    foto_url,
                    id_municipio,
                    id_sector
                FROM estudiantes
                WHERE TRIM(id_estudiante) = %s;
            """

            cursor.execute(
                query,
                (codigo_limpio,)
            )

            return cursor.fetchone()

    except Exception as e:

        st.error(
            f"Error técnico en la base de datos: {e}"
        )

        return None

    finally:

        con.close()


# ==========================================================
# MUNICIPIOS POR DEPARTAMENTO
# ==========================================================

def web_obtener_municipios_por_departamento(
    id_departamento
):
    """
    Retorna:

        (
            id_municipio,
            codigo_dane,
            nombre
        )

    únicamente de un departamento.
    """

    if not id_departamento:

        return []

    con = obtener_conexion_directa()

    if not con:

        return []

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id_municipio,
                    codigo_dane,
                    nombre
                FROM municipios
                WHERE id_departamento = %s
                ORDER BY nombre;
                """,
                (id_departamento,)
            )

            return cur.fetchall()

    except Exception as e:

        st.error(
            f"Error cargando municipios: {e}"
        )

        return []

    finally:

        con.close()


# ==========================================================
# SECTORES POR MUNICIPIO
# ==========================================================

def web_obtener_sectores_por_municipio(
    id_municipio
):
    """
    Retorna los sectores pertenecientes
    exclusivamente al municipio indicado.

    Estructura:

        (
            id_sector,
            nombre_sector,
            tipo
        )
    """

    if not id_municipio:

        return []

    con = obtener_conexion_directa()

    if not con:

        return []

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id_sector,
                    nombre_sector,
                    tipo
                FROM sectores
                WHERE id_municipio = %s
                ORDER BY nombre_sector;
                """,
                (id_municipio,)
            )

            return cur.fetchall()

    except Exception as e:

        st.error(
            f"Error cargando sectores: {e}"
        )

        return []

    finally:

        con.close()


# ==========================================================
# CONSULTAR SECTOR
# ==========================================================

def web_consultar_sector(
    id_sector
):
    """
    Devuelve un sector específico.
    """

    if not id_sector:

        return None

    con = obtener_conexion_directa()

    if not con:

        return None

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id_sector,
                    id_municipio,
                    nombre_sector,
                    tipo,
                    observacion
                FROM sectores
                WHERE id_sector = %s;
                """,
                (id_sector,)
            )

            return cur.fetchone()

    except Exception:

        return None

    finally:

        con.close()


# ==========================================================
# UBICACIÓN DE LA INSTITUCIÓN
# ==========================================================

def web_obtener_ubicacion_institucion(
    id_institucion="INST-DICA"
):
    """
    Obtiene la ubicación institucional actual.

    Devuelve:

        {
            "id_departamento": ...,
            "id_municipio": ...
        }

    Esta función se utilizará posteriormente para que
    el formulario de estudiantes muestre por defecto
    la ubicación de la institución.

    No se fija Córdoba ni Cereté en el código.
    Se consulta la configuración real de la institución.
    """

    con = obtener_conexion_directa()

    if not con:

        return None

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id_departamento,
                    id_municipio
                FROM instituciones
                WHERE id_institucion = %s;
                """,
                (id_institucion,)
            )

            fila = cur.fetchone()

            if not fila:

                return None

            return {
                "id_departamento": fila[0],
                "id_municipio": fila[1],
            }

    except Exception as e:

        st.error(
            f"Error obteniendo ubicación institucional: {e}"
        )

        return None

    finally:

        con.close()


# ==========================================================
# OBTENER SECTOR CON SU MUNICIPIO
# ==========================================================

def web_consultar_sector_con_municipio(
    id_sector
):
    """
    Consulta un sector junto con el municipio al que pertenece.

    Útil para validar que el sector seleccionado corresponde
    realmente al municipio seleccionado.
    """

    if not id_sector:

        return None

    con = obtener_conexion_directa()

    if not con:

        return None

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    s.id_sector,
                    s.nombre_sector,
                    s.tipo,
                    s.id_municipio,
                    m.nombre AS municipio
                FROM sectores s
                LEFT JOIN municipios m
                    ON m.id_municipio = s.id_municipio
                WHERE s.id_sector = %s;
                """,
                (id_sector,)
            )

            return cur.fetchone()

    except Exception:

        return None

    finally:

        con.close()