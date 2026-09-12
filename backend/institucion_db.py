
import streamlit as st
from backend.db_manager import (
    obtener_conexion_directa
)



def web_obtener_institucion(id_inst="INST-DICA"):
    """
    Devuelve un diccionario con todos los campos de la institución,
    incluyendo los IDs y los nombres del departamento y municipio.
    """

    con = obtener_conexion_directa()

    if not con:
        return None

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT
                    i.id_institucion,
                    i.nit_dane,
                    i.nombre_institucion,
                    i.resolucion_aprobacion,
                    i.mision,
                    i.vision,
                    i.logo_url,
                    i.direccion_principal,
                    i.telefono_principal,

                    i.id_municipio,
                    m.nombre AS municipio,

                    i.id_departamento,
                    d.nombre AS departamento,

                    i.email_institucional,
                    i.nombre_rector,
                    i.correo_rector,
                    i.eslogan,
                    i.escudo_url

                FROM instituciones i

                LEFT JOIN departamentos d
                    ON d.id_departamento = i.id_departamento

                LEFT JOIN municipios m
                    ON m.id_municipio = i.id_municipio

                WHERE i.id_institucion = %s;
                """,
                (id_inst,)
            )

            row = cur.fetchone()

            if not row:
                return None

            columnas = [
                "id_institucion",
                "nit_dane",
                "nombre_institucion",
                "resolucion_aprobacion",
                "mision",
                "vision",
                "logo_url",
                "direccion_principal",
                "telefono_principal",

                "id_municipio",
                "municipio",

                "id_departamento",
                "departamento",

                "email_institucional",
                "nombre_rector",
                "correo_rector",
                "eslogan",
                "escudo_url"
            ]

            return dict(zip(columnas, row))

    except Exception as e:

        st.error(
            f"Error al leer institución: {e}"
        )

        return None

    finally:

        con.close()

def web_actualizar_institucion(
    id_inst,
    nombre,
    nit,
    resolucion,
    direccion,
    telefono,
    id_municipio,
    id_departamento,
    email,
    rector,
    correo_rector,
    mision,
    vision,
    logo_url,
    eslogan="",
    escudo_url=""
):
    """
    Actualiza todos los campos de la institución.

    Municipio y departamento se almacenan mediante sus IDs
    correspondientes a los catálogos:
        - id_departamento
        - id_municipio

    Retorna:
        (True, mensaje) si la actualización fue exitosa.
        (False, mensaje) si ocurrió algún error.
    """

    con = obtener_conexion_directa()

    if not con:
        return False, "Sin conexión a la base de datos."

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                UPDATE instituciones
                SET
                    nombre_institucion = %s,
                    nit_dane = %s,
                    resolucion_aprobacion = %s,
                    direccion_principal = %s,
                    telefono_principal = %s,
                    id_municipio = %s,
                    id_departamento = %s,
                    email_institucional = %s,
                    nombre_rector = %s,
                    correo_rector = %s,
                    mision = %s,
                    vision = %s,
                    logo_url = %s,
                    eslogan = %s,
                    escudo_url = %s
                WHERE id_institucion = %s;
                """,
                (
                    nombre,
                    nit,
                    resolucion,
                    direccion,
                    telefono,
                    id_municipio,
                    id_departamento,
                    email,
                    rector,
                    correo_rector,
                    mision,
                    vision,
                    logo_url,
                    eslogan,
                    escudo_url,
                    id_inst
                )
            )

            actualizados = cur.rowcount

        con.commit()

        if actualizados:

            return (
                True,
                "Datos de la institución actualizados correctamente."
            )

        return (
            False,
            f"No se encontró la institución '{id_inst}'."
        )

    except Exception as e:

        con.rollback()

        return (
            False,
            f"Error al actualizar: {e}"
        )

    finally:

        con.close()
