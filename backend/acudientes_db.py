from psycopg2 import errors

from backend.db_manager import obtener_conexion_directa



def web_consultar_acudiente(id_acudiente):
    con = obtener_conexion_directa()
    if not con:
        return None

    try:
        with con.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id_acudiente,
                    id_tipo_documento,
                    numero_documento,
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido,
                    fecha_nacimiento,
                    id_departamento_nacimiento,
                    id_municipio_nacimiento,
                    telefono_principal,
                    correo_electronico,
                    ocupacion,
                    id_sector,
                    direccion_residencia,
                    observaciones
                FROM acudientes
                WHERE id_acudiente = %s;
                """,
                (id_acudiente,)
            )

            return cursor.fetchone()

    except Exception:
        return None

    finally:
        con.close()


def web_buscar_acudiente_dinamico(termino=""):

    con = obtener_conexion_directa()

    if not con:
        return []

    try:

        with con.cursor() as cursor:

            if termino:

                cursor.execute(
                    """
                    SELECT
                        id_acudiente,
                        id_tipo_documento,
                        numero_documento,
                        primer_nombre,
                        segundo_nombre,
                        primer_apellido,
                        segundo_apellido,
                        fecha_nacimiento,
                        id_departamento_nacimiento,
                        id_municipio_nacimiento,
                        telefono_principal,
                        correo_electronico,
                        ocupacion,
                        id_sector,
                        direccion_residencia,
                        observaciones,
                        fecha_registro
                    FROM acudientes
                    WHERE
                        numero_documento ILIKE %s
                        OR primer_nombre ILIKE %s
                        OR segundo_nombre ILIKE %s
                        OR primer_apellido ILIKE %s
                        OR segundo_apellido ILIKE %s
                    ORDER BY
                        primer_apellido,
                        segundo_apellido,
                        primer_nombre,
                        segundo_nombre;
                    """,
                    (
                        f"%{termino}%",
                        f"%{termino}%",
                        f"%{termino}%",
                        f"%{termino}%",
                        f"%{termino}%"
                    )
                )

            else:

                cursor.execute(
                    """
                    SELECT
                        id_acudiente,
                        id_tipo_documento,
                        numero_documento,
                        primer_nombre,
                        segundo_nombre,
                        primer_apellido,
                        segundo_apellido,
                        fecha_nacimiento,
                        id_departamento_nacimiento,
                        id_municipio_nacimiento,
                        telefono_principal,
                        correo_electronico,
                        ocupacion,
                        id_sector,
                        direccion_residencia,
                        observaciones,
                        fecha_registro
                    FROM acudientes
                    """
                )

            return cursor.fetchall()
    except Exception as e:

        print(e)
        return []

    finally:

        con.close()
        
def web_registrar_acudiente(
    id_acu,
    id_tipo_documento,
    numero_documento,
    primer_nombre,
    segundo_nombre,
    primer_apellido,
    segundo_apellido,
    fecha_nacimiento,
    id_departamento,
    id_municipio,
    telefono,
    correo,
    ocupacion,
    id_sector,
    direccion,
    observaciones
):
    """
    Registra un acudiente.
    El parentesco se registra posteriormente en la matrícula.
    """

    con = obtener_conexion_directa()

    if not con:
        return False, "No fue posible establecer conexión con la base de datos."

    try:

        with con.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO acudientes
                (
                    id_acudiente,
                    id_tipo_documento,
                    numero_documento,
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido,
                    fecha_nacimiento,
                    id_departamento_nacimiento,
                    id_municipio_nacimiento,
                    telefono_principal,
                    correo_electronico,
                    ocupacion,
                    id_sector,
                    direccion_residencia,
                    observaciones
                )
                VALUES
                (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                );
                """,
                (
                    id_acu,
                    id_tipo_documento,
                    numero_documento,
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido,
                    fecha_nacimiento,
                    id_departamento,
                    id_municipio,
                    telefono,
                    correo,
                    ocupacion,
                    id_sector,
                    direccion,
                    observaciones
                )
            )

        con.commit()

        nombre_completo = (
            f"{primer_nombre} "
            f"{segundo_nombre or ''} "
            f"{primer_apellido} "
            f"{segundo_apellido or ''}"
        ).strip()

        return True, f"Acudiente '{nombre_completo}' registrado exitosamente."

    except errors.UniqueViolation:

        con.rollback()

        return False, (
            f"Ya existe un acudiente con el código "
            f"'{id_acu}' o con el documento '{numero_documento}'."
        )

    except errors.ForeignKeyViolation:

        con.rollback()

        return False, "Alguno de los catálogos seleccionados no existe."

    except Exception as e:

        con.rollback()

        return False, f"Error inesperado: {e}"

    finally:

        con.close()

