"""
==========================================================
MÓDULO: ESTUDIANTES
Autor: Proyecto EduManager
==========================================================
"""

import streamlit as st
import datetime
import time
import os
import tempfile
import requests
import re
from io import BytesIO
import streamlit.components.v1 as components
from streamlit_searchbox import st_searchbox
from backend.matriculas_db import web_consultar_matricula
from backend.acudientes_db import web_consultar_acudiente
from backend.drive_manager import DriveManager
from backend.documentos_db import guardar_documento, obtener_documentos_estudiante

from backend.estudiantes_db import (
    web_generar_codigo_estudiante,
    web_registrar_estudiante,
    web_buscar_estudiante_dinamico,
    web_actualizar_estudiante,
    web_actualizar_foto_estudiante,
    web_consultar_estudiante,
    web_obtener_sectores_por_municipio
    )

from backend.catalogos_db import (
    obtener_departamentos,
    obtener_municipios,
    
)

from backend.utils import obtener_url_o_ruta_imagen


def _activar_enter_formulario_estudiante():
    """Permite avanzar con Enter por el orden visual/lógico del formulario."""
    components.html(
        """
        <script>
        (() => {
            // El orden del DOM no coincide siempre con el orden visual de
            // las columnas de Streamlit. Por eso se define explícitamente
            // la secuencia que debe seguir la tecla Enter.
            const ordenFormulario = [
                "Tipo de Documento",
                "Número de Documento",
                "Departamento de Expedición (Filtro)",
                "Municipio de Expedición",
                "Primer Apellido",
                "Segundo Apellido (Opcional)",
                "Primer Nombre",
                "Segundo Nombre (Opcional)",
                "Fecha de Nacimiento",
                "Género",
                "Dirección de Residencia",
                "Teléfono de Contacto",
                "Estrato Socioeconómico",
                "Departamento",
                "Municipio",
                "Barrio / Vereda",
                "Grupo Sanguíneo y RH",
                "Grupo Sisbén",
                "EPS Asignada",
                "Caracterización Poblacional"
            ];

            const selectorCampos = [
                "input[aria-label]:not([type='hidden']):not([type='file']):not([role='combobox'])",
                "input[data-testid='stDateInputField']",
                "textarea[aria-label]",
                "[role='combobox'][aria-label]"
            ].join(",");

            const obtenerRaiz = () => window.parent.document.querySelector(
                    "[data-testid='stAppViewContainer']"
                ) || window.parent.document.body;

            const normalizar = (texto) => (texto || "")
                .replaceAll("*", "")
                .split(" ")
                .filter(Boolean)
                .join(" ")
                .trim()
                .toLocaleLowerCase();

            const campoVisible = (campo) => {
                const rect = campo.getBoundingClientRect();
                return !campo.disabled && rect.width > 0 && rect.height > 0;
            };

            const camposVisibles = () => {
                const raiz = obtenerRaiz();

                return Array.from(raiz.querySelectorAll(selectorCampos)).filter((campo) => {
                    return campoVisible(campo);
                });
            };

            const buscarCampo = (etiqueta) => {
                const etiquetaNormalizada = normalizar(etiqueta);
                const candidatos = camposVisibles();
                const campoExacto = candidatos.find((campo) => {
                    const ariaLabel = normalizar(campo.getAttribute("aria-label"));
                    return ariaLabel === etiquetaNormalizada;
                });

                if (campoExacto) {
                    return campoExacto;
                }

                if (etiquetaNormalizada === "fecha de nacimiento") {
                    const campoFecha = candidatos.find((campo) =>
                        campo.getAttribute("data-testid") === "stDateInputField"
                    );
                    if (campoFecha) {
                        return campoFecha;
                    }
                }

                return candidatos.find((campo) => {
                    const ariaLabel = normalizar(campo.getAttribute("aria-label"));
                    return ariaLabel.startsWith(`${etiquetaNormalizada} `);
                });
            };

            const buscarSiguienteCampo = (posicionActual) => {
                for (let posicion = posicionActual + 1; posicion < ordenFormulario.length; posicion += 1) {
                    const siguiente = buscarCampo(ordenFormulario[posicion]);
                    if (siguiente) {
                        return siguiente;
                    }
                }
                return null;
            };

            const instalar = () => {
                ordenFormulario.forEach((etiqueta, posicion) => {
                    const campo = buscarCampo(etiqueta);
                    if (!campo) {
                        return;
                    }

                    if (campo.dataset.enterFormularioInstalado === "1") {
                        return;
                    }

                    campo.dataset.enterFormularioInstalado = "1";
                    campo.addEventListener("keydown", (evento) => {
                        if (evento.key !== "Enter") {
                            return;
                        }

                        // Si un campo opcional no está renderizado (por
                        // ejemplo, Barrio/Vereda sin sectores), se salta al
                        // siguiente campo disponible.
                        const siguiente = buscarSiguienteCampo(posicion);

                        if (!siguiente) {
                            return;
                        }

                        evento.preventDefault();
                        evento.stopPropagation();
                        siguiente.focus();
                        siguiente.scrollIntoView({block: "center", behavior: "smooth"});
                    }, true);
                });
            };

            instalar();
            const observador = new MutationObserver(instalar);
            observador.observe(window.parent.document.body, {
                childList: true,
                subtree: true
            });
            window.setTimeout(() => observador.disconnect(), 30000);
        })();
        </script>
        """,
        height=0,
    )

def limpiar_formulario_estudiante():
    """Limpia todos los campos del formulario y el buscador asignando valores vacíos a sus keys de sesión"""
    st.session_state["reg_est_tipo_doc"] = "TI"
    st.session_state["reg_est_num_doc"] = ""
    st.session_state["reg_est_lug_exp"] = ""
    st.session_state["reg_est_p_nom"] = ""
    st.session_state["reg_est_s_nom"] = ""
    st.session_state["reg_est_p_ape"] = ""
    st.session_state["reg_est_s_ape"] = ""
    st.session_state["reg_est_f_nac"] = datetime.date(2015, 1, 1)
    st.session_state["reg_est_gen"] = "Masculino"
    st.session_state["reg_est_rh"] = "O+"
    st.session_state["reg_est_eps"] = ""
    st.session_state["reg_est_sisben"] = ""
    st.session_state["reg_est_caract"] = "Ninguna"
    st.session_state["reg_est_dir"] = ""
    st.session_state["reg_est_barrio"] = ""
    st.session_state["reg_est_estrato"] = "1"
    st.session_state["reg_est_tel"] = ""
    st.session_state["reg_est_id_real"] = web_generar_codigo_estudiante()
    
    # Limpiar estados de control y selección anterior
    st.session_state.pop("estudiante_actual", None)
    st.session_state.pop("nuevo_estudiante", None)
    st.session_state.pop("modo_edicion_estudiante", None)
    st.session_state.pop("uploader_foto_registro_est", None)
    st.session_state.pop("buscar_estudiante", None)

    

