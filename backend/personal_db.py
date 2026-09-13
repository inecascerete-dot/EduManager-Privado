"""Acceso a datos y operaciones PostgreSQL relacionadas con el personal."""

from psycopg2 import errors
import streamlit as st

from backend.db_manager import obtener_conexion_directa


def web_consultar_personal(id_funcionario):
    con = obtener_conexion_directa()
    if not con:
        return None
    try:
        with con.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id_personal, numero_documento, nombres, apellidos, telefono,
                    correo_electronico, cargo, escalafon_grado, decreto_nombramiento,
                    tipo_vinculacion, foto_url, estado_laboral, fecha_estado_laboral
                FROM personal
                WHERE id_personal = %s;
            """, (id_funcionario,))
            return cursor.fetchone()
    except Exception as e:
        st.error(f"Error al consultar personal: {e}")
        return None
    finally:
        con.close()


def web_buscar_personal_dinamico():
    con = obtener_conexion_directa()
    if not con:
        return []
    try:
        with con.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id_personal, numero_documento, nombres, apellidos, telefono,
                    correo_electronico, cargo, escalafon_grado, decreto_nombramiento,
                    tipo_vinculacion, foto_url, estado_laboral, fecha_estado_laboral
                FROM personal
                ORDER BY apellidos, nombres;
            """)
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Error al cargar personal: {e}")
        return []
    finally:
        con.close()


def obtener_siguiente_codigo_personal():
    """Genera el siguiente código consecutivo con formato PERS-0001."""
    con = obtener_conexion_directa()
    if not con:
        return "PERS-0001"

    try:
        with con.cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(
                    MAX(
                        CAST(
                            SUBSTRING(id_personal FROM '^PERS-([0-9]+)$')
                            AS INTEGER
                        )
                    ),
                    0
                ) + 1
                FROM personal
                WHERE id_personal ~* '^PERS-[0-9]+$';
            """)
            consecutivo = cursor.fetchone()[0]
            return f"PERS-{consecutivo:04d}"
    except Exception:
        return "PERS-0001"
    finally:
        con.close()


def web_registrar_personal(
        id_p, num_doc, nombres, apellidos, telefono, correo,
        rol, escalafon, decreto, vinculacion, estado, f_estado, foto_url):
    con = obtener_conexion_directa()
    if not con:
        return False, "No fue posible establecer conexión con la base de datos."
    try:
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO personal (
                    id_personal, numero_documento, nombres, apellidos, telefono,
                    correo_electronico, rol, escalafon_grado, decreto_nombramiento,
                    tipo_vinculacion, estado_laboral, fecha_estado_laboral, foto_url
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (id_p, num_doc, nombres, apellidos, telefono, correo,
                  rol, escalafon, decreto, vinculacion, estado, f_estado, foto_url))
            con.commit()
            return True, f"Personal '{nombres} {apellidos}' registrado exitosamente."
    except errors.UniqueViolation:
        con.rollback()
        return False, f"Ya existe un funcionario con el código '{id_p}'."
    except Exception as e:
        con.rollback()
        return False, f"Error inesperado: {e}"
    finally:
        con.close()


def web_obtener_personal_activo():
    """Retorna personal activo para usarlo en selectboxes y asignaciones."""
    con = obtener_conexion_directa()
    if not con:
        return []
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT id_personal,
                       nombres || ' ' || apellidos AS nombre_completo,
                       cargo
                FROM personal
                WHERE estado_laboral = 'Activo' OR estado_laboral IS NULL
                ORDER BY apellidos, nombres;
            """)
            return cur.fetchall()
    except Exception as e:
        st.error(f"Error al cargar personal: {e}")
        return []
    finally:
        con.close()