def web_verificar_documento_acudiente(numero_documento):
    """
    Verifica si ya existe un acudiente registrado con el número de documento dado.
    Retorna True si existe, False en caso contrario.
    """
    con = obtener_conexion_directa()
    if not con:
        return False

    try:
        with con.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_acudiente 
                FROM acudientes 
                WHERE numero_documento = %s;
                """,
                (numero_documento.strip(),)
            )
            resultado = cursor.fetchone()
            return resultado is not None

    except Exception:
        return False

    finally:
        con.close()

def web_consultar_acudiente_por_documento(numero_documento):
    con = obtener_conexion_directa()
    if not con:
        return None

    try:
        with con.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id_acudiente,
                    id_tipo_documento,
                    numero_documento,
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido,
                    fecha_nacimiento,
                    id_departamento_nacimiento,
                    id_municipio_nacimiento,
                    telefono_principal,
                    correo_electronico,
                    ocupacion,
                    id_sector,
                    direccion_residencia,
                    observaciones
                FROM acudientes
                WHERE numero_documento = %s;
                """,
                (str(numero_documento).strip(),)
            )
            return cursor.fetchone()

    except Exception as e:
        print(f"Error consultando acudiente por documento: {e}") # Te ayudará a ver si ocurre otro detalle en consola
        return None

    finally:
        con.close()

def web_actualizar_acudiente(
    id_acu,
    id_tipo_documento,
    numero_documento,
    primer_nombre,
    segundo_nombre,
    primer_apellido,
    segundo_apellido,
    fecha_nacimiento,
    id_departamento,
    id_municipio,
    telefono,
    correo,
    ocupacion,
    id_sector,
    direccion,
    observaciones
):
    """
    Actualiza la información de un acudiente existente en la base de datos.
    """
    con = obtener_conexion_directa()

    if not con:
        return False, "No fue posible establecer conexión con la base de datos."

    try:
        with con.cursor() as cursor:
            cursor.execute(
                """
                UPDATE acudientes SET
                    id_tipo_documento = %s,
                    numero_documento = %s,
                    primer_nombre = %s,
                    segundo_nombre = %s,
                    primer_apellido = %s,
                    segundo_apellido = %s,
                    fecha_nacimiento = %s,
                    id_departamento_nacimiento = %s,
                    id_municipio_nacimiento = %s,
                    telefono_principal = %s,
                    correo_electronico = %s,
                    ocupacion = %s,
                    id_sector = %s,
                    direccion_residencia = %s,
                    observaciones = %s
                WHERE id_acudiente = %s;
                """,
                (
                    id_tipo_documento,
                    numero_documento,
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido,
                    fecha_nacimiento,
                    id_departamento,
                    id_municipio,
                    telefono,
                    correo,
                    ocupacion,
                    id_sector,
                    direccion,
                    observaciones,
                    id_acu
                )
            )

        con.commit()

        nombre_completo = (
            f"{primer_nombre} "
            f"{segundo_nombre or ''} "
            f"{primer_apellido} "
            f"{segundo_apellido or ''}"
        ).strip()

        return True, f"Acudiente '{nombre_completo}' actualizado exitosamente."

    except Exception as e:
        con.rollback()
        return False, f"Error al actualizar el acudiente: {e}"

    finally:
        con.close()

def obtener_siguiente_codigo_acudiente():

    con = obtener_conexion_directa()

    if not con:
        return "ACU-0001"

    try:

        with con.cursor() as cur:

            cur.execute("""
                SELECT
                    COALESCE(
                        MAX(
                            CAST(
                                REPLACE(id_acudiente,'ACU-','')
                                AS INTEGER
                            )
                        ),
                        0
                    ) + 1
                FROM acudientes;
            """)

            consecutivo = cur.fetchone()[0]

            return f"ACU-{consecutivo:04d}"

    except Exception:

        return "ACU-0001"

    finally:

        con.close()