def limpiar_estado_estudiantes():
    """
    Limpia completamente el estado temporal del módulo Estudiantes.
    Se utiliza al salir del módulo o al volver a entrar desde cero.
    """

    claves = [
        "estudiante_actual",
        "nuevo_estudiante",
        "modo_edicion_estudiante",
        "modo_edicion",
        "buscar_estudiante",
        "estudiantes_encontrados",
        "mensaje_exito_estudiante",
        "data_estudiantes",
        "mat_editando_est",
        "id_est_mat",
        "mat_est_data",
        "mat_est_nom",
        "refrescar_estudiante_matricula",
    ]

    for clave in claves:
        st.session_state.pop(clave, None)

    # Limpiar también los campos del formulario
    campos_formulario = [
        "reg_est_id_real",
        "reg_est_tipo_doc",
        "reg_est_num_doc",
        "reg_est_lug_exp",
        "reg_est_p_nom",
        "reg_est_s_nom",
        "reg_est_p_ape",
        "reg_est_s_ape",
        "reg_est_f_nac",
        "reg_est_gen",
        "reg_est_rh",
        "reg_est_eps",
        "reg_est_sisben",
        "reg_est_caract",
        "reg_est_dir",
        "reg_est_barrio",
        "reg_est_estrato",
        "reg_est_tel",
        "reg_est_id_departamento",
        "reg_est_id_municipio",
        "reg_est_id_sector",
        "reg_est_foto_url",
    ]

    for clave in campos_formulario:
        st.session_state.pop(clave, None)

def cargar_estudiante_en_session(est):
    """Carga los datos del estudiante de la BD en las variables de sesión del formulario."""
    if not est:
        return
    st.session_state["reg_est_id_real"] = est[0]
    st.session_state["reg_est_tipo_doc"] = est[1] or "TI"
    st.session_state["reg_est_num_doc"] = est[2] or ""
    st.session_state["reg_est_lug_exp"] = est[3] or ""
    
    if est[4]:
        st.session_state["reg_est_f_nac"] = est[4] if isinstance(est[4], datetime.date) else datetime.date.fromisoformat(str(est[4]))
    else:
        st.session_state["reg_est_f_nac"] = datetime.date(2015, 1, 1)

    st.session_state["reg_est_gen"] = est[5] or "Masculino"
    st.session_state["reg_est_rh"] = est[6] or "O+"
    st.session_state["reg_est_eps"] = est[7] or ""
    st.session_state["reg_est_sisben"] = est[8] or ""
    st.session_state["reg_est_caract"] = est[9] or "Ninguna"
    st.session_state["reg_est_dir"] = est[10] or ""
    st.session_state["reg_est_barrio"] = est[11] or ""
    st.session_state["reg_est_estrato"] = str(est[12]) if est[12] is not None else "1"
    st.session_state["reg_est_tel"] = est[13] or ""
    st.session_state["reg_est_p_ape"] = est[14] or ""
    st.session_state["reg_est_s_ape"] = est[15] or ""
    st.session_state["reg_est_p_nom"] = est[16] or ""
    st.session_state["reg_est_s_nom"] = est[17] or ""
    st.session_state["reg_est_foto_url"] = est[18] if len(est) > 18 else ""
    
    # CARGAR UBICACIÓN DESDE LA BD (Índices 19 y 20)[cite: 3]
    muni_db = est[19] if len(est) > 19 else None
    sector_db = est[20] if len(est) > 20 else None
    
    st.session_state["reg_est_id_municipio"] = muni_db
    st.session_state["reg_est_id_sector"] = sector_db
    
    # Asegurar que el sector guardado sea tratado como entero si existe
    if sector_db is not None:
        try:
            st.session_state["reg_est_id_sector"] = int(sector_db)
        except (TypeError, ValueError):
            pass
    
    # DERIVAR Y FIJAR EL DEPARTAMENTO CORRESPONDIENTE
    dep_db = 0
    if muni_db:
        departamentos = obtener_departamentos()
        for d in departamentos:
            munis_dep = obtener_municipios(d[0])
            if any(m[0] == muni_db for m in munis_dep):
                dep_db = d[0]
                break
    st.session_state["reg_est_id_departamento"] = dep_db

