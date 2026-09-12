from backend.db_manager import obtener_conexion_directa


def obtener_tipos_documento():

    con = obtener_conexion_directa()

    if not con:
        return []

    try:

        with con.cursor() as cur:

            cur.execute("""
                SELECT
                    id_tipo_documento,
                    codigo,
                    descripcion
                FROM tipos_documento
                ORDER BY descripcion;
            """)

            return cur.fetchall()

    finally:

        con.close()


def obtener_departamentos():

    con = obtener_conexion_directa()

    if not con:
        return []

    try:

        with con.cursor() as cur:

            cur.execute("""
                SELECT
                    id_departamento,
                    codigo_dane,
                    nombre
                FROM departamentos
                ORDER BY nombre;
            """)

            return cur.fetchall()

    finally:

        con.close()


def obtener_municipios(id_departamento):

    con = obtener_conexion_directa()

    if not con:
        return []

    try:

        with con.cursor() as cur:

            cur.execute("""
                SELECT
                    id_municipio,
                    codigo_dane,
                    nombre
                FROM municipios
                WHERE id_departamento=%s
                ORDER BY nombre;
            """, (id_departamento,))

            return cur.fetchall()

    finally:

        con.close()


def obtener_sectores():

    con = obtener_conexion_directa()

    if not con:
        return []

    try:

        with con.cursor() as cur:

            cur.execute("""
                SELECT
                    id_sector,
                    nombre_sector,
                    tipo
                FROM sectores
                ORDER BY nombre_sector;
            """)

            return cur.fetchall()

    finally:

        con.close()

import psycopg2 # O el conector que estés utilizando para PostgreSQL

def obtener_nombre_sector_por_id(id_sector):
    """
    Busca por debajo en la tabla de sectores el nombre correspondiente al ID,
    sin necesidad de que el usuario lo seleccione manualmente.
    """
    conexion = None
    cursor = None
    try:
        # Reemplaza esto con tu función real para conectar a la base de datos
        conexion = obtener_conexion_directa() 
        cursor = conexion.cursor()
        
        # Ajusta el nombre de la tabla ('sectores') y de la columna si tienen otro nombre en tu BD
        query = "SELECT nombre FROM sectores WHERE id = %s"
        cursor.execute(query, (id_sector,))
        resultado = cursor.fetchone()
        
        if resultado and resultado[0]:
            return resultado[0]
        return "—"
        
    except Exception as e:
        print(f"Error al buscar el nombre del sector: {e}")
        return "—"
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

def obtener_sectores_por_municipio(id_municipio):
    con = obtener_conexion_directa()

    if not con:
        return []

    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT
                    id_sector,
                    nombre_sector,
                    tipo
                FROM sectores
                WHERE id_municipio = %s
                ORDER BY nombre_sector;
            """, (id_municipio,))

            return cur.fetchall()

    finally:
        con.close()

def obtener_municipios_por_departamento(id_departamento):
    """
    Obtiene los municipios pertenecientes a un departamento.

    Función de compatibilidad para los módulos que utilizan
    el nombre obtener_municipios_por_departamento().
    """
    return obtener_municipios(id_departamento)