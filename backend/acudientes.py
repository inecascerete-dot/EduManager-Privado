import streamlit as st
import datetime

from streamlit_searchbox import st_searchbox
from backend.catalogos_db import (
    obtener_tipos_documento,
    obtener_departamentos,
    obtener_municipios,
    obtener_sectores
)
from backend.acudientes_db import (
    web_registrar_acudiente,
    web_consultar_acudiente_por_documento,
    web_buscar_acudiente_dinamico,
    web_actualizar_acudiente,
    obtener_siguiente_codigo_acudiente,
    web_obtener_acudidos_por_acudiente,
    web_obtener_documentos_acudiente,
    web_guardar_documento_acudiente
)

def cargar_catalogos_acudiente(id_departamento=None):
    """Carga todos los catálogos utilizados por el módulo de acudientes."""
    tipos_documento = obtener_tipos_documento()
    departamentos = obtener_departamentos()
    sectores = obtener_sectores()
    municipios = []

    if id_departamento:
        municipios = obtener_municipios(id_departamento)

    return {
        "tipos_documento": tipos_documento,
        "departamentos": departamentos,
        "municipios": municipios,
        "sectores": sectores
    }

def limpiar_formulario_acudiente():
    """Limpia todos los campos del formulario asignando valores vacíos a sus keys de sesión"""
    st.session_state["reg_acu_tipo_doc"] = None
    st.session_state["reg_acu_num_doc"] = ""
    st.session_state["reg_acu_pnom"] = ""
    st.session_state["reg_acu_snom"] = ""
    st.session_state["reg_acu_pap"] = ""
    st.session_state["reg_acu_sap"] = ""
    st.session_state["reg_acu_fecha"] = None
    st.session_state["reg_acu_depto"] = None
    st.session_state["reg_acu_municipio"] = None
    st.session_state["reg_acu_tel"] = ""
    st.session_state["reg_acu_dir"] = ""
    st.session_state["reg_acu_sector"] = None
    st.session_state["reg_acu_correo"] = ""
    st.session_state["reg_acu_ocupacion"] = ""
    st.session_state["reg_acu_obs"] = ""
    st.session_state["reg_acu_id_real"] = obtener_siguiente_codigo_acudiente()
    st.session_state.pop("acudiente_actual", None)
    st.session_state.pop("nuevo_acudiente", None)
    st.session_state.pop("modo_edicion", None)

def cargar_acudiente_en_session(acudiente):
    """Carga los datos de la tupla de la BD en las variables de sesión del formulario."""
    if not acudiente:
        return
    st.session_state["reg_acu_id_real"] = acudiente[0]
    st.session_state["reg_acu_num_doc"] = acudiente[2] or ""
    st.session_state["reg_acu_pnom"] = acudiente[3] or ""
    st.session_state["reg_acu_snom"] = acudiente[4] or ""
    st.session_state["reg_acu_pap"] = acudiente[5] or ""
    st.session_state["reg_acu_sap"] = acudiente[6] or ""
    
    if acudiente[7]:
        st.session_state["reg_acu_fecha"] = acudiente[7] if isinstance(acudiente[7], datetime.date) else datetime.date.fromisoformat(str(acudiente[7]))
    else:
        st.session_state["reg_acu_fecha"] = None

    st.session_state["reg_acu_tel"] = acudiente[10] or ""
    st.session_state["reg_acu_correo"] = acudiente[11] or ""
    st.session_state["reg_acu_ocupacion"] = acudiente[12] or ""
    st.session_state["reg_acu_dir"] = acudiente[14] or ""
    st.session_state["reg_acu_obs"] = acudiente[15] or ""

    catalogos = cargar_catalogos_acudiente(acudiente[8])

    for t in catalogos["tipos_documento"]:
        if t[0] == acudiente[1]:
            st.session_state["reg_acu_tipo_doc"] = t
            break

    for d in catalogos["departamentos"]:
        if d[0] == acudiente[8]:
            st.session_state["reg_acu_depto"] = d
            break

    st.session_state["reg_acu_municipio"] = None
    if acudiente[8]:
        municipios = obtener_municipios(acudiente[8])
        for m in municipios:
            if m[0] == acudiente[9]:
                st.session_state["reg_acu_municipio"] = m
                break

    for s in catalogos["sectores"]:
        if s[0] == acudiente[13]:
            st.session_state["reg_acu_sector"] = s
            break