def mostrar_formulario_estudiante(modo="nuevo"):
    """
    Interfaz de registro, consulta o edición de estudiantes con botones de acción superiores.
    """
    is_nuevo = (modo == "nuevo")

    # 🔥 Blindaje definitivo: Si es nuevo y no hay código o el estado anterior estaba en falso, 
    # generamos uno fresco de la base de datos de inmediato.
    if is_nuevo:
        if "reg_est_id_real" not in st.session_state:
            st.session_state["reg_est_id_real"] = web_generar_codigo_estudiante()
        st.session_state["modo_edicion_estudiante"] = True

    edit_mode = st.session_state.get("modo_edicion_estudiante", is_nuevo)

    if is_nuevo:
        st.title("📝 Registro de Nuevo Estudiante")
        st.write("Complete la información para incorporar al estudiante al sistema institucional.")
    else:
        st.title("👤 Ficha del Estudiante")

    # 🔥 OBTENEMOS EL CÓDIGO ACTUAL EN SESIÓN
    est_id = st.session_state.get("reg_est_id_real")

    # 🔥 LA CORRECCIÓN: Si el código atascado es el EST-00223 (o está vacío), 
    # lo forzamos a que pida un código nuevo de inmediato a la base de datos.
    if not est_id or est_id == "EST-00223":
        est_id = web_generar_codigo_estudiante()
        st.session_state["reg_est_id_real"] = est_id

    st.info(f"**Código Interno Asignado:** {est_id}")

    # === BOTONES DE ACCIÓN (SUPERIORES) ===
    st.write("---")
    if is_nuevo:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 Guardar Nuevo Estudiante", use_container_width=True, type="primary"):
                guardar_estudiante_formulario()
        with col_b2:
            if st.button("❌ Cancelar Registro", use_container_width=True):
                limpiar_formulario_estudiante()
                st.rerun()
    else:
        if not edit_mode:
            if st.button("✏️ Editar Estudiante", use_container_width=True, type="secondary"):
                st.session_state["modo_edicion_estudiante"] = True
                st.rerun()
        else:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
                    actualizar_estudiante_formulario()
            with col_b2:
                if st.button("❌ Cancelar Edición", use_container_width=True):
                    st.session_state["modo_edicion_estudiante"] = False
                    if "estudiante_actual" in st.session_state:
                        cargar_estudiante_en_session(st.session_state["estudiante_actual"])
                    st.rerun()
    st.write("---")

    # === FOTOGRAFÍA Y DATOS PRINCIPALES (MODO VISTA) ===
    if not is_nuevo and not edit_mode:
        est = st.session_state.get("estudiante_actual")
        foto_est_url = est[18] if est and len(est) > 18 else None

        col_foto_e, col_datos_e = st.columns([1, 4])

        with col_foto_e:
            imagen_mostrada = False
            try:
                if foto_est_url:
                    foto_str = str(foto_est_url).strip()
                    
                    # 1. Si es un enlace de Google Drive, extraer el ID y convertir a enlace directo de visualización
                    if "drive.google.com" in foto_str:
                        try:
                            file_id = None
                            match_file = re.search(r'/file/d/([a-zA-Z0-9_-]+)', foto_str)
                            if match_file:
                                file_id = match_file.group(1)
                            else:
                                match_id = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', foto_str)
                                if match_id:
                                    file_id = match_id.group(1)
                            
                            if file_id:
                                url_directa = f"https://drive.google.com/uc?export=view&id={file_id}"
                                sep = "&" if "?" in url_directa else "?"
                                url_final = f"{url_directa}{sep}v={int(time.time())}"
                                
                                r = requests.get(url_final, timeout=5)
                                if r.status_code == 200 and len(r.content) > 1000:
                                    st.image(BytesIO(r.content), width=130)
                                    imagen_mostrada = True
                        except Exception:
                            pass
                    
                    # 2. Si no es Drive o falló, comprobar si es un archivo local en assets o ruta directa
                    if not imagen_mostrada:
                        ruta_local = foto_str
                        if not os.path.exists(ruta_local):
                            ruta_local = os.path.join("assets", os.path.basename(foto_str))
                        
                        if os.path.exists(ruta_local):
                            st.image(ruta_local, width=130)
                            imagen_mostrada = True
                        elif foto_str.startswith("http://") or foto_str.startswith("https://"):
                            try:
                                sep = "&" if "?" in foto_str else "?"
                                url_final = f"{foto_str}{sep}v={int(time.time())}"
                                r = requests.get(url_final, timeout=5)
                                if r.status_code == 200:
                                    st.image(BytesIO(r.content), width=130)
                                    imagen_mostrada = True
                            except Exception:
                                pass

                if not imagen_mostrada:
                    st.markdown(
                        "<div style='width:130px;height:160px;"
                        "border:2px dashed #ccc;"
                        "border-radius:8px;"
                        "display:flex;"
                        "align-items:center;"
                        "justify-content:center;"
                        "color:#aaa;"
                        "font-size:36px'>👤</div>",
                        unsafe_allow_html=True
                    )
                    st.caption("Sin foto")

            except Exception as e:
                st.caption(f"Error cargando foto: {e}")

        with col_datos_e:
            st.markdown(f"**Nombre Completo:** {est[16]} {est[17] or ''} {est[14]} {est[15] or ''}")
            st.markdown(f"**Documento:** {est[1]} - {est[2]}")
            st.markdown(f"**Teléfono:** {est[13]}")
            st.markdown(f"**Dirección:** {est[10]} ({est[11]})")

        st.write("---")
    # === BLOQUE 1: IDENTIFICACIÓN ===
    st.markdown("### 📋 1. Datos de Identificación")
    col1, col2 = st.columns(2)

    tipos_doc = ["TI", "RC", "CC", "NES", "PEP"]
    with col1:
        st.selectbox(
            "Tipo de Documento*",
            options=tipos_doc,
            index=tipos_doc.index(st.session_state.get("reg_est_tipo_doc", "TI")) if st.session_state.get("reg_est_tipo_doc") in tipos_doc else 0,
            key="reg_est_tipo_doc",
            disabled=not edit_mode
        )

    with col2:
        st.text_input(
            "Número de Documento*",
            key="reg_est_num_doc",
            placeholder="Ingrese número de documento...",
            disabled=not edit_mode
        )

    # -------------------------------------------------------------------------
    # MUNICIPIO DE EXPEDICIÓN CONTROLADO POR DEPARTAMENTO (EN CASCADA)
    # -------------------------------------------------------------------------
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        # Lista de departamentos de Colombia (puedes ajustar o usar tu función si ya la tienes)
        # Por defecto dejamos los principales y Córdoba de primero por tu ubicación
        lista_departamentos = ["Córdoba", "Antioquia", "Atlántico", "Bogotá D.C.", "Bolívar", "Cundinamarca", "Sucre", "Valle del Cauca"]
        
        dep_exp_visual = st.selectbox(
            "Departamento de Expedición (Filtro)*",
            options=lista_departamentos,
            key="reg_est_dep_exp_visual",
            disabled=not edit_mode
        )

    with col_exp2:
        # Filtrar municipios según el departamento seleccionado
        # Si tienes una función en tu backend, la usas aquí. Si no, usamos un diccionario rápido de respaldo:
        municipios_por_dep = {
            "Córdoba": ["Montería", "Lorica", "Cereté", "Sahagún", "Planeta Rica", "Montelíbano", "Tierralta", "San Antero", "Chinú", "Ayapel"],
            "Antioquia": ["Medellín", "Bello", "Itagüí", "Envigado", "Rionegro", "Apartadó"],
            "Sucre": ["Sincelejo", "Corozal", "San Marcos", "Tolú", "Sampués"],
            "Bolívar": ["Cartagena", "Magangué", "Turbaco", "Arjona"],
            "Atlántico": ["Barranquilla", "Soledad", "Malambo", "Puerto Colombia"],
            "Bogotá D.C.": ["Bogotá D.C."],
            "Cundinamarca": ["Soacha", "Facatativá", "Chía", "Zipaquirá", "Girardot"],
            "Valle del Cauca": ["Cali", "Buenaventura", "Palmira", "Tuluá", "Buga"]
        }
        
        lista_mun = municipios_por_dep.get(dep_exp_visual, ["Otro"])

        # Mantenemos exactamente la misma key "reg_est_lug_exp" para que tu base de datos reciba el valor sin modificar el backend
        st.selectbox(
            "Municipio de Expedición*",
            options=lista_mun,
            key="reg_est_lug_exp",
            disabled=not edit_mode
        )

    col_nom1, col_nom2 = st.columns(2)
    with col_nom1:
        st.text_input("Primer Apellido*", key="reg_est_p_ape", disabled=not edit_mode)
    with col_nom2:
        st.text_input("Segundo Apellido (Opcional)", key="reg_est_s_ape", disabled=not edit_mode)
       
    col_ape1, col_ape2 = st.columns(2)
    with col_ape1:
        st.text_input("Primer Nombre*", key="reg_est_p_nom", disabled=not edit_mode)
    with col_ape2:
        st.text_input("Segundo Nombre (Opcional)", key="reg_est_s_nom", disabled=not edit_mode) 

    if edit_mode:
        _activar_enter_formulario_estudiante()

    # === BLOQUE 2: SOCIODEMOGRÁFICA ===

    st.write("---")
    st.markdown("### 📍 2. Información Sociodemográfica y de Contacto")

    col5, col6 = st.columns(2)

    estratos = ["1", "2", "3", "4"]
    generos = ["Masculino", "Femenino", "Otro"]

    with col5:

        min_date = datetime.date(2000, 1, 1)
        max_date = datetime.date.today()

        st.date_input(
            "Fecha de Nacimiento",
            min_value=min_date,
            max_value=max_date,
            key="reg_est_f_nac",
            disabled=not edit_mode
        )

        st.text_input(
            "Dirección de Residencia*",
            key="reg_est_dir",
            disabled=not edit_mode
        )

        st.selectbox(
            "Estrato Socioeconómico*",
            options=estratos,
            index=(
                estratos.index(
                    str(
                        st.session_state.get(
                            "reg_est_estrato",
                            "1"
                        )
                    )
                )
                if str(
                    st.session_state.get(
                        "reg_est_estrato",
                        "1"
                    )
                ) in estratos
                else 0
            ),
            key="reg_est_estrato",
            disabled=not edit_mode
        )


    with col6:

        st.selectbox(
            "Género*",
            options=generos,
            index=(
                generos.index(
                    st.session_state.get(
                        "reg_est_gen",
                        "Masculino"
                    )
                )
                if st.session_state.get(
                    "reg_est_gen"
                ) in generos
                else 0
            ),
            key="reg_est_gen",
            disabled=not edit_mode
        )

        st.text_input(
            "Teléfono de Contacto*",
            key="reg_est_tel",
            disabled=not edit_mode
        )


    # ============================================================
    # UBICACIÓN DEL ESTUDIANTE
    # ============================================================

    st.write("---")
    st.markdown("### 📍 Ubicación de Residencia")

    # 1. CARGAR / ASEGURAR IDs DESDE EL ESTUDIANTE ACTUAL (Solo si no hay datos en sesión)
    if "estudiante_actual" in st.session_state and st.session_state["estudiante_actual"]:
        est_actual_tupla = st.session_state["estudiante_actual"]
        if not st.session_state.get("reg_est_id_municipio") or int(st.session_state.get("reg_est_id_municipio", 0)) == 0:
            if len(est_actual_tupla) > 19 and est_actual_tupla[19]:
                st.session_state["reg_est_id_municipio"] = est_actual_tupla[19]
        
        if not st.session_state.get("reg_est_id_sector"):
            if len(est_actual_tupla) > 20 and est_actual_tupla[20]:
                st.session_state["reg_est_id_sector"] = est_actual_tupla[20]

    # 2. Obtener departamentos
    departamentos = obtener_departamentos()
    opciones_departamentos = {d[0]: d[2] for d in departamentos}
    ids_departamentos = [0] + list(opciones_departamentos.keys())
    opciones_departamentos[0] = "Seleccione departamento"

    # Detectar el departamento anterior en sesión para saber si el usuario lo cambió
    dep_anterior = st.session_state.get("reg_est_id_departamento", 0)

    municipio_id_actual = st.session_state.get("reg_est_id_municipio", 0)
    
    # Derivar departamento si no está definido
    if (not dep_anterior or dep_anterior == 0) and municipio_id_actual:
        for d in departamentos:
            munis_dep = obtener_municipios(d[0])
            if any(m[0] == municipio_id_actual for m in munis_dep):
                dep_anterior = d[0]
                break
        st.session_state["reg_est_id_departamento"] = dep_anterior

    # Selector de Departamento
    st.selectbox(
        "Departamento*",
        options=ids_departamentos,
        format_func=lambda x: opciones_departamentos.get(x, "Seleccione departamento"),
        key="reg_est_id_departamento",
        disabled=not edit_mode
    )

    departamento_activo = st.session_state.get("reg_est_id_departamento", 0)

    # 3. CONTROL EN CASCADA: Si el usuario cambió de departamento en modo edición, limpiamos municipio y sector
    if edit_mode and dep_anterior != departamento_activo:
        st.session_state["reg_est_id_municipio"] = 0
        st.session_state["reg_est_id_sector"] = None
        municipio_id_actual = 0

    # ============================================================
    # MUNICIPIO
    # ============================================================
    municipios = obtener_municipios(departamento_activo) if departamento_activo and departamento_activo != 0 else []
    opciones_municipios = {0: "Seleccione municipio"}
    for m in municipios:
        opciones_municipios[m[0]] = m[2]
    ids_municipios = list(opciones_municipios.keys())

    # Si el municipio actual no pertenece al departamento activo, lo reseteamos a 0
    if municipio_id_actual not in ids_municipios:
        municipio_id_actual = 0
        st.session_state["reg_est_id_municipio"] = 0

    # Selector de Municipio
    st.selectbox(
        "Municipio*",
        options=ids_municipios,
        index=ids_municipios.index(municipio_id_actual) if municipio_id_actual in ids_municipios else 0,
        format_func=lambda x: opciones_municipios.get(x, "Seleccione municipio"),
        key="reg_est_id_municipio",
        disabled=not edit_mode
    )

    municipio_id = st.session_state.get("reg_est_id_municipio", 0)
    municipio_nombre = opciones_municipios.get(municipio_id, "")

    # ============================================================
    # SECTOR / BARRIO / VEREDA
    # ============================================================
    try:
        municipio_id_int = int(municipio_id) if municipio_id else 0
    except (TypeError, ValueError):
        municipio_id_int = 0

    sectores = []
    if municipio_id_int > 0:
        sectores = web_obtener_sectores_por_municipio(municipio_id_int)

    opciones_sectores = {
        s[0]: f"{s[1]} ({s[2]})"
        for s in sectores
    }
    ids_sectores = list(opciones_sectores.keys())

    # CAPTURAR EL PUENTE DEL NUEVO SECTOR ANTES DE CREAR EL WIDGET
    if "sector_recien_creado_id" in st.session_state:
        nuevo_id = st.session_state.pop("sector_recien_creado_id")
        if nuevo_id in ids_sectores:
            st.session_state["reg_est_id_sector"] = nuevo_id

    id_sector_en_sesion = st.session_state.get("reg_est_id_sector")
    try:
        id_sector_en_sesion = int(id_sector_en_sesion) if id_sector_en_sesion else None
    except (TypeError, ValueError):
        id_sector_en_sesion = None

    # Si el sector actual no pertenece a los sectores del municipio, lo limpiamos
    if id_sector_en_sesion not in ids_sectores:
        id_sector_en_sesion = None
        st.session_state["reg_est_id_sector"] = None

    if ids_sectores:
        indice_seleccionado = 0
        if id_sector_en_sesion in ids_sectores:
            indice_seleccionado = ids_sectores.index(id_sector_en_sesion)

        st.selectbox(
            "Barrio / Vereda*",
            options=ids_sectores,
            index=indice_seleccionado,
            format_func=lambda x: opciones_sectores[x],
            key="reg_est_id_sector",
            disabled=not edit_mode
        )
    else:
        st.session_state["reg_est_id_sector"] = None
        st.info("No hay barrios o veredas registrados para este municipio.")    
    # ============================================================
    # CREAR NUEVO SECTOR / VEREDA
    # ============================================================

    if edit_mode:

        if st.button(
            "➕ Registrar nuevo barrio / vereda",
            use_container_width=True,
            key="btn_nuevo_sector_estudiante"
        ):

            st.session_state[
                "mostrar_registro_sector_desde_estudiante"
            ] = True

            st.rerun()


    if st.session_state.get(
        "mostrar_registro_sector_desde_estudiante",
        False
    ):

        st.markdown("---")
        st.markdown(
            "### ➕ Registrar nuevo barrio / vereda"
        )

        st.info(
            f"Municipio: **{municipio_nombre}**"
        )

        nombre_nuevo_sector = st.text_input(
            "Nombre del barrio o vereda*",
            key="nuevo_sector_nombre_estudiante"
        )

        tipo_nuevo_sector = st.selectbox(
            "Tipo*",
            ["Barrio", "Vereda"],
            key="nuevo_sector_tipo_estudiante"
        )

        observacion_nuevo_sector = st.text_area(
            "Observación",
            key="nuevo_sector_observacion_estudiante"
        )

        col_sector1, col_sector2 = st.columns(2)

        with col_sector1:

            if st.button(
                "💾 Guardar sector",
                use_container_width=True,
                type="primary",
                key="guardar_sector_estudiante"
            ):

                nombre_limpio = (
                    nombre_nuevo_sector
                    or ""
                ).strip()

                if not nombre_limpio:

                    st.error(
                        "❌ Escriba el nombre del barrio "
                        "o vereda."
                    )

                else:

                    from backend.sectores_db import (
                        web_registrar_sector
                    )

                    ok_sector, mensaje_sector = (
                        web_registrar_sector(
                            municipio_id,
                            nombre_limpio,
                            tipo_nuevo_sector,
                            observacion_nuevo_sector
                        )
                    )

                    if ok_sector:

                        st.success("✅ Sector registrado correctamente.")

                        # Buscar el ID del sector recién creado
                        sectores_actualizados = web_obtener_sectores_por_municipio(municipio_id)
                        
                        if sectores_actualizados:
                            for s in sectores_actualizados:
                                if s[1].strip().lower() == nombre_limpio.lower():
                                    # GUARDAMOS EN LA VARIABLE PUENTE (No choca con ningún widget)
                                    st.session_state["sector_recien_creado_id"] = int(s[0])
                                    break
                            else:
                                ultimo_sector = max(sectores_actualizados, key=lambda x: x[0])
                                st.session_state["sector_recien_creado_id"] = int(ultimo_sector[0])

                        st.session_state["mostrar_registro_sector_desde_estudiante"] = False
                        st.session_state.pop("nuevo_sector_nombre_estudiante", None)
                        st.session_state.pop("nuevo_sector_tipo_estudiante", None)
                        st.session_state.pop("nuevo_sector_observacion_estudiante", None)

                        st.rerun()

                    else:

                        st.error(
                            f"❌ {mensaje_sector}"
                        )

        with col_sector2:

            if st.button(
                "❌ Cancelar",
                use_container_width=True,
                key="cancelar_sector_estudiante"
            ):

                st.session_state[
                    "mostrar_registro_sector_desde_estudiante"
                ] = False

                st.rerun()

    # === BLOQUE 3: SALUD ===
    st.write("---")
    st.markdown("### 🩺 3. Salud y Caracterización Poblacional")
    col7, col8 = st.columns(2)
    
    rhs = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
    caracterizaciones = ["Ninguna", "Víctima del conflicto", "Afrocolombiano", "Indígena", "Discapacidad", "Rom", "Palenquero"]

    with col7:
        st.selectbox(
            "Grupo Sanguíneo y RH*", 
            options=rhs, 
            index=rhs.index(st.session_state.get("reg_est_rh", "O+")) if st.session_state.get("reg_est_rh") in rhs else 0,
            key="reg_est_rh", 
            disabled=not edit_mode
        )
        st.text_input("Grupo Sisbén (Ej: A1, B3, C2)*", key="reg_est_sisben", disabled=not edit_mode)
    with col8:
        st.text_input("EPS Asignada*", key="reg_est_eps", disabled=not edit_mode)
        st.selectbox(
            "Caracterización Poblacional*", 
            options=caracterizaciones,
            index=caracterizaciones.index(st.session_state.get("reg_est_caract", "Ninguna")) if st.session_state.get("reg_est_caract") in caracterizaciones else 0,
            key="reg_est_caract",
            disabled=not edit_mode
        )

    # === BLOQUE 4: FOTOGRAFÍA (EN EDICIÓN O NUEVO) ===
    if is_nuevo or edit_mode:
        st.write("---")
        st.markdown("### 📷 4. Fotografía del Estudiante")
        st.caption("Opcional — puede agregarse ahora o actualizarse más adelante.")
        
        archivo_foto_est = st.file_uploader(
            "Subir foto del estudiante (JPG, PNG)",
            type=["jpg", "jpeg", "png"],
            key=f"uploader_foto_registro_est_{est_id}"
        )
        if archivo_foto_est:
            st.image(archivo_foto_est, width=120, caption="Vista previa")


