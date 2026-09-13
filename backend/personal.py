"""Interfaz de consulta y registro del personal institucional."""

import datetime
import os

import streamlit as st
from streamlit_searchbox import st_searchbox

from backend.form_navigation import activar_navegacion_enter
from backend.personal_db import (
    obtener_siguiente_codigo_personal,
    web_buscar_personal_dinamico,
    web_registrar_personal,
)


def mostrar_consulta_personal():
    st.title("🧑‍🏫 Ficha de Personal Institucional")

    if "data_personal" not in st.session_state:
        with st.spinner("Cargando registro de personal..."):
            st.session_state.data_personal = web_buscar_personal_dinamico()

    def buscar_personal(searchterm):
        if not searchterm:
            return []

        texto = searchterm.strip().lower()
        resultados = []
        st.session_state.personal_encontrado = {}

        for p in st.session_state.data_personal:
            id_p = str(p[0])
            num_doc = str(p[1])
            nombres = str(p[2])
            apellidos = str(p[3])
            nombre_completo = f"{nombres} {apellidos}"
            palabras = nombre_completo.lower().split()

            coincide_nombre = any(palabra.startswith(texto) for palabra in palabras)
            coincide_doc = num_doc.startswith(texto)
            coincide_codigo = id_p.lower().startswith(texto)

            if coincide_nombre or coincide_doc or coincide_codigo:
                etiqueta = (
                    f"{nombre_completo} - Doc: {num_doc} - Código: {id_p}"
                )
                resultados.append(etiqueta)
                st.session_state.personal_encontrado[etiqueta] = p

        return resultados[:20]

    seleccion = st_searchbox(
        buscar_personal,
        placeholder="Escriba nombre, apellido, documento o código...",
        label="Buscar funcionario",
        key="buscar_funcionario",
    )

    if seleccion:
        resultado_per = st.session_state.personal_encontrado.get(seleccion)
        if resultado_per:
            (
                id_p, num_doc, nombres, apellidos, tel, correo, cargo,
                escalafon, decreto, vinculacion, foto_url, estado_lab, f_estado
            ) = resultado_per

            nombre_funcionario = f"{nombres} {apellidos}".strip()
            st.markdown(f"## 🧑‍🏫 {nombre_funcionario}")
            st.markdown(f"**Código de Personal:** `{id_p}`")
            st.write("---")
            st.markdown("### 📋 Perfil e Identificación")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Documento de Identidad:** `{num_doc}`")
                st.markdown(f"**Cargo / Rol Institucional:** {cargo}")
            with col2:
                if foto_url and foto_url != "sin_foto.png":
                    try:
                        st.image(f"assets/{foto_url}", caption=f"Foto de {nombres}", width=180)
                    except Exception:
                        st.info(
                            f"📸 Archivo asignado: `{foto_url}` "
                            "(Falta cargar el archivo físico en el servidor)"
                        )
                else:
                    st.warning("👤 Este funcionario no tiene una fotografía registrada en el sistema.")

            st.write("---")
            st.markdown("### 💼 Situación Laboral y Estatuto")
            col3, col4 = st.columns(2)
            with col3:
                st.markdown(f"**Tipo de Vinculación:** {vinculacion}")
                st.markdown(f"**Decreto de Nombramiento:** {decreto}")
            with col4:
                st.markdown(f"**Grado de Escalafón:** `{escalafon}`")
                st.markdown(f"**Estado Laboral Actual:** `{estado_lab}` ({f_estado})")

            st.write("---")
            st.markdown("### 📞 Información de Contacto")
            col5, col6 = st.columns(2)
            with col5:
                st.markdown(f"**Teléfono / Celular:** {tel}")
            with col6:
                st.markdown(f"**Correo Electrónico:** {correo}")