def mostrar_formulario_acudiente(modo="nuevo"):
    """
    Interfaz de registro, consulta o edición de acudientes dentro de la pestaña Datos.
    """
    is_nuevo = (modo == "nuevo")
    edit_mode = st.session_state.get("modo_edicion", is_nuevo)

    if is_nuevo:
        st.title("📝 Registro de Nuevo Acudiente")
        st.write("Complete la información del padre, madre o tutor responsable.")
    else:
        st.title("👨‍👩‍👧 Información del Acudiente")

    acu_id = st.session_state.get("reg_acu_id_real", obtener_siguiente_codigo_acudiente())
    st.info(f"**Código Interno Asignado:** {acu_id}")

    # === BOTONES DE ACCIÓN (UBICADOS ARRIBA PARA EVITAR CONFLICTOS DE ESTADO) ===
    st.write("---")
    if is_nuevo:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 Guardar Nuevo Acudiente", use_container_width=True, type="primary"):
                guardar_acudiente_formulario()
        with col_b2:
            if st.button("❌ Cancelar Registro", use_container_width=True):
                limpiar_formulario_acudiente()
                st.rerun()
    else:
        if not edit_mode:
            if st.button("✏️ Editar Acudiente", use_container_width=True, type="secondary"):
                st.session_state["modo_edicion"] = True
                st.rerun()
        else:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
                    actualizar_acudiente_formulario()
            with col_b2:
                if st.button("❌ Cancelar Edición", use_container_width=True):
                    st.session_state["modo_edicion"] = False
                    if "acudiente_actual" in st.session_state:
                        cargar_acudiente_en_session(st.session_state["acudiente_actual"])
                    st.rerun()
    st.write("---")

    catalogos = cargar_catalogos_acudiente(
        st.session_state["reg_acu_depto"][0] if st.session_state.get("reg_acu_depto") else None
    )

    # === BLOQUE 1: IDENTIFICACIÓN ===
    st.markdown("### 📋 1. Identificación")
    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            "Tipo de documento*",
            options=catalogos["tipos_documento"],
            format_func=lambda x: f"{x[1]} - {x[2]}",
            index=None if not st.session_state.get("reg_acu_tipo_doc") else catalogos["tipos_documento"].index(st.session_state["reg_acu_tipo_doc"]) if st.session_state["reg_acu_tipo_doc"] in catalogos["tipos_documento"] else None,
            placeholder="Seleccione tipo de documento...",
            key="reg_acu_tipo_doc",
            disabled=not edit_mode
        )

    with col2:
        st.text_input(
            "Número de documento*",
            key="reg_acu_num_doc",
            placeholder="Ingrese número de documento...",
            disabled=not edit_mode
        )

    col3, col4 = st.columns(2)
    with col3:
        st.text_input("Primer nombre*", key="reg_acu_pnom", disabled=not edit_mode)
    with col4:
        st.text_input("Segundo nombre", key="reg_acu_snom", disabled=not edit_mode)

    col5, col6 = st.columns(2)
    with col5:
        st.text_input("Primer apellido*", key="reg_acu_pap", disabled=not edit_mode)
    with col6:
        st.text_input("Segundo apellido", key="reg_acu_sap", disabled=not edit_mode)

    min_date = datetime.date(1930, 1, 1)
    max_date = datetime.date.today()
    st.date_input(
        "Fecha de nacimiento*",
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY",
        key="reg_acu_fecha",
        disabled=not edit_mode
    )

    # Ubicación
    col7, col8 = st.columns(2)
    with col7:
        st.selectbox(
            "Departamento de nacimiento*",
            options=catalogos["departamentos"],
            format_func=lambda x: x[2],
            index=None if not st.session_state.get("reg_acu_depto") else catalogos["departamentos"].index(st.session_state["reg_acu_depto"]) if st.session_state["reg_acu_depto"] in catalogos["departamentos"] else None,
            placeholder="Seleccione departamento...",
            key="reg_acu_depto",
            disabled=not edit_mode
        )

    with col8:
        depto_actual = st.session_state.get("reg_acu_depto")
        if depto_actual:
            municipios = obtener_municipios(depto_actual[0])
            st.selectbox(
                "Municipio de nacimiento*",
                options=municipios,
                format_func=lambda x: x[2],
                index=None if not st.session_state.get("reg_acu_municipio") else municipios.index(st.session_state["reg_acu_municipio"]) if st.session_state["reg_acu_municipio"] in municipios else None,
                placeholder="Seleccione municipio...",
                key="reg_acu_municipio",
                disabled=not edit_mode
            )
        else:
            st.selectbox(
                "Municipio de nacimiento*",
                options=[],
                index=None,
                placeholder="Seleccione primero un departamento...",
                key="reg_acu_municipio_vacio",
                disabled=True
            )

    st.write("---")
    st.markdown("### 📞 2. Información de Contacto")

    col9, col10 = st.columns(2)
    with col9:
        st.text_input("Teléfono Principal*", key="reg_acu_tel", disabled=not edit_mode)
        st.text_input("Dirección de Residencia", key="reg_acu_dir", disabled=not edit_mode)

        st.selectbox(
            "Barrio / Vereda / Corregimiento*",
            options=catalogos["sectores"],
            format_func=lambda x: f"{x[1]} ({x[2]})",
            index=None if not st.session_state.get("reg_acu_sector") else catalogos["sectores"].index(st.session_state["reg_acu_sector"]) if st.session_state["reg_acu_sector"] in catalogos["sectores"] else None,
            placeholder="Seleccione un sector...",
            key="reg_acu_sector",
            disabled=not edit_mode
        )

    with col10:
        st.text_input("Correo Electrónico", key="reg_acu_correo", disabled=not edit_mode)
        st.text_input("Ocupación", key="reg_acu_ocupacion", disabled=not edit_mode)
        st.text_area("Observaciones", height=80, key="reg_acu_obs", disabled=not edit_mode)

    st.info("💡 El parentesco (mamá, papá, tío…) se registra en la matrícula, ya que puede cambiar cada año lectivo.")