def guardar_estudiante_formulario():
    id_limpio = st.session_state.get("reg_est_id_real") or web_generar_codigo_estudiante()
    if not id_limpio:
        st.error("❌ No fue posible generar el código del estudiante.")
        return

    p_nom = st.session_state.get("reg_est_p_nom", "").strip()
    p_ape = st.session_state.get("reg_est_p_ape", "").strip()
    num_doc = st.session_state.get("reg_est_num_doc", "").strip()
    dir_res = st.session_state.get("reg_est_dir", "").strip()
    tel = st.session_state.get("reg_est_tel", "").strip()
    
    # Campos opcionales para evitar bloqueos innecesarios
    sisben = st.session_state.get("reg_est_sisben", "").strip().upper()
    eps = st.session_state.get("reg_est_eps", "").strip()

    # Validación flexible de campos principales
    if not (p_nom and p_ape and num_doc and dir_res and tel):
        st.error("❌ Por favor, diligencie los campos obligatorios principales (*): Nombre, Apellido, Documento, Dirección y Teléfono.")
        return

    foto_url_est = None
    archivo_foto_est = st.session_state.get(f"uploader_foto_registro_est_{id_limpio}")
    if archivo_foto_est is not None:
        ext_foto = archivo_foto_est.name.rsplit(".", 1)[-1].lower()
        foto_url_est = f"{id_limpio}_foto.{ext_foto}"
        os.makedirs("assets", exist_ok=True)
        with open(os.path.join("assets", foto_url_est), "wb") as _f:
            _f.write(archivo_foto_est.getbuffer())

    with st.spinner("Registrando datos en PostgreSQL..."):
        # Llamamos a web_registrar_estudiante sin pasarle barrio_vereda, 
        # ya que la función ahora lo calcula automáticamente por debajo con el id_sector.
        exito, mensaje = web_registrar_estudiante(
            id_est=id_limpio,
            tipo_doc=st.session_state.get("reg_est_tipo_doc"),
            num_doc=num_doc,
            lug_exp=st.session_state.get("reg_est_lug_exp", "").strip(),  # Municipio de expedición
            f_nac=st.session_state.get("reg_est_f_nac"),
            genero=st.session_state.get("reg_est_gen"),
            rh=st.session_state.get("reg_est_rh"),
            eps=eps,
            sisben=sisben,
            caract=st.session_state.get("reg_est_caract"),
            direccion=dir_res,
            estrato=st.session_state.get("reg_est_estrato"),
            tel=tel,
            p_ape=p_ape.upper(),
            s_ape=st.session_state.get("reg_est_s_ape", "").strip().upper(),
            p_nom=p_nom.upper(),
            s_nom=st.session_state.get("reg_est_s_nom", "").strip().upper(),
            foto_url=foto_url_est,
            id_municipio=st.session_state.get("reg_est_id_municipio"),
            id_sector=st.session_state.get("reg_est_id_sector")
        )
        
    if exito:
        st.session_state["mensaje_exito_estudiante"] = mensaje
        st.session_state.pop("data_estudiantes", None)
        
        # Activar banderas para volver limpio al flujo de matrícula
        if st.session_state.get("registrando_estudiante_desde_matricula", False):
            st.session_state["mat_estudiante_creado_desde_registro"] = True
            st.session_state["mat_estudiante_creado_id"] = id_limpio
            st.session_state["registrando_estudiante_desde_matricula"] = False
            st.session_state["nuevo_estudiante"] = False
            st.session_state["modo_edicion_estudiante"] = False

        limpiar_formulario_estudiante()
        st.rerun()
    else:
        st.error(f"❌ {mensaje}")