def mostrar_formulario_personal():
    st.title("📝 Registro de Personal Institucional")
    st.write("Incorpore nuevos funcionarios al sistema. Las fotografías se guardarán automáticamente en el servidor.")

    st.markdown("### 📋 1. Datos de Identificación y Perfil")
    col1, col2 = st.columns(2)
    with col1:
        per_id = st.text_input(
            "Código Interno Único (Ej: PERS-0001)*",
            value=obtener_siguiente_codigo_personal(),
            disabled=True,
        )
        per_nombres = st.text_input("Nombres Completos*")
        per_rol = st.selectbox("Cargo / Rol Institucional*", ["Docente de Aula", "Coordinador", "Rector", "Orientador", "Administrativo"])
    with col2:
        per_doc = st.text_input("Número de Documento*")
        per_apellidos = st.text_input("Apellidos Completos*")

    st.write("---")
    st.markdown("### 📞 2. Información de Contacto")
    col5, col6 = st.columns(2)
    with col5:
        per_tel = st.text_input("Teléfono / Celular de Contacto*")
    with col6:
        per_correo = st.text_input("Correo Electrónico*")

    st.write("---")
    st.markdown("### 📸 3. Gestión de Fotografía")
    archivo_foto = st.file_uploader(
        "Subir foto de perfil del docente/directivo (Formatos JPG, PNG)",
        type=["jpg", "jpeg", "png"],
    )
    foto_url_valor = "sin_foto.png"
    if archivo_foto is not None:
        extension = archivo_foto.name.split(".")[-1]
        foto_url_valor = f"{per_id.strip()}_foto.{extension}"

    st.write("---")
    st.markdown("### 💼 4. Situación Laboral y Estatuto Docente")
    fila_a_col1, fila_a_col2 = st.columns(2)
    with fila_a_col1:
        per_vinculacion = st.selectbox("Tipo de Vinculación*", ["-", "Propiedad", "Provisionalidad", "Período de Prueba", "Contratación"])
    with fila_a_col2:
        per_decreto = st.selectbox("Decreto de Nombramiento*", ["-", "Decreto 1278 (Estatuto Nuevo)", "Decreto 2277 (Estatuto Antiguo)", "Otro / Administrativo"])

    fila_b_col1, fila_b_col2 = st.columns(2)
    with fila_b_col1:
        if "-" in per_decreto:
            opciones_escalafon = ["Debe seleccionar un decreto primero"]
        elif "1278" in per_decreto:
            opciones_escalafon = ["-", "1A", "1B", "1C", "1D", "2A", "2B", "2C", "2D", "3A", "3B", "3C", "3D"]
        elif "2277" in per_decreto:
            opciones_escalafon = ["-"] + [f"Categoría {i}" for i in range(1, 15)]
        else:
            opciones_escalafon = ["No Aplica"]
        per_escalafon = st.selectbox("Grado de Escalafón*", opciones_escalafon)

    with fila_b_col2:
        per_estado = st.selectbox("Estado Laboral Actual*", ["-", "Activo", "Inactivo", "Licencia", "Comisión"])

    fila_c_col1, _ = st.columns(2)
    with fila_c_col1:
        per_f_estado = st.date_input("Fecha de Cambio de Estado", value=datetime.date.today())

    st.write("---")
    boton_guardar_per = st.button("💾 Guardar Registro Personal", use_container_width=True)
    activar_navegacion_enter([
        "Código Interno Único", "Número de Documento", "Nombres Completos",
        "Apellidos Completos", "Cargo / Rol Institucional",
        "Teléfono / Celular de Contacto", "Correo Electrónico",
        "Tipo de Vinculación", "Decreto de Nombramiento", "Grado de Escalafón",
        "Estado Laboral Actual", "Fecha de Cambio de Estado",
    ])

    if boton_guardar_per:
        id_p_l = per_id.strip()
        doc_l = per_doc.strip()
        nom_l = per_nombres.strip()
        ape_l = per_apellidos.strip()
        tel_l = per_tel.strip()
        correo_l = per_correo.strip()

        if not (id_p_l and doc_l and nom_l and ape_l and tel_l and correo_l):
            st.error("❌ Por favor, diligencie todos los campos obligatorios de texto (Campos con asterisco *).")
        elif per_vinculacion == "-" or per_decreto == "-" or per_escalafon == "-" or per_estado == "-":
            st.error("❌ Error por omisión: Debe seleccionar una opción válida en los menús de la Situación Laboral.")
        elif per_escalafon == "Debe seleccionar un decreto primero":
            st.error("❌ Por favor, asigne un Decreto de Nombramiento válido.")
        else:
            with st.spinner("Registrando funcionario y guardando archivos..."):
                if archivo_foto is not None:
                    os.makedirs("assets", exist_ok=True)
                    ruta_destino = os.path.join("assets", foto_url_valor)
                    with open(ruta_destino, "wb") as f:
                        f.write(archivo_foto.getbuffer())

                exito, mensaje = web_registrar_personal(
                    id_p_l, doc_l, nom_l, ape_l, tel_l, correo_l,
                    per_rol, per_escalafon, per_decreto, per_vinculacion,
                    per_estado, per_f_estado, foto_url_valor,
                )

            if exito:
                st.success(f"✅ {mensaje}")
                st.balloons()
            else:
                st.error(f"❌ {mensaje}")
