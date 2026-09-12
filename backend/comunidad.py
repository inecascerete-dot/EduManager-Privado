from backend.db_manager import obtener_conexion
# ==========================================
# 📑 SECCIÓN 1: ESTUDIANTES (18 Campos)
# ==========================================

def registrar_estudiante(
    id_estudiante, tipo_documento, numero_documento, lugar_expedicion, 
    fecha_nacimiento, genero, grupo_sanguineo_rh, eps, sisben_grupo, 
    caracterizacion_poblacional, direccion_residencia, barrio_vereda, 
    estrato, telefono_contacto, primer_apellido, segundo_apellido, 
    primer_nombre, segundo_nombre
):
    """Inserta un registro completo de estudiante en la base de datos."""
    con = obtener_conexion()
    if not con: return
    try:
        with con.cursor() as cursor:
            query = """
                INSERT INTO estudiantes (
                    id_estudiante, tipo_documento, numero_documento, lugar_expedicion, 
                    fecha_nacimiento, genero, grupo_sanguineo_rh, eps, sisben_grupo, 
                    caracterizacion_poblacional, direccion_residencia, barrio_vereda, 
                    estrato, telefono_contacto, primer_apellido, segundo_apellido, 
                    primer_nombre, segundo_nombre
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (
                id_estudiante, tipo_documento, numero_documento, lugar_expedicion, 
                fecha_nacimiento, genero, grupo_sanguineo_rh, eps, sisben_grupo, 
                caracterizacion_poblacional, direccion_residencia, barrio_vereda, 
                estrato, telefono_contacto, primer_apellido, segundo_apellido, 
                primer_nombre, segundo_nombre
            ))
            con.commit()
            print(f"🎉 ¡Éxito! Estudiante '{primer_nombre} {primer_apellido}' registrado.")
    except Exception as e:
        con.rollback()
        print(f"❌ Error en tabla estudiantes: {e}")
    finally:
        con.close()


def consultar_estudiante(id_estudiante):
    """Busca la ficha de un estudiante por su ID."""
    con = obtener_conexion()
    if not con: return
    try:
        with con.cursor() as cursor:
            query = "SELECT * FROM estudiantes WHERE id_estudiante = %s;"
            cursor.execute(query, (id_estudiante,))
            resultado = cursor.fetchone()
            print(f"\n--- 📋 FICHA DEL ESTUDIANTE ({id_estudiante}) ---")
            print(f"🔹 Datos: {resultado}" if resultado else f"🔍 No encontrado.")
            print("------------------------------------------------\n")
    except Exception as e:
        print(f"❌ Error al consultar estudiante: {e}")
    finally:
        con.close()


# ==========================================
# 🧑‍🏫 SECCIÓN 2: PERSONAL INSTITUCIONAL (13 Campos)
# ==========================================

def registrar_personal(
    id_personal, numero_documento, nombres, apellidos, telefono, 
    correo_electronico, rol, escalafon_grado, decreto_nombramiento, 
    tipo_vinculacion, foto_url, estado_laboral, fecha_estado_laboral
):
    """Inserta un docente, directivo o administrativo en la tabla personal."""
    con = obtener_conexion()
    if not con: return
    try:
        with con.cursor() as cursor:
            query = """
                INSERT INTO personal (
                    id_personal, numero_documento, nombres, apellidos, telefono, 
                    correo_electronico, rol, escalafon_grado, decreto_nombramiento, 
                    tipo_vinculacion, foto_url, estado_laboral, fecha_estado_laboral
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (
                id_personal, numero_documento, nombres, apellidos, telefono, 
                correo_electronico, rol, escalafon_grado, decreto_nombramiento, 
                tipo_vinculacion, foto_url, estado_laboral, fecha_estado_laboral
            ))
            con.commit()
            print(f"🎉 ¡Éxito! Miembro del personal '{nombres} {apellidos}' [{rol}] registrado con ID: {id_personal}.")
    except Exception as e:
        con.rollback()
        print(f"❌ Error en tabla personal: {e}")
    finally:
        con.close()


def consultar_personal(id_personal):
    """Busca un miembro del personal por su ID."""
    con = obtener_conexion()
    if not con: return
    try:
        with con.cursor() as cursor:
            query = "SELECT * FROM personal WHERE id_personal = %s;"
            cursor.execute(query, (id_personal,))
            resultado = cursor.fetchone()
            print(f"\n--- 🧑‍🏫 FICHA DE PERSONAL ({id_personal}) ---")
            print(f"🔹 Datos: {resultado}" if resultado else f"🔍 No encontrado.")
            print("------------------------------------------------\n")
    except Exception as e:
        print(f"❌ Error al consultar personal: {e}")
    finally:
        con.close()


# ==========================================
# 🧪 PRUEBAS DE EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    print("🚀 Operando Motor de Comunidad Académica (Estudiantes y Personal)...")
    
    # 📝 Prueba 1: Insertar un Estudiante
    registrar_estudiante(
        "EST-203", "TI", "1067000222", "Cereté", "2012-05-14", "Masculino", 
        "O+", "Mutual Ser", "A1", "Ninguna", "Calle Principal", "Cañito", 1, 
        "3001234567", "Pérez", "Ramos", "Juan", "Carlos"
    )
    
    # 📝 Prueba 2: Insertar un Docente/Coordinador en la tabla Personal
    registrar_personal(
        id_personal="PERS-001",
        numero_documento="78000111",
        nombres="María Eugenia",
        apellidos="Gómez Hoyos",
        telefono="3117654321",
        correo_electronico="maria.gomez@dica.edu.co",
        rol="Docente",                     # Aquí defines si es Docente, Coordinador, etc.
        escalafon_grado="2AM",
        decreto_nombramiento="Dec-1278",
        tipo_vinculacion="Propiedad",
        foto_url="avatar_maria.png",
        estado_laboral="Activo",
        fecha_estado_laboral="2026-01-15"
    )
    
    # 🔍 Consultas de Validación
    consultar_estudiante("EST-203")
    consultar_personal("PERS-001")