def actualizar_estudiante_formulario():
    est = st.session_state.get("estudiante_actual")
    if not est:
        return
    eid = est[0]

    p_nom = st.session_state.get("reg_est_p_nom", "").strip()
    p_ape = st.session_state.get("reg_est_p_ape", "").strip()
    num_doc = st.session_state.get("reg_est_num_doc", "").strip()
    dir_res = st.session_state.get("reg_est_dir", "").strip()
    tel = st.session_state.get("reg_est_tel", "").strip()
    sisben = st.session_state.get("reg_est_sisben", "").strip().upper()
    eps = st.session_state.get("reg_est_eps", "").strip()

    id_municipio = st.session_state.get(
        "reg_est_id_municipio"
    )

    id_sector = st.session_state.get(
        "reg_est_id_sector"
    )

    if not (
        p_nom
        and p_ape
        and num_doc
        and dir_res
        and tel
        and sisben
        and eps
        and id_municipio
        and id_sector
    ):
        st.error(
            "❌ Complete todos los campos obligatorios (*)."
        )
        return

    with st.spinner("Actualizando estudiante..."):
        ok_e, msg_e = web_actualizar_estudiante(
        eid,
        st.session_state.get("reg_est_tipo_doc"),
        num_doc,
        st.session_state.get("reg_est_lug_exp", "").strip(),
        st.session_state.get("reg_est_f_nac"),
        st.session_state.get("reg_est_gen"),
        st.session_state.get("reg_est_rh"),
        eps,
        sisben,
        st.session_state.get("reg_est_caract"),
        dir_res,

        # NUEVA UBICACIÓN
        st.session_state.get("reg_est_id_municipio"),
        st.session_state.get("reg_est_id_sector"),

        st.session_state.get("reg_est_estrato"),
        tel,
        p_ape.upper(),
        st.session_state.get("reg_est_s_ape", "").strip().upper(),
        p_nom.upper(),
        st.session_state.get("reg_est_s_nom", "").strip().upper(),
    )
        if ok_e:
            nueva_foto = st.session_state.get(f"uploader_foto_registro_est_{eid}")
            if nueva_foto is not None:
                drive = DriveManager()
                foto_url = drive.subir_foto_estudiante(nueva_foto, eid)
                ok_foto, msg_foto = web_actualizar_foto_estudiante(eid, foto_url)
                if not ok_foto:
                    st.warning(msg_foto)

            st.session_state["mensaje_exito_estudiante"] = f"✅ {msg_e}"
            # Limpiar caché para obligar a volver a leer la base
            st.session_state.pop("data_estudiantes", None)

            # ============================================================
            # RECARGAR EL ESTUDIANTE COMPLETO DESDE LA BASE DE DATOS
            # ============================================================

            estudiante_actualizado = web_consultar_estudiante(str(eid))

            if estudiante_actualizado:

                st.session_state["estudiante_actual"] = estudiante_actualizado

                # Recargar todos los campos normales del estudiante
                cargar_estudiante_en_session(
                    estudiante_actualizado
                )

                # ========================================================
                # SINCRONIZAR UBICACIÓN
                # ========================================================

                # El estudiante guarda directamente el municipio.
                municipio_actual = (
                    estudiante_actualizado[19]
                    if len(estudiante_actualizado) > 19
                    else None
                )

                sector_actual = (
                    estudiante_actualizado[20]
                    if len(estudiante_actualizado) > 20
                    else None
                )

                st.session_state[
                    "reg_est_id_municipio"
                ] = municipio_actual

                st.session_state[
                    "reg_est_id_sector"
                ] = sector_actual

                # Buscar el departamento correspondiente al municipio
                if municipio_actual:

                    departamentos = obtener_departamentos()

                    for departamento in departamentos:

                        municipios_dep = obtener_municipios(
                            departamento[0]
                        )

                        for municipio in municipios_dep:

                            if municipio[0] == municipio_actual:

                                st.session_state[
                                    "reg_est_id_departamento"
                                ] = departamento[0]

                                break

                        if st.session_state.get(
                            "reg_est_id_departamento"
                        ) == departamento[0]:

                            break
            else:
                st.error("❌ Se guardó el estudiante, pero no fue posible recargar sus datos.")

            st.session_state["modo_edicion_estudiante"] = False

            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ {msg_e}")


