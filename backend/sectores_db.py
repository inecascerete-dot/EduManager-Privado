from backend.db_manager import obtener_conexion_directa


def web_registrar_sector(
    id_municipio,
    nombre_sector,
    tipo,
    observacion=""
):
    con = obtener_conexion_directa()

    if not con:
        return False, "No fue posible conectar con la base de datos."

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                INSERT INTO sectores
                (
                    id_municipio,
                    nombre_sector,
                    tipo,
                    observacion
                )
                VALUES
                (%s,%s,%s,%s);
                """,
                (
                    id_municipio,
                    nombre_sector.upper().strip(),
                    tipo,
                    observacion.strip()
                )
            )

        con.commit()

        return True, "Sector registrado correctamente."

    except Exception as e:

        con.rollback()

        return False, str(e)

    finally:

        con.close()


def web_buscar_sectores(id_municipio):

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
                WHERE id_municipio=%s
                ORDER BY nombre_sector;
                """,
                (id_municipio,)
            )

            return cur.fetchall()

    except Exception:

        return []

    finally:

        con.close()


def web_consultar_sector(id_sector):

    con = obtener_conexion_directa()

    if not con:
        return None

    try:

        with con.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM sectores
                WHERE id_sector=%s;
                """,
                (id_sector,)
            )

            return cur.fetchone()

    except Exception:

        return None

    finally:

        con.close()