def guardar_acudiente_formulario():
    tipo_doc = st.session_state.get("reg_acu_tipo_doc")
    doc_l = st.session_state.get("reg_acu_num_doc", "").strip()
    pnom_l = st.session_state.get("reg_acu_pnom", "").strip()
    pap_l = st.session_state.get("reg_acu_pap", "").strip()
    tel_l = st.session_state.get("reg_acu_tel", "").strip()
    depto = st.session_state.get("reg_acu_depto")
    muni = st.session_state.get("reg_acu_municipio")
    sector = st.session_state.get("reg_acu_sector")
    fecha_nac = st.session_state.get("reg_acu_fecha")

    if not (
        tipo_doc and doc_l and pnom_l and pap_l and tel_l
        and depto and muni and sector and fecha_nac
    ):
        st.error("❌ Por favor diligencie todos los campos obligatorios (*).")
        return

    with st.spinner("Registrando acudiente..."):
        exito, mensaje = web_registrar_acudiente(
            st.session_state["reg_acu_id_real"],
            tipo_doc[0],
            doc_l,
            pnom_l,
            st.session_state.get("reg_acu_snom", "").strip(),
            pap_l,
            st.session_state.get("reg_acu_sap", "").strip(),
            fecha_nac,
            depto[0],
            muni[0],
            tel_l,
            st.session_state.get("reg_acu_correo", "").strip(),
            st.session_state.get("reg_acu_ocupacion", "").strip(),
            sector[0],
            st.session_state.get("reg_acu_dir", "").strip(),
            st.session_state.get("reg_acu_obs", "").strip()
        )

    if exito:
        st.session_state["mensaje_exito"] = mensaje
        st.session_state.pop("data_acudientes", None)
        limpiar_formulario_acudiente()
        st.rerun()
    else:
        st.error(mensaje)


def actualizar_acudiente_formulario():
    tipo_doc = st.session_state.get("reg_acu_tipo_doc")
    doc_l = st.session_state.get("reg_acu_num_doc", "").strip()
    pnom_l = st.session_state.get("reg_acu_pnom", "").strip()
    pap_l = st.session_state.get("reg_acu_pap", "").strip()
    tel_l = st.session_state.get("reg_acu_tel", "").strip()
    depto = st.session_state.get("reg_acu_depto")
    muni = st.session_state.get("reg_acu_municipio")
    sector = st.session_state.get("reg_acu_sector")
    fecha_nac = st.session_state.get("reg_acu_fecha")

    if not (
        tipo_doc and doc_l and pnom_l and pap_l and tel_l
        and depto and muni and sector and fecha_nac
    ):
        st.error("❌ Por favor complete todos los campos obligatorios (*).")
        return

    acu_id = st.session_state.get("reg_acu_id_real")

    with st.spinner("Actualizando acudiente..."):
        exito, mensaje = web_actualizar_acudiente(
            acu_id,
            tipo_doc[0],
            doc_l,
            pnom_l,
            st.session_state.get("reg_acu_snom", "").strip(),
            pap_l,
            st.session_state.get("reg_acu_sap", "").strip(),
            fecha_nac,
            depto[0],
            muni[0],
            tel_l,
            st.session_state.get("reg_acu_correo", "").strip(),
            st.session_state.get("reg_acu_ocupacion", "").strip(),
            sector[0],
            st.session_state.get("reg_acu_dir", "").strip(),
            st.session_state.get("reg_acu_obs", "").strip()
        )

    if exito:
        st.success(mensaje)
        

        # Limpiar caché
        st.session_state.pop("data_acudientes", None)

        # Salir del modo edición
        st.session_state["modo_edicion"] = False
        st.session_state["modo_edicion_acudiente"] = False

        # Consultar nuevamente el acudiente actualizado
        acudiente_fresco = web_consultar_acudiente_por_documento(doc_l)

        if acudiente_fresco:
            # Actualiza el formulario
            st.session_state["acudiente_actual"] = acudiente_fresco
            cargar_acudiente_en_session(acudiente_fresco)

            # ===== ACTUALIZA LA TARJETA DE MATRÍCULA =====
            st.session_state["mat_acu_data"] = acudiente_fresco

            nombre = (
                f"{acudiente_fresco[3]} "
                f"{acudiente_fresco[4]} "
                f"{acudiente_fresco[5]} "
                f"{acudiente_fresco[6]}"
            ).strip()

            st.session_state["mat_acu_nom"] = nombre

        st.balloons()
        st.rerun()
    else:
        st.error(mensaje)