def mostrar_busqueda_estudiantes():
    # Detectar si se acaba de ingresar a este módulo desde otra sección del menú principal
    if st.session_state.get("modulo_activo") != "estudiantes":
        st.session_state["modulo_activo"] = "estudiantes"
        limpiar_formulario_estudiante()

    st.title("👶 Gestión de Estudiantes")

    if "mensaje_exito_estudiante" in st.session_state:
        st.success(st.session_state.pop("mensaje_exito_estudiante"))

    col1, col2 = st.columns([3, 1])

    with col1:
        if "data_estudiantes" not in st.session_state:
            with st.spinner("Cargando base de datos de estudiantes..."):
                st.session_state.data_estudiantes = web_buscar_estudiante_dinamico("")

        if st.session_state.data_estudiantes is not None:
            def buscar_estudiantes(searchterm: str):
                if not searchterm:
                    return []

                texto = searchterm.strip().lower()
                resultados = []
                st.session_state.estudiantes_encontrados = {}

                for r in st.session_state.data_estudiantes:
                    codigo = str(r[0])
                    documento = str(r[2])
                    nombre_completo = f"{r[14] or ''} {r[15] or ''} {r[16] or ''} {r[17] or ''}".replace("  ", " ").strip()

                    palabras = nombre_completo.lower().split()
                    coincide_nombre = any(palabra.startswith(texto) for palabra in palabras)
                    coincide_documento = documento.lower().startswith(texto)
                    coincide_codigo = codigo.lower().startswith(texto)

                    if coincide_nombre or coincide_documento or coincide_codigo:
                        etiqueta = f"Cod: {codigo} - {nombre_completo} - Doc: {documento}"
                        resultados.append(etiqueta)
                        st.session_state.estudiantes_encontrados[etiqueta] = r

                return resultados[:20]

            seleccion = st_searchbox(
                buscar_estudiantes,
                placeholder="Escriba código, nombre, apellido o documento...",
                label="Buscar estudiante",
                key="buscar_estudiante"
            )

            if seleccion:
                nuevo_est = st.session_state.estudiantes_encontrados.get(seleccion)
                if nuevo_est:
                    estudiante_completo = web_consultar_estudiante(nuevo_est[0])
                    if estudiante_completo:
                        if "estudiante_actual" not in st.session_state or st.session_state.estudiante_actual[0] != estudiante_completo[0]:
                            st.session_state["estudiante_actual"] = estudiante_completo
                            st.session_state["nuevo_estudiante"] = False
                            st.session_state["modo_edicion_estudiante"] = False
                            cargar_estudiante_en_session(estudiante_completo)
                            st.rerun()

    with col2:
        if st.button("➕ Nuevo", use_container_width=True):
            limpiar_formulario_estudiante()
            st.session_state["nuevo_estudiante"] = True
            st.session_state["modo_edicion_estudiante"] = True
            st.rerun()

    st.write("---")

    # === SISTEMA DE PESTAÑAS ===
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Datos del Estudiante",
        "📑 Matrícula",
        "👨‍👩‍👧 Acudiente",
        "📂 Documentos"
    ])

    with tab1:
        if st.session_state.get("nuevo_estudiante", False):
            mostrar_formulario_estudiante(modo="nuevo")
        elif "estudiante_actual" in st.session_state and st.session_state["estudiante_actual"]:
            mostrar_formulario_estudiante(modo="consulta")
        else:
            st.info("🔍 Busque un estudiante en la parte superior o haga clic en el botón ➕ Nuevo para registrar uno nuevo.")

    with tab2:
        if "estudiante_actual" in st.session_state and st.session_state["estudiante_actual"]:
            resultado_mat = web_consultar_matricula(st.session_state["estudiante_actual"][0])
            
            if resultado_mat:
                (id_mat, id_est, id_acu, folio, ano_lectivo, sede, jornada, estado, id_curso, institucion, observaciones) = resultado_mat
                
                st.markdown("### 📝 Información de Matrícula")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Folio", value=str(folio or ""), disabled=True, key="mat_folio")
                    st.text_input("Año Lectivo", value=str(ano_lectivo or ""), disabled=True, key="mat_ano_lectivo")
                    st.text_input("Sede", value=str(sede or ""), disabled=True, key="mat_sede")
                    st.text_input("Jornada", value=str(jornada or ""), disabled=True, key="mat_jornada")
                    st.text_input("Institución", value=str(institucion or ""), disabled=True, key="mat_institucion")
                
                with col2:
                    st.text_input("Código Matrícula", value=str(id_mat or ""), disabled=True, key="mat_id_mat")
                    st.text_input("Curso", value=str(id_curso or ""), disabled=True, key="mat_id_curso")
                    st.text_input("Estado", value=str(estado or ""), disabled=True, key="mat_estado")
                    st.text_input("Código Acudiente", value=str(id_acu or ""), disabled=True, key="mat_id_acu")
                
                st.text_area("Observaciones", value=str(observaciones or ""), disabled=True, key="mat_observaciones")
                
            else:
                st.warning("No existe matrícula registrada para este estudiante.")
        else:
            st.info("Seleccione un estudiante primero.")

    with tab3:
        if "estudiante_actual" in st.session_state and st.session_state["estudiante_actual"]:
            resultado_mat = web_consultar_matricula(st.session_state["estudiante_actual"][0])
            if resultado_mat:
                id_acu = resultado_mat[2]
                resultado_acu = web_consultar_acudiente(id_acu)
                
                if resultado_acu:
                    st.markdown("### 📝 Información de Matrícula y Acudiente")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text_input("Código Acudiente", value=str(resultado_acu[0]), disabled=True)
                        st.text_input("Documento", value=str(resultado_acu[2]), disabled=True)
                        st.text_input("Nombres", value=f"{resultado_acu[3]} {resultado_acu[4] or ''}".strip(), disabled=True)
                        st.text_input("Teléfono", value=str(resultado_acu[10] or ""), disabled=True)
                        st.text_input("Ocupación", value=str(resultado_acu[12] or ""), disabled=True)
                    
                    with col2:
                        st.text_input("Apellidos", value=f"{resultado_acu[5]} {resultado_acu[6] or ''}".strip(), disabled=True)
                        st.text_input("Correo", value=str(resultado_acu[11] or ""), disabled=True)
                        st.text_input("Dirección", value=str(resultado_acu[14] or ""), disabled=True)
                    
                    st.text_area("Observaciones", value=str(resultado_acu[15] or ""), disabled=True)

                else:
                    st.warning(f"No se encontró información para el acudiente {id_acu}")
            else:
                st.warning("No existe matrícula registrada para este estudiante.")
        else:
            st.info("Seleccione un estudiante primero.")

    with tab4:
        if "estudiante_actual" in st.session_state and st.session_state["estudiante_actual"]:
            mostrar_documentos_estudiante(st.session_state["estudiante_actual"])
        else:
            st.info("Seleccione un estudiante primero.")


