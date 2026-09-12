from backend.db_manager import obtener_conexion_directa


def guardar_documento(
    id_estudiante,
    tipo_documento,
    nombre_archivo,
    drive_id,
    drive_url,
    carpeta_drive,
    usuario="Sistema",
    observaciones=""
):

    conn = obtener_conexion_directa()
    if not conn:
        raise RuntimeError("No fue posible conectar con la base de datos.")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documentos
                (
                    estudiante_id,
                    tipo_documento,
                    nombre_archivo,
                    drive_id,
                    drive_url,
                    carpeta_drive,
                    usuario,
                    observaciones
                )
                VALUES
                (
                    %s,%s,%s,%s,%s,%s,%s,%s
                )
                """,
                (
                    id_estudiante,
                    tipo_documento,
                    nombre_archivo,
                    drive_id,
                    drive_url,
                    carpeta_drive,
                    usuario,
                    observaciones
                )
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def obtener_documentos_estudiante(estudiante_id):

    conn = obtener_conexion_directa()
    if not conn:
        return []

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    tipo_documento,
                    nombre_archivo,
                    drive_url,
                    fecha_subida
                FROM documentos
                WHERE estudiante_id = %s
                ORDER BY fecha_subida DESC
                """,
                (estudiante_id,)
            )
            return cur.fetchall()
    finally:
        conn.close()
