from psycopg2 import errors
from backend.db_manager import obtener_conexion_directa

def web_consultar_matricula(id_estudiante):
    con = obtener_conexion_directa()
    if not con:
        return None
    try:
        with con.cursor() as cursor:
            query = """
                SELECT
                    id_matricula, id_estudiante, id_acudiente, folio_matricula, ano_lectivo,
                    sede, jornada, estado, id_curso, id_institucion, observaciones
                FROM matriculas
                WHERE id_estudiante = %s;
            """
            cursor.execute(query, (id_estudiante,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error al consultar la matrícula: {e}")
        return None
    finally:
        con.close()

def web_consultar_matricula_por_ano(id_estudiante, ano_lectivo):
    """
    Consulta si un estudiante ya tiene una matrícula registrada
    para un año lectivo específico.

    Retorna un diccionario con los datos de la matrícula si existe.
    Retorna None si no existe.
    """
    con = obtener_conexion_directa()

    if not con:
        return None

    try:
        with con.cursor() as cursor:
            query = """
                SELECT
                    m.id_matricula,
                    m.id_estudiante,
                    m.id_acudiente,
                    m.folio_matricula,
                    m.ano_lectivo,
                    m.sede,
                    m.jornada,
                    m.estado,
                    m.id_curso,
                    m.id_institucion,
                    m.observaciones,
                    COALESCE(g.nombre_grado, '—') AS nombre_grado,
                    COALESCE(c.grupo, '—') AS grupo
                FROM matriculas m
                LEFT JOIN cursos c
                    ON c.id_curso = m.id_curso
                LEFT JOIN grados g
                    ON g.id_grado = c.id_grado
                WHERE m.id_estudiante = %s
                  AND m.ano_lectivo = %s
                ORDER BY m.id_matricula DESC
                LIMIT 1;
            """

            cursor.execute(
                query,
                (id_estudiante, ano_lectivo)
            )

            fila = cursor.fetchone()

            if not fila:
                return None

            return {
                "id_matricula": fila[0],
                "id_estudiante": fila[1],
                "id_acudiente": fila[2],
                "folio": fila[3],
                "ano_lectivo": fila[4],
                "sede": fila[5],
                "jornada": fila[6],
                "estado": fila[7],
                "id_curso": fila[8],
                "id_institucion": fila[9],
                "observaciones": fila[10],
                "grado": fila[11],
                "grupo": fila[12]
            }

    except Exception as e:
        print(f"Error consultando matrícula por año: {e}")
        return None

    finally:
        con.close()

def web_generar_folio_matricula(ano):
    con = obtener_conexion_directa()
    if not con:
        return None
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT generar_folio_matricula(%s)", (ano,))
            resultado = cursor.fetchone()
            return resultado[0]
    except Exception as e:
        print(f"Error generando folio: {e}")
        return None
    finally:
        con.close()


def web_registrar_matricula(
        id_est, id_acu, folio, ano, fecha_mat, parentesco,
        sede, jornada, estado, curso, institucion, observaciones=None):
    con = obtener_conexion_directa()
    if not con:
        return False, "No fue posible establecer conexión con la base de datos."
    try:
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO matriculas (
                    id_estudiante, id_acudiente, folio_matricula, ano_lectivo,
                    fecha_matricula, parentesco, sede, jornada, estado, id_curso, id_institucion, observaciones
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                id_est, id_acu, folio, ano, fecha_mat,
                parentesco, sede, jornada, estado, curso, institucion, observaciones
            ))
            con.commit()
            return True, "Matrícula registrada exitosamente."
    except errors.ForeignKeyViolation as e:
        con.rollback()
        err = str(e)
        if "id_estudiante" in err:
            return False, "El estudiante seleccionado no existe en el sistema."
        elif "id_acudiente" in err:
            return False, "El acudiente seleccionado no existe en el sistema."
        elif "id_curso" in err:
            return False, "El curso seleccionado no existe."
        else:
            return False, "Datos relacionados no encontrados."
    except errors.UniqueViolation as e:
        con.rollback()
        constraint = e.diag.constraint_name or ""
        if "folio" in constraint:
            return False, "El número de folio ya está registrado."
        elif "id_estudiante" in constraint:
            return False, "El estudiante ya tiene una matrícula registrada."
        else:
            return False, f"Dato duplicado: {constraint}"
    except errors.NotNullViolation:
        con.rollback()
        return False, "Hay campos obligatorios sin diligenciar."
    except Exception as e:
        con.rollback()
        return False, f"Error inesperado: {e}"
    finally:
        con.close()


def web_buscar_matriculas(ano_lectivo=None, id_curso=None, estado=None):
    """Retorna lista de matrículas con datos del estudiante, filtradas por año/curso/estado."""
    con = obtener_conexion_directa()
    if not con:
        return []
    try:
        condiciones = []
        params = []
        if ano_lectivo:
            condiciones.append("m.ano_lectivo = %s")
            params.append(ano_lectivo)
        if id_curso:
            condiciones.append("m.id_curso = %s")
            params.append(id_curso)
        if estado:
            condiciones.append("m.estado = %s")
            params.append(estado)
        where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
        with con.cursor() as cur:
            cur.execute(f"""
                SELECT m.id_matricula,
                       m.folio_matricula,
                       m.ano_lectivo,
                       m.estado,
                       m.id_curso,
                       COALESCE(g.nombre_grado, '—') AS nombre_grado,
                       COALESCE(c.grupo, '—')        AS grupo,
                       m.id_estudiante,
                       CONCAT_WS(' ',
                           e.primer_nombre, e.segundo_nombre,
                           e.primer_apellido, e.segundo_apellido
                       )                             AS nombre_estudiante,
                       e.foto_url,                   -- <--- Aquí usamos foto_url
                       m.sede,
                       m.jornada,
                       m.fecha_matricula,
                       m.observaciones
                FROM matriculas m
                LEFT JOIN cursos    c ON c.id_curso    = m.id_curso
                LEFT JOIN grados    g ON g.id_grado    = c.id_grado
                LEFT JOIN estudiantes e ON e.id_estudiante = m.id_estudiante
                {where}
                ORDER BY m.ano_lectivo DESC, g.id_grado, c.grupo, e.primer_apellido;
            """, params)
            cols = [
                "id_matricula", "folio", "ano_lectivo", "estado",
                "id_curso", "nombre_grado", "grupo", "id_estudiante",
                "nombre_estudiante", "foto_url", "sede", "jornada", "fecha_matricula", "observaciones"
            ]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        return []
    finally:
        con.close()


def web_actualizar_estado_matricula(id_matricula, nuevo_estado, observaciones=None):
    """Cambia el estado y las observaciones de una matrícula. Retorna (bool, mensaje)."""
    estados_validos = {"Matriculado", "Inscrito", "Trasladado", "Retirado", "Anulado"}
    if nuevo_estado not in estados_validos:
        return False, f"Estado '{nuevo_estado}' no es válido."
    con = obtener_conexion_directa()
    if not con:
        return False, "No fue posible establecer conexion con la base de datos."
    try:
        with con.cursor() as cur:
            cur.execute("""
                UPDATE matriculas
                SET estado = %s, observaciones = %s
                WHERE id_matricula = %s;
            """, (nuevo_estado, observaciones, id_matricula))
            actualizados = cur.rowcount
        con.commit()
        if actualizados:
            return True, f"Matrícula #{id_matricula} actualizada a '{nuevo_estado}'."
        return False, f"No se encontró matrícula con ID {id_matricula}."
    except Exception as e:
        con.rollback()
        return False, f"Error al actualizar: {e}"
    finally:
        con.close()


def web_obtener_matriculas_activas_curso(id_curso, ano_lectivo):
    """Lista de (id_matricula, nombre_completo) para el curso/año, orden alfabético."""
    con = obtener_conexion_directa()
    if not con:
        return []
    try:
        with con.cursor() as cur:
            cur.execute(
                """
                SELECT m.id_matricula,
                       e.primer_nombre || ' ' || COALESCE(e.segundo_nombre,'') || ' ' ||
                       e.primer_apellido || ' ' || COALESCE(e.segundo_apellido,'') AS nombre
                FROM matriculas m
                JOIN estudiantes e ON e.id_estudiante = m.id_estudiante
                WHERE m.id_curso=%s AND m.ano_lectivo=%s AND m.estado='ACTIVO'
                ORDER BY e.primer_apellido, e.primer_nombre;
                """,
                (id_curso, ano_lectivo)
            )
            return [(r[0], r[1].strip()) for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        con.close()