def mostrar_documentos_estudiante(est):
    st.subheader("📁 Repositorio Documental")
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"]{
        gap:0.4rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        tipo = st.selectbox(
            "Tipo de documento",
            ["Registro Civil", "Tarjeta de Identidad", "EPS", "Sisben", "Foto", "Observador", "Otro"],
            key=f"tipo_{est[0]}"
        )

    with col2:
        archivo = st.file_uploader(
            "Seleccionar documento",
            type=["pdf", "jpg", "jpeg", "png"],
            key=f"doc_{est[0]}"
        )

        st.write("")
        subir = st.button("📤 Subir documento", use_container_width=True, key=f"subir_{est[0]}")

    if subir:
        if archivo is None:
            st.warning("Seleccione un documento.")
            st.stop()

        drive = DriveManager()
        carpeta_estudiante = drive.obtener_carpeta_estudiante(est[0])

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo.name)[1]) as temp:
            temp.write(archivo.getbuffer())
            ruta_temporal = temp.name

        resultado = drive.subir_archivo(ruta_temporal, archivo.name, carpeta_estudiante)

        guardar_documento(
            id_estudiante=est[0],
            tipo_documento=tipo,
            nombre_archivo=archivo.name,
            drive_id=resultado["id"],
            drive_url=resultado["webViewLink"],
            carpeta_drive=carpeta_estudiante
        )

        os.remove(ruta_temporal)
        st.success("Documento cargado correctamente.")
        st.write(resultado["webViewLink"])

    st.divider()

    documentos = obtener_documentos_estudiante(est[0])

    if not documentos:
        st.info("Este estudiante aún no tiene documentos registrados.")
    else:
        col1, col2, col3 = st.columns([8, 1.2, 1.2])
        with col1:
            st.subheader("📁 Documentos registrados")
        with col2:
            st.markdown("<center><b>Ver</b></center>", unsafe_allow_html=True)
        with col3:
            st.markdown("<center><b>Eliminar</b></center>", unsafe_allow_html=True)

        st.markdown("---")

        for doc in documentos:
            url_drive = None
            for item in doc:
                if isinstance(item, str) and item.startswith("http"):
                    url_drive = item
                    break

            col_d1, col_d2, col_d3 = st.columns([6, 0.8, 0.8])
            nombre_doc = doc[1] if len(doc) > 1 else "Documento"
            tipo_doc = doc[2] if len(doc) > 2 else ""
            
            col_d1.markdown(f"**📄 {nombre_doc}** <span style='color:gray; font-size:0.85em;'>({tipo_doc})</span>", unsafe_allow_html=True)

            with col_d2:
                if url_drive:
                    st.link_button("👁️", url_drive, use_container_width=True, key=f"link_ver_{doc[0]}")
                else:
                    st.button("👁️", key=f"ver_disabled_{doc[0]}", disabled=True, use_container_width=True)

            with col_d3:
                st.button("🗑️", key=f"eliminar_doc_{doc[0]}", use_container_width=True)
            st.markdown("---")