def web_obtener_acudidos_por_acudiente(id_acudiente):
    con = obtener_conexion_directa()
    if not con:
        return []

    try:
        with con.cursor() as cursor:
            print(f"🔍 DEBUG: Buscando acudidos para el ID acudiente: repr('{id_acudiente}')")
            
            # Simplificamos la consulta para evitar errores de columnas de cursos si varían, 
            # trayendo la matrícula, el estudiante y el curso de forma segura.
            cursor.execute(
                """
                SELECT 
                    e.id_estudiante,
                    e.numero_documento,
                    e.primer_nombre,
                    e.segundo_nombre,
                    e.primer_apellido,
                    e.segundo_apellido,
                    e.foto_url,
                    COALESCE(m.id_curso, 'Sin asignar') AS grado_grupo,
                    m.parentesco,
                    m.ano_lectivo
                FROM matriculas m
                JOIN estudiantes e ON m.id_estudiante = e.id_estudiante
                WHERE TRIM(m.id_acudiente) = TRIM(%s);
                """,
                (str(id_acudiente),)
            )
            resultados = cursor.fetchall()
            print(f"🔍 DEBUG: Resultados encontrados: {len(resultados)}")
            return resultados
            
    except Exception as e:
        print(f"❌ Error al obtener acudidos desde matrículas: {e}")
        return []
    finally:
        con.close()


def web_obtener_documentos_acudiente(id_acudiente):
    print(f"🔍 DEBUG: Consultando documentos para el acudiente con ID: '{id_acudiente}' (Tipo: {type(id_acudiente)})")
    
    con = obtener_conexion_directa()
    if not con:
        print("❌ Error: No hay conexión a la base de datos.")
        return []
        
    try:
        with con.cursor() as cursor:
            # Hacemos la consulta asegurándonos de limpiar espacios en blanco por si acaso
            cursor.execute(
                """
                SELECT id, tipo_documento, nombre_archivo, drive_file_id, url, fecha_subida
                FROM documentos_acudientes
                WHERE TRIM(id_acudiente) = TRIM(%s)
                ORDER BY fecha_subida DESC;
                """,
                (str(id_acudiente),)
            )
            resultados = cursor.fetchall()
            print(f"📄 DEBUG: Se encontraron {len(resultados)} documentos.")
            return resultados
    except Exception as e:
        print(f"❌ Error consultando documentos del acudiente: {e}")
        return []
    finally:
        con.close()

def web_guardar_documento_acudiente(id_acudiente, tipo_documento, archivo_subido):
    """
    Sube un documento del acudiente a Google Drive (en su carpeta de ACUDIENTES)
    y guarda el registro en la tabla independiente documentos_acudientes.
    """
    if not archivo_subido:
        return False, "No se ha seleccionado ningún archivo."

    ruta_temporal = None
    try:
        from backend.drive_manager import DriveManager
        from tempfile import NamedTemporaryFile
        from pathlib import Path
        import os

        # 1. Instanciar el gestor de Drive
        dm = DriveManager()

        # 2. Obtener o crear la carpeta estructurada para el acudiente
        id_carpeta_destino = dm.obtener_carpeta_acudiente(id_acudiente)
        if not id_carpeta_destino:
            return False, "No se pudo crear o encontrar la carpeta en Google Drive."

        # 3. Manejar el archivo temporal
        extension = Path(archivo_subido.name).suffix
        nombre_original = archivo_subido.name
        
        with NamedTemporaryFile(delete=False, suffix=extension) as temp:
            temp.write(archivo_subido.getbuffer())
            ruta_temporal = temp.name

        # 4. Subir archivo usando el método de DriveManager
        archivo_info = dm.subir_archivo(ruta_temporal, nombre_original, id_carpeta_destino)
        
        if not archivo_info or "id" not in archivo_info:
            return False, "Error al subir el archivo a Google Drive."

        file_id = archivo_info["id"]
        url_archivo = archivo_info.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view?usp=drivesdk")

        # 5. Dar permisos públicos de lectura
        try:
            dm.service.permissions().create(
                fileId=file_id,
                body={
                    "type": "anyone",
                    "role": "reader"
                }
            ).execute()
        except Exception as e:
            print(f"⚠️ Aviso al otorgar permisos públicos: {e}")

        # 6. Registrar en la NUEVA tabla documentos_acudientes
        con = obtener_conexion_directa()
        if not con:
            return False, "Error de conexión a la base de datos."

        with con.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documentos_acudientes (
                    id_acudiente, 
                    tipo_documento, 
                    nombre_archivo, 
                    drive_file_id, 
                    url, 
                    id_carpeta, 
                    fecha_subida, 
                    subido_por
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, 'Sistema');
                """,
                (
                    id_acudiente, 
                    tipo_documento, 
                    nombre_original, 
                    file_id, 
                    url_archivo, 
                    id_carpeta_destino
                )
            )
            con.commit()
        con.close()

        return True, "¡Documento del acudiente subido y registrado exitosamente!"

    except Exception as e:
        print(f"❌ Error al guardar documento del acudiente: {e}")
        return False, f"Error técnico: {e}"
        
    finally:
        if ruta_temporal and os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