def mostrar_acudientes():
    st.title("👨‍👩‍👧 Gestión de Acudientes")

    if 'mensaje_exito' in st.session_state:
        st.success(st.session_state['mensaje_exito'])
        st.balloons()
        del st.session_state['mensaje_exito']

    col1, col2 = st.columns([3, 1])

    with col1:
        if "data_acudientes" not in st.session_state:
            with st.spinner("Cargando base de datos de acudientes..."):
                st.session_state.data_acudientes = web_buscar_acudiente_dinamico("")

        if st.session_state.data_acudientes is not None:
            def buscar_acudientes(searchterm: str):
                if not searchterm:
                    return []

                texto = searchterm.strip().lower()
                resultados = []
                st.session_state.acudientes_encontrados = {}

                for r in st.session_state.data_acudientes:
                    codigo = str(r[0]).strip()
                    documento = str(r[2])
                    nombre = (
                        f"{r[5] or ''} {r[6] or ''} {r[3] or ''} {r[4] or ''}"
                    ).replace("  ", " ").strip()

                    palabras = nombre.lower().split()
                    coincide_nombre = any(palabra.startswith(texto) for palabra in palabras)
                    coincide_documento = documento.lower().startswith(texto)
                    coincide_codigo = codigo.lower().startswith(texto)

                    if coincide_nombre or coincide_documento or coincide_codigo:
                        etiqueta = f"Cod: {codigo} - {nombre} - Doc: {documento}"
                        resultados.append(etiqueta)
                        st.session_state.acudientes_encontrados[etiqueta] = r

                st.session_state["sin_resultados_acudiente"] = (len(texto) >= 3 and len(resultados) == 0)
                return resultados[:20]

            seleccion = st_searchbox(
                buscar_acudientes,
                placeholder="Escriba código, nombre, apellido o documento...",
                label="Buscar acudiente",
                key="buscar_acudiente"
            )

            if st.session_state.get("sin_resultados_acudiente", False):
                st.info("ℹ️ No existe ningún acudiente con ese criterio. Haga clic en ➕ Nuevo para registrarlo.")

            if seleccion:
                acudiente_busqueda = st.session_state.acudientes_encontrados.get(seleccion)
                if acudiente_busqueda:
                    acudiente_completo = web_consultar_acudiente_por_documento(acudiente_busqueda[2])
                    if acudiente_completo:
                        if "acudiente_actual" not in st.session_state or st.session_state.acudiente_actual[0] != acudiente_completo[0]:
                            st.session_state["acudiente_actual"] = acudiente_completo
                            st.session_state["nuevo_acudiente"] = False
                            st.session_state["modo_edicion"] = False
                            cargar_acudiente_en_session(acudiente_completo)
                            st.rerun()

    with col2:
        if st.button("➕ Nuevo", use_container_width=True):
            limpiar_formulario_acudiente()
            st.session_state["nuevo_acudiente"] = True
            st.session_state["modo_edicion"] = True
            st.rerun()

    st.write("---")

    # === SISTEMA DE PESTAÑAS ===
    tab_datos, tab_acudidos, tab_documentos = st.tabs([
        "📋 Datos",
        "👨‍🎓 Acudidos",
        "📄 Documentos"
    ])

    with tab_datos:
        if st.session_state.get("nuevo_acudiente", False):
            mostrar_formulario_acudiente(modo="nuevo")
        elif "acudiente_actual" in st.session_state and st.session_state["acudiente_actual"]:
            mostrar_formulario_acudiente(modo="consulta")
        else:
            st.info("🔍 Busque un acudiente en la parte superior o haga clic en el botón ➕ Nuevo para registrar uno nuevo.")

    with tab_acudidos:
        st.markdown("### 👨‍🎓 Alumnos a su cargo")
        acudiente_actual = st.session_state.get("acudiente_actual")
        
        if not acudiente_actual:
            st.warning("⚠️ Primero debe seleccionar o buscar un acudiente.")
        else:
            id_acu = acudiente_actual[0] # id_acudiente
            estudiantes = web_obtener_acudidos_por_acudiente(id_acu)
            
            if not estudiantes:
                st.info("ℹ️ Este acudiente no tiene estudiantes registrados a su cargo actualmente.")
            else:
                for est in estudiantes:
                    with st.container(border=True):
                        col_f, col_i = st.columns([1, 6])
                        with col_f:
                            foto_url = est[6] # foto_url
                            # Usamos el conversor seguro de Drive
                            if foto_url and "drive.google.com" in foto_url:
                                try:
                                    file_id = foto_url.split("/file/d/")[1].split("/")[0] if "/file/d/" in foto_url else foto_url.split("id=")[1].split("&")[0]
                                    foto_url = f"https://lh3.googleusercontent.com/d/{file_id}"
                                except Exception:
                                    pass
                            
                            if foto_url and foto_url.startswith("http"):
                                try:
                                    st.image(foto_url, width=55)
                                except Exception:
                                    st.markdown("👤")
                            else:
                                st.markdown("<div style='font-size: 30px; text-align: center;'>👤</div>", unsafe_allow_html=True)
                                
                        with col_i:
                            nombre_est = f"{est[2] or ''} {est[3] or ''} {est[4] or ''} {est[5] or ''}".strip()
                            parentesco = est[8] or "No especificado"
                            ano_lectivo = est[9] or "Actual"
                            
                            st.markdown(f"**{nombre_est}**")
                            st.caption(f"Documento: `{est[1]}` | Grado: **{est[7]}** | Parentesco: **{parentesco}** (Año: {ano_lectivo})")

    with tab_documentos:
        st.markdown("### 📄 Documentos del Acudiente")
        
        # 1. Obtenemos el ID del acudiente actual de manera segura
        id_acudiente_actual = st.session_state.get("acudiente_actual")
        if isinstance(id_acudiente_actual, (list, tuple)):
            id_acu = id_acudiente_actual[0]
        else:
            id_acu = id_acudiente_actual

        if not id_acu:
            st.warning("⚠️ Primero debe seleccionar o buscar un acudiente.")
        else:
            # 2. SECCIÓN DE LISTADO (Igual que en estudiantes)
            st.markdown("#### 📁 Documentos registrados")
            documentos = web_obtener_documentos_acudiente(id_acu)
            
            if documentos:
                for doc in documentos:
                    # Estructura devuelta: id, tipo_documento, nombre_archivo, drive_file_id, url, fecha_subida
                    doc_id, tipo, nombre_archivo, drive_id, url, fecha = doc
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        col1.markdown(f"📄 **{tipo}**")
                        col2.caption(f"Archivo: {nombre_archivo}\nSubido: {str(fecha)[:16]}")
                        if url:
                            col3.link_button("Ver archivo 🔗", url, use_container_width=True)
            else:
                st.info("📁 Este acudiente no tiene documentos cargados todavía.")

            st.divider()

            # 3. SECCIÓN DEL FORMULARIO DE SUBIDA
            st.markdown("#### 📤 Subir nuevo documento")
            with st.form(key="form_subir_doc_acudiente", clear_on_submit=True):
                nombre_doc_input = st.text_input("Nombre o tipo de documento (ej. Cédula, Residencia)")
                archivo_subido = st.file_uploader("Seleccionar archivo (PDF o Imagen)", type=["pdf", "png", "jpg", "jpeg"])
                
                subir_btn = st.form_submit_button("Subir documento", type="primary")
                if subir_btn:
                    if archivo_subido and nombre_doc_input:
                        with st.spinner("Subiendo a Google Drive y guardando en la base de datos..."):
                            exito, mensaje = web_guardar_documento_acudiente(
                                id_acudiente=id_acu,
                                tipo_documento=nombre_doc_input,
                                archivo_subido=archivo_subido
                            )
                            if exito:
                                st.success(f"✅ {mensaje}")
                                st.rerun()
                            else:
                                st.error(f"❌ {mensaje}")
                    else:
                        st.warning("⚠️ Por favor ingrese el tipo de documento y seleccione un archivo.")