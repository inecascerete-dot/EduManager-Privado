import os
import sys
import datetime
import tempfile
import streamlit as st
from datetime import date
from streamlit_searchbox import st_searchbox
from backend.drive_manager import DriveManager
from backend.documentos_db import (
    guardar_documento, 
    obtener_documentos_estudiante,
  )

from backend.acudientes_db import (
    web_obtener_documentos_acudiente,
    web_guardar_documento_acudiente,
    web_registrar_acudiente
 )


# Agrega la ruta raíz del proyecto para permitir importar desde la carpeta principal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.acudientes_db import (
    web_buscar_acudiente_dinamico,
    web_consultar_acudiente_por_documento,
    obtener_siguiente_codigo_acudiente
)
from backend.utils import flash_set, mostrar_flash
from backend.estudiantes_db import (
    web_buscar_estudiante_dinamico,
    web_actualizar_foto_estudiante
)

from backend.db_manager import (
    web_obtener_cursos,
    web_obtener_cursos_completo,
    web_obtener_grados_con_detalle
)

from backend.matriculas_db import (
    web_generar_folio_matricula,
    web_registrar_matricula,
    web_buscar_matriculas,
    web_actualizar_estado_matricula,
    web_consultar_matricula_por_ano
)

from backend.estudiantes import (
    cargar_estudiante_en_session,
    mostrar_formulario_estudiante,
    web_generar_codigo_estudiante
)

from backend.acudientes import (
    cargar_acudiente_en_session,
    mostrar_formulario_acudiente,
    limpiar_formulario_acudiente,
    cargar_catalogos_acudiente
)

from backend.catalogos_db import (
    obtener_tipos_documento,
    obtener_departamentos,
    obtener_municipios,
    obtener_sectores,
    obtener_sectores_por_municipio
)

import re
import os
from backend.utils import obtener_ruta_foto


def abreviar_grado(nombre_grado):
    """Convierte un nombre de grado largo en una abreviatura corta (ej: Quinto -> 5°)."""
    if not nombre_grado:
        return ""
    mapeo = {
        "preescolar": "Pre", "transición": "Tr", "primero": "1°", 
        "segundo": "2°", "tercero": "3°", "cuarto": "4°", "quinto": "5°", 
        "sexto": "6°", "séptimo": "7°", "octavo": "8°", 
        "noveno": "9°", "décimo": "10°", "undécimo": "11°"
    }
    # Buscamos en minúsculas por si viene con mayúsculas/minúsculas distintas
    return mapeo.get(nombre_grado.strip().lower(), nombre_grado[:3])

def limpiar_matricula():
    claves = [
        "estudiante_actual",
        "mat_est_data",
        "mat_est_nom",
        "id_est_mat",
        "mat_acu_data",
        "mat_acu_nom",
        "id_acu_mat",
        "buscar_estudiante_matricula",
        "buscar_acudiente_matricula",
        "nuevo_estudiante",
        "mat_editando_est",
        "mat_editando_acu",
        "modo_edicion",
        "modo_edicion_acudiente"
    ]

    for c in claves:
        st.session_state.pop(c, None)

def mostrar_ficha_estudiante(estudiante):
    """
    Ficha resumen del estudiante con diseño en tarjetas e iconos.
    Muestra la fotografía almacenada en Google Drive o una imagen local.
    """

    if not estudiante:
        return False

    try:
        codigo = estudiante[0]
        tipo_documento = estudiante[1]
        numero_documento = estudiante[2]

        lugar_nacimiento = estudiante[3] if len(estudiante) > 3 else "—"
        fecha_nacimiento = estudiante[4] if len(estudiante) > 4 else "—"
        sexo = estudiante[5] if len(estudiante) > 5 else "—"
        grupo_sanguineo = estudiante[6] if len(estudiante) > 6 else "—"
        eps = estudiante[7] if len(estudiante) > 7 else "—"
        sisben = estudiante[8] if len(estudiante) > 8 else "—"
        poblacion = estudiante[9] if len(estudiante) > 9 else "—"

        p_nom = estudiante[16] if len(estudiante) > 16 else ""
        s_nom = estudiante[17] if len(estudiante) > 17 else ""
        p_ape = estudiante[14] if len(estudiante) > 14 else ""
        s_ape = estudiante[15] if len(estudiante) > 15 else ""

        nombre_completo = (
            f"{p_nom} {s_nom} {p_ape} {s_ape}"
        ).strip()

        direccion = estudiante[10] if len(estudiante) > 10 else "—"
        estrato = estudiante[12] if len(estudiante) > 12 else "—"
        telefono = estudiante[13] if len(estudiante) > 13 else "—"

        # La fotografía está en el campo 18 de la consulta SELECT *
        url_foto = estudiante[18] if len(estudiante) > 18 else None
        sector = estudiante[11] if len(estudiante) > 11 else None

    except Exception:
        codigo = estudiante[0] if len(estudiante) > 0 else ""
        tipo_documento = estudiante[1] if len(estudiante) > 1 else ""
        numero_documento = estudiante[2] if len(estudiante) > 2 else ""

        lugar_nacimiento = "—"
        fecha_nacimiento = "—"
        sexo = "—"
        grupo_sanguineo = "—"
        eps = "—"
        sisben = "—"
        poblacion = "—"
        nombre_completo = "Estudiante"
        direccion = "—"
        sector = "—"
        estrato = "—"
        telefono = "—"
        url_foto = None

    with st.container(border=True):

        # =========================================================
        # 1. CABECERA: FOTO + DATOS PRINCIPALES (Nivelados correctamente)
        # =========================================================
        col_foto, col_info = st.columns([1, 3])

        with col_foto:
            imagen_mostrada = False

            try:
                if url_foto:
                    ruta_foto = obtener_ruta_foto(url_foto)

                    if ruta_foto:
                        # -------------------------------------------------
                        # Google Drive
                        # -------------------------------------------------
                        if (
                            isinstance(ruta_foto, str)
                            and "drive.google.com" in ruta_foto
                        ):
                            try:
                                import requests
                                from io import BytesIO

                                respuesta = requests.get(
                                    ruta_foto,
                                    timeout=10
                                )

                                if (
                                    respuesta.status_code == 200
                                    and respuesta.content
                                ):
                                    st.image(
                                        BytesIO(respuesta.content),
                                        width=130,
                                        caption="Foto actual"
                                    )
                                    imagen_mostrada = True

                            except Exception:
                                pass

                        # -------------------------------------------------
                        # Archivo local
                        # -------------------------------------------------
                        elif os.path.exists(str(ruta_foto)):
                            st.image(
                                ruta_foto,
                                width=130,
                                caption="Foto actual"
                            )
                            imagen_mostrada = True

                        # -------------------------------------------------
                        # Otra URL HTTP/HTTPS
                        # -------------------------------------------------
                        elif (
                            isinstance(ruta_foto, str)
                            and (
                                ruta_foto.startswith("http://")
                                or ruta_foto.startswith("https://")
                            )
                        ):
                            try:
                                import requests
                                from io import BytesIO

                                respuesta = requests.get(
                                    ruta_foto,
                                    timeout=10
                                )

                                if (
                                    respuesta.status_code == 200
                                    and respuesta.content
                                ):
                                    st.image(
                                        BytesIO(respuesta.content),
                                        width=130,
                                        caption="Foto actual"
                                    )
                                    imagen_mostrada = True

                            except Exception:
                                pass

            except Exception:
                imagen_mostrada = False

            # -------------------------------------------------------------
            # Si no pudo mostrar la foto
            # -------------------------------------------------------------
            if not imagen_mostrada:
                st.markdown(
                    "<div style='width:130px;height:160px;"
                    "border:2px dashed #cbd5e1;"
                    "border-radius:8px;"
                    "display:flex;"
                    "align-items:center;"
                    "justify-content:center;"
                    "color:#94a3b8;"
                    "font-size:30px;"
                    "background:#f8fafc'>👤</div>",
                    unsafe_allow_html=True
                )
                st.caption("Sin foto")

        with col_info:
            st.markdown(f"### {nombre_completo}")
            st.markdown(f"**📄 Documento:** {tipo_documento} — {numero_documento}")
            st.markdown(f"**📍 Lugar Exp. Documento:** {lugar_nacimiento}")
            st.markdown(f"**📅 Fecha de nacimiento:** {fecha_nacimiento}")

        st.markdown("---")

        # =========================================================
        # 2. DATOS DEL ESTUDIANTE EN DOS COLUMNAS AMPLIAS
        # =========================================================
        st.markdown(
            """
            <div style="
                font-size: 24px;
                font-weight: 700;
                color: #1f2937;
                margin: 10px 0 18px 0;
            ">
                📋 Información del estudiante
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2, gap="large")

        def crear_tarjeta(icono, titulo, valor):
            return f"""
            <div style="
                background:#f8fafc;
                border:1px solid #e2e8f0;
                border-radius:10px;
                padding:14px 16px;
                margin-bottom:12px;
            ">
                <div style="
                    font-size:12px;
                    color:#64748b;
                    font-weight:600;
                    margin-bottom:5px;
                ">{icono} {titulo}</div>
                <div style="
                    font-size:16px;
                    color:#1e293b;
                    font-weight:600;
                ">{valor}</div>
            </div>
            """

        # ---------------------------------------------------------
        # COLUMNA 1 (Primer bloque de campos)
        # ---------------------------------------------------------
        with c1:
            st.markdown(crear_tarjeta("🆔", "Código", codigo), unsafe_allow_html=True)
            st.markdown(crear_tarjeta("⚧️", "Sexo", sexo), unsafe_allow_html=True)
            st.markdown(crear_tarjeta("🩸", "Grupo sanguíneo", grupo_sanguineo), unsafe_allow_html=True)
            st.markdown(crear_tarjeta("👥", "Grupo Población", poblacion), unsafe_allow_html=True)
            st.markdown(crear_tarjeta("📍", "Direccion", direccion), unsafe_allow_html=True)
            

        # ---------------------------------------------------------
        # COLUMNA 2 (Segundo bloque de campos)
        # ---------------------------------------------------------
        with c2:
            st.markdown(crear_tarjeta("📞", "Teléfono", telefono), unsafe_allow_html=True)
            st.markdown(crear_tarjeta("📊", "Estrato", estrato), unsafe_allow_html=True)
            st.markdown(crear_tarjeta("🏥", "EPS", eps), unsafe_allow_html=True)
            st.markdown(crear_tarjeta("📋", "Sisbén", sisben), unsafe_allow_html=True)
            st.markdown(crear_tarjeta("🗺️", "Barrio", sector), unsafe_allow_html=True)

        # =========================================================
        # 3. BOTÓN EDITAR
        # =========================================================
        st.write("")

        editar = st.button(
            "✏️ Revisar y editar estudiante",
            key="btn_editar_ficha_estudiante",
            use_container_width=True
        )

        return editar
    
def mostrar_ficha_acudiente(acudiente):
    """
    Ficha detallada del acudiente con diseño en tarjetas e iconos, 
    equilibrando los campos principales en dos columnas.
    """
    if not acudiente:
        return False

    try:
        codigo = acudiente[0] if len(acudiente) > 0 else "—"
        tipo_doc = acudiente[1] if len(acudiente) > 1 else "—"
        documento = acudiente[2] if len(acudiente) > 2 else "—"
        p_nom = acudiente[3] if len(acudiente) > 3 else ""
        s_nom = acudiente[4] if len(acudiente) > 4 else ""
        p_ape = acudiente[5] if len(acudiente) > 5 else ""
        s_ape = acudiente[6] if len(acudiente) > 6 else ""
        
        nombre_completo = f"{p_nom} {s_nom} {p_ape} {s_ape}".strip()
        if not nombre_completo:
            nombre_completo = f"Acudiente {codigo}"

        telefono = acudiente[10] if len(acudiente) > 10 else "—"
        correo = acudiente[11] if len(acudiente) > 11 else "—"
        direccion = acudiente[14] if len(acudiente) > 14 else "—"
        
        # 1. Obtenemos los catálogos primero para poder traducir de una vez
        tipos = {str(t[0]): t[2] for t in obtener_tipos_documento()}
        departamentos = {str(d[0]): d[2] for d in obtener_departamentos()}
        sectores = {str(s[0]): s[1] for s in obtener_sectores()}

        tipo_doc = tipos.get(str(tipo_doc), tipo_doc)

        # 2. Traducimos el sector de una vez para usarlo arriba
        raw_sector = str(acudiente[13]) if len(acudiente) > 13 and acudiente[13] is not None else ""
        sector = sectores.get(raw_sector, raw_sector) if raw_sector else "—"

        # 3. Creamos extras SIN el sector, para que no se repita abajo
        extras = {
            "Fecha de nacimieno": acudiente[7] if len(acudiente) > 7 else "",
            "Departamento de nacimiento": departamentos.get(str(acudiente[8]), acudiente[8]) if len(acudiente) > 8 and acudiente[8] else "",
            "Municipio de nacimiento": "",
            "Ocupación": acudiente[12] if len(acudiente) > 12 else "",
            "Observaciones": acudiente[15] if len(acudiente) > 15 else ""
        }

        # Resolver municipio correctamente si hay departamento
        if len(acudiente) > 8 and acudiente[8] and len(acudiente) > 9 and acudiente[9]:
            municipios = obtener_municipios(acudiente[8])
            dic_municipios = {str(m[0]): m[2] for m in municipios}
            extras["Municipio de nacimiento"] = dic_municipios.get(str(acudiente[9]), acudiente[9])

        extras = {k: v for k, v in extras.items() if str(v).strip()}
        
    except Exception:
        codigo = acudiente[0] if len(acudiente) > 0 else ""
        documento = acudiente[2] if len(acudiente) > 2 else ""
        nombre_completo = "Acudiente"
        telefono, correo, direccion, sector = "—", "—", "—", "—"
        extras = {}

    with st.container(border=True):
        # 1. Cabecera principal estilo tarjeta con avatar
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                background: #ffffff;
                padding: 15px;
                border-radius: 8px;
                border-left: 6px solid #0d6efd;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                margin-bottom: 15px;
            ">
                <div style="
                    background: #e1effe;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 15px;
                    flex-shrink: 0;
                ">
                    <span style="font-size: 28px;">👤</span>
                </div>
                <div>
                    <div style="
                        font-size: 22px;
                        font-weight: 700;
                        color: #1f2937;
                    ">
                        {codigo} - {nombre_completo}
                    </div>
                    <div style="
                        font-size: 16px;
                        font-weight: 600;
                        color: #2563eb;
                        margin-top: 4px;
                    ">
                        {tipo_doc} &nbsp;|&nbsp; {documento}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Función auxiliar para renderizar cada cajita de campo
        def tarjeta_campo(icon, label, value):
            return f"""
            <div style="
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 14px;
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            ">
                <div style="
                    background: #e2e8f0;
                    border-radius: 6px;
                    width: 36px;
                    height: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 12px;
                    flex-shrink: 0;
                    font-size: 18px;
                ">
                    {icon}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-size: 12px; color: #64748b; font-weight: 500;">{label}</div>
                    <div style="font-size: 14px; color: #1e293b; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{value}</div>
                </div>
            </div>
            """

        # 2. Datos principales distribuidos equilibradamente (incluyendo el Sector ya traducido arriba al lado de la dirección)
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(tarjeta_campo("📞", "Teléfono", str(telefono)), unsafe_allow_html=True)
            st.markdown(tarjeta_campo("📍", "Dirección", str(direccion)), unsafe_allow_html=True)
        with c2:
            st.markdown(tarjeta_campo("✉️", "Correo electrónico", str(correo)), unsafe_allow_html=True)
            st.markdown(tarjeta_campo("🏢", "Barrio / Sector", str(sector)), unsafe_allow_html=True)

        # 3. Datos Adicionales (si existen) con el mismo formato de tarjetas
        if extras:
            st.markdown("---")
            st.markdown("##### 📌 Datos Registrados Adicionales")
            
            iconos_extra = {
                "Fecha de nacimieno": "📅",
                "Departamento": "🏛️",
                "Municipio": "📍",
                "Ocupación": "💼",
                "Observaciones": "📝"
            }
            
            ce1, ce2 = st.columns(2)
            items = list(extras.items())
            
            for i, (k, v) in enumerate(items):
                ico = iconos_extra.get(k, "📋")
                html_tarjeta = tarjeta_campo(ico, k, str(v))
                if i % 2 == 0:
                    with ce1:
                        st.markdown(html_tarjeta, unsafe_allow_html=True)
                else:
                    with ce2:
                        st.markdown(html_tarjeta, unsafe_allow_html=True)

        st.write("")
        editar = st.button(
            "✏️ Revisar y editar acudiente",
            key="btn_editar_ficha_acudiente",
            use_container_width=True
        )
        return editar

def mostrar_registro_matricula():
    """
    Interfaz completa del registro de matrículas con fichas interactivas en cada paso.
    """

    st.title("📝 Registro de Nuevas Matrículas")

    if "mat_registro_exitoso" in st.session_state:
        msg_exito = st.session_state.pop("mat_registro_exitoso")
        st.success(f"✅ {msg_exito}")
        st.balloons()
        st.info("Puede registrar una nueva matrícula usando el formulario a continuación.")
        st.write("")

    if "mat_paso" not in st.session_state:
        st.session_state.mat_paso = 1
    if "mat_est_nom" not in st.session_state:
        st.session_state.mat_est_nom = ""
    if "mat_acu_nom" not in st.session_state:
        st.session_state.mat_acu_nom = ""
    if "data_estudiantes" not in st.session_state:
        st.session_state.data_estudiantes = web_buscar_estudiante_dinamico("")
    if "data_acudientes" not in st.session_state:
        st.session_state.data_acudientes = web_buscar_acudiente_dinamico("")

    paso_actual = st.session_state.mat_paso

    PASOS = ["1 · Estudiante", "2 · Acudiente", "3 · Datos académicos", "4 · Documentos", "5 · Confirmar"]
    cols_prog = st.columns(5)
    for i, (col, label) in enumerate(zip(cols_prog, PASOS), start=1):
        with col:
            if i < paso_actual:
                st.markdown(f"<div style='text-align:center;padding:6px 0;background:#d4edda;border-radius:8px;font-size:13px;color:#155724;font-weight:600'>✔ {label}</div>", unsafe_allow_html=True)
            elif i == paso_actual:
                st.markdown(f"<div style='text-align:center;padding:6px 0;background:#0d6efd;border-radius:8px;font-size:13px;color:#fff;font-weight:700'>{label}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center;padding:6px 0;background:#e9ecef;border-radius:8px;font-size:13px;color:#6c757d'>{label}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- CÁLCULO DE PROGRESO REAL BASADO EN DATOS ---
    puntos_progreso = 0
    
    # 20% si hay estudiante cargado (usamos tu clave id_est_mat o mat_est_data)
    if st.session_state.get("id_est_mat") or st.session_state.get("mat_est_data"):
        puntos_progreso += 20
        
    # 20% si hay acudiente cargado
    if st.session_state.get("id_acu_mat") or st.session_state.get("mat_acu_data"):
        puntos_progreso += 20
        
    # 20% si hay datos académicos seleccionados (ej: curso)
    if st.session_state.get("mat_curso"):
        puntos_progreso += 20
        
    # 20% por documentos (puedes ajustar esta regla según tu lógica interna de documentos)
    if paso_actual >= 4:  # o validando si ya subió documentos
        puntos_progreso += 20
        
    # El porcentaje final normalizado para la barra de Streamlit (de 0.0 a 1.0)
    porcentaje_flotante = puntos_progreso / 100.0

    col_progreso, col_boton = st.columns([4, 1])

    with col_progreso:
        st.progress(
            porcentaje_flotante, 
            text=f"Progreso real de la matrícula: {puntos_progreso}% (Paso {paso_actual} de 5)"
        )

    with col_boton:
        if st.button("🚫 Cancelar", key="mat_cancelar_wizard", help="Descarta el progreso actual y reinicia el formulario", use_container_width=True):
            limpiar_matricula()
            claves_wizard = [
                "mat_est_nom", "mat_acu_nom", "mat_est_data", "mat_acu_data",
                "mat_paso", "mat_parentesco", "mat_ano", "mat_sede",
                "mat_jornada", "mat_curso", "mat_estado", "mat_fecha",
                "mat_observaciones", "mat_est_sin_resultados", "mat_acu_sin_resultados",
                "id_est_mat", "id_acu_mat", "mat_editando_est", "mat_editando_acu",
                "modo_edicion", "modo_edicion_estudiante", "modo_edicion_acudiente"
            ]
            for _k in claves_wizard:
                st.session_state.pop(_k, None)
            st.rerun()

    st.markdown("---")
    st.write("")

    # =========================================================
    # PASO 1 — Buscar y validar el Estudiante
    # =========================================================
    if paso_actual == 1:
        
        # -------------------------------------------------------------------------
        # 0. CONTROL DE PANTALLA: SI ESTAMOS REGISTRANDO UN ESTUDIANTE NUEVO
        # -------------------------------------------------------------------------
        if st.session_state.get("registrando_estudiante_desde_matricula", False):
            st.markdown("### 🆕 Registrar nuevo estudiante")
            st.info("El estudiante no fue encontrado. Complete el formulario para registrarlo y continuar con la matrícula.")
            
            # Botón de escape limpio para cancelar y liberar el código
            if st.button("❌ Cancelar y volver", key="btn_cancelar_reg_mat_absoluto", use_container_width=True):
                st.session_state["registrando_estudiante_desde_matricula"] = False
                st.session_state["modo_edicion_estudiante"] = False
                st.session_state["nuevo_estudiante"] = False
                st.session_state.pop("reg_est_id_real", None)
                st.rerun()
                
            st.write("---")
            
            # CSS INFALIBLE: Oculta el último botón dentro del formulario de registro (que es el de Cancelar Registro)
            st.markdown("""
                <style>
                    /* Oculta de forma directa el botón de cancelar interno del formulario compartido */
                    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
                        display: none !important;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Llamas a tu formulario normalmente
            mostrar_formulario_estudiante(modo="nuevo")
            
            # Detenemos para que no pinte el buscador debajo
            st.stop()
        # -------------------------------------------------------------------------
        # VISTA NORMAL DEL PASO 1 (Buscador y Año Lectivo)
        # -------------------------------------------------------------------------
        st.markdown("### 🕵️ Paso 1: Identificar al Estudiante")
        st.info("Busque al estudiante por su código, documento o nombre. Verifique su ficha antes de continuar.")

        # =========================================================
        # AÑO LECTIVO DE LA MATRÍCULA
        # =========================================================
        st.markdown("#### 📅 Año lectivo de la matrícula")

        ano_actual = date.today().year

        mat_ano = st.selectbox(
            "Seleccione el año lectivo*",
            options=list(range(ano_actual - 1, ano_actual + 2)),
            index=1,
            key="mat_p1_ano"
        )

        st.session_state.mat_ano = mat_ano

        # =========================================================
        # RECUPERAR ESTUDIANTE RECIÉN CREADO
        # =========================================================

        if st.session_state.get(
            "mat_estudiante_creado_desde_registro",
            False
        ):

            codigo_creado = st.session_state.get(
                "mat_estudiante_creado_id"
            )

            if codigo_creado:

                # -----------------------------------------------------
                # RECARGAR LA LISTA DESDE LA BASE DE DATOS
                # -----------------------------------------------------

                st.session_state.pop(
                    "data_estudiantes",
                    None
                )

                st.session_state.data_estudiantes = (
                    web_buscar_estudiante_dinamico("")
                )

                # -----------------------------------------------------
                # BUSCAR EL ESTUDIANTE RECIÉN CREADO
                # -----------------------------------------------------

                estudiante_creado = None

                for fila in st.session_state.data_estudiantes:

                    if str(fila[0]) == str(codigo_creado):
                        estudiante_creado = fila
                        break

                # -----------------------------------------------------
                # SI LO ENCONTRAMOS
                # -----------------------------------------------------

                if estudiante_creado:

                    st.session_state.mat_est_data = estudiante_creado

                    st.session_state.id_est_mat = str(
                        estudiante_creado[0]
                    )

                    nombre_estudiante = (
                        f"{estudiante_creado[16]} "
                        f"{estudiante_creado[17]} "
                        f"{estudiante_creado[14]} "
                        f"{estudiante_creado[15]}"
                    ).strip()

                    st.session_state.mat_est_nom = (
                        nombre_estudiante
                    )

                    # -------------------------------------------------
                    # VALIDAR MATRÍCULA PARA EL AÑO SELECCIONADO
                    # -------------------------------------------------

                    matricula_existente = (
                        web_consultar_matricula_por_ano(
                            st.session_state.id_est_mat,
                            st.session_state.mat_ano
                        )
                    )

                    st.session_state[
                        "matricula_existente_actual"
                    ] = matricula_existente

                    # -------------------------------------------------
                    # LIMPIAR BANDERAS
                    # -------------------------------------------------

                    st.session_state.pop(
                        "mat_estudiante_creado_desde_registro",
                        None
                    )

                    st.session_state.pop(
                        "mat_estudiante_creado_id",
                        None
                    )

                    st.success(
                        f"✅ Estudiante registrado correctamente: "
                        f"{nombre_estudiante}"
                    )

        def buscar_estudiantes_matricula(searchterm: str):
            if not searchterm:
                st.session_state["mat_est_sin_resultados"] = False
                return []
            texto = searchterm.strip().lower()
            resultados = []
            st.session_state.estudiantes_encontrados_mat = {}
            for r in st.session_state.data_estudiantes:
                codigo = str(r[0])
                documento = str(r[2])
                nombre_completo = f"{r[16]} {r[17]} {r[14]} {r[15]}".strip()
                palabras = nombre_completo.lower().split()
                coincide_nombre = any(p.startswith(texto) for p in palabras)
                coincide_documento = documento.lower().startswith(texto)
                coincide_codigo = codigo.lower().startswith(texto)
                if coincide_nombre or coincide_documento or coincide_codigo:
                    etiqueta = f"Cod: {codigo} - {nombre_completo} - Doc: {documento}"
                    resultados.append(etiqueta)
                    st.session_state.estudiantes_encontrados_mat[etiqueta] = r
            st.session_state["mat_est_sin_resultados"] = len(resultados) == 0
            return resultados[:20]

        seleccion_estudiante = st_searchbox(
            buscar_estudiantes_matricula,
            placeholder="Escriba código, nombre, apellido o documento...",
            label="Buscar estudiante",
            key="buscar_estudiante_matricula"
        )

        # 1. Cuando se selecciona un estudiante en el buscador
        if seleccion_estudiante:
            resultado_est = st.session_state.get("estudiantes_encontrados_mat", {}).get(seleccion_estudiante)

            if resultado_est:
                st.session_state.mat_est_data = resultado_est
                st.session_state.id_est_mat = str(resultado_est[0])

                nombre_estudiante = f"{resultado_est[16]} {resultado_est[17]} {resultado_est[14]} {resultado_est[15]}".strip()
                st.session_state.mat_est_nom = nombre_estudiante
                st.session_state["mat_est_sin_resultados"] = False

                # 2. Validar matrícula inmediatamente para el año seleccionado
                matricula_existente = web_consultar_matricula_por_ano(
                    st.session_state.id_est_mat,
                    st.session_state.mat_ano
                )
                st.session_state["matricula_existente_actual"] = matricula_existente

        # 3. Procesar visualización si ya hay un estudiante cargado en sesión
        if st.session_state.get("mat_est_nom"):
            est = st.session_state.get("mat_est_data")

            if not est:
                st.session_state.mat_est_nom = ""
                st.rerun()

            # Sincronización si el formulario indicó refrescar
            if st.session_state.pop("refrescar_estudiante_matricula", False):
                st.session_state["mat_editando_est"] = False
                codigo = st.session_state.get("id_est_mat")
                st.session_state.pop("data_estudiantes", None)
                st.session_state.data_estudiantes = web_buscar_estudiante_dinamico("")

                for fila in st.session_state.data_estudiantes:
                    if str(fila[0]) == str(codigo):
                        st.session_state.mat_est_data = fila
                        st.session_state.mat_est_nom = f"{fila[16]} {fila[17]} {fila[14]} {fila[15]}".strip()
                        break
                st.rerun()

            # Vista exclusiva: Formulario de edición directa o Ficha Resumen
            if st.session_state.get("mat_editando_est", False):
                st.markdown("### ✏️ Editar Estudiante")
                resultado = mostrar_formulario_estudiante(modo="edicion")

                if not st.session_state.get("modo_edicion_estudiante", False):
                    codigo_estudiante = st.session_state.get("id_est_mat")
                    st.session_state.pop("data_estudiantes", None)
                    st.session_state.data_estudiantes = web_buscar_estudiante_dinamico("")

                    for fila in st.session_state.data_estudiantes:
                        if str(fila[0]) == str(codigo_estudiante):
                            st.session_state.mat_est_data = fila
                            st.session_state.mat_est_nom = f"{fila[16]} {fila[17]} {fila[14]} {fila[15]}".strip()
                            break

                    st.session_state["mat_editando_est"] = False
                    st.rerun()
            else:
                ir_a_editar = mostrar_ficha_estudiante(est)
                if ir_a_editar:
                    st.session_state["mat_editando_est"] = True
                    st.session_state["estudiante_actual"] = est
                    st.session_state["nuevo_estudiante"] = False
                    st.session_state["modo_edicion_estudiante"] = True
                    st.session_state["modo_edicion"] = True
                    cargar_estudiante_en_session(est)
                    st.rerun()
                else:
                    st.write("")

                    # Obtener estado de la matrícula almacenada
                    matricula_existente = st.session_state.get("matricula_existente_actual")

                    # =====================================================
                    # EL ESTUDIANTE YA TIENE MATRÍCULA PARA ESTE AÑO
                    # =====================================================
                    if matricula_existente:
                        st.error(
                            f"🚫 El estudiante ya tiene una matrícula registrada "
                            f"para el año lectivo {matricula_existente.get('ano_lectivo', mat_ano)}."
                        )

                        st.markdown(
                            f"""
                            <div style="
                                border: 2px solid #dc3545;
                                border-radius: 10px;
                                padding: 18px;
                                background: #fff5f5;
                                margin-top: 10px;
                                margin-bottom: 15px;
                            ">
                                <h4 style="
                                    color: #b02a37;
                                    margin-top: 0;
                                    margin-bottom: 15px;
                                ">
                                    📋 Matrícula existente
                                </h4>
                                <p style="margin: 8px 0;">
                                    <strong>📅 Año lectivo:</strong> {matricula_existente.get('ano_lectivo', '—')}
                                </p>
                                <p style="margin: 8px 0;">
                                    <strong>📌 Estado:</strong> {matricula_existente.get('estado') or '—'}
                                </p>
                                <p style="margin: 8px 0;">
                                    <strong>🏫 Sede:</strong> {matricula_existente.get('sede') or '—'}
                                </p>
                                <p style="margin: 8px 0;">
                                    <strong>⏰ Jornada:</strong> {matricula_existente.get('jornada') or '—'}
                                </p>
                                <p style="margin: 8px 0;">
                                    <strong>🎓 Grado:</strong> {matricula_existente.get('grado') or '—'}
                                </p>
                                <p style="margin: 8px 0;">
                                    <strong>👥 Grupo:</strong> {matricula_existente.get('grupo') or '—'}
                                </p>
                                <p style="margin: 8px 0;">
                                    <strong>📄 Folio:</strong> {matricula_existente.get('folio') or '—'}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.warning("⚠️ No puede crear una segunda matrícula para este estudiante en el mismo año lectivo.")

                    # =====================================================
                    # NO EXISTE MATRÍCULA → PERMITIR CONTINUAR
                    # =====================================================
                    else:
                        if st.button(
                            "Continuar →",
                            key="p1_siguiente",
                            use_container_width=True,
                            type="primary"
                        ):
                            st.session_state.mat_paso = 2
                            st.rerun()

        elif st.session_state.get("mat_est_sin_resultados"):

            st.error("❌ El estudiante no se encontró en el sistema.")

            st.write(
                "El estudiante no está registrado. "
                "Puede crearlo directamente desde Matrícula:"
            )

            if st.button(
                "➕ Registrar nuevo estudiante",
                key="p1_registrar_estudiante_desde_matricula",
                use_container_width=True,
                type="primary"
            ):

                # 1. Activar bandera de registro exclusivo desde matrícula
                st.session_state["registrando_estudiante_desde_matricula"] = True

                # 2. Configurar modo nuevo estudiante
                st.session_state["nuevo_estudiante"] = True
                st.session_state["modo_edicion_estudiante"] = True

                # 3. Limpiar variables para evitar rastros y errores de NoneType
                st.session_state["estudiante_actual"] = None
                st.session_state.mat_est_data = None
                st.session_state.mat_est_nom = ""

                # 4. GENERAR UN CÓDIGO NUEVO Y REAL (Evita que tome el primero de la BD)
                st.session_state["reg_est_id_real"] = web_generar_codigo_estudiante()

                st.rerun()
            
    # =========================================================
    # PASO 2 — Buscar acudiente, registrar si no existe y parentesco
    # =========================================================
    elif paso_actual == 2:
        if not st.session_state.get("id_est_mat") or not st.session_state.get("mat_est_data"):
            flash_set("warning", "⚠️ Primero debe seleccionar un estudiante. Regresando al Paso 1...")
            st.session_state.mat_paso = 1
            st.rerun()

        st.markdown("### 👤 Paso 2: Acudiente Responsable")
        st.info("Busque al acudiente por código, documento o nombre. Verifique su ficha, gestione sus documentos y seleccione el parentesco.")

        with st.expander("✔ Estudiante seleccionado", expanded=False):
            st.write(f"**{st.session_state.mat_est_nom}** — Código: `{st.session_state.get('id_est_mat','')}`")

        def buscar_acudientes_matricula(searchterm: str):
            if not searchterm:
                st.session_state["mat_acu_sin_resultados"] = False
                return []
            texto = searchterm.strip().lower()
            resultados = []
            st.session_state.acudientes_encontrados_mat = {}
            for r in st.session_state.data_acudientes:
                codigo = str(r[0])
                documento = str(r[2]) if len(r) > 2 else str(r[1])
                nombre_completo = f"{r[3]} {r[4]} {r[5]} {r[6]}".strip() if len(r) > 6 else f"{r[2]}".strip()
                palabras = nombre_completo.lower().split()
                coincide_nombre = any(p.startswith(texto) for p in palabras)
                coincide_documento = documento.lower().startswith(texto)
                coincide_codigo = codigo.lower().startswith(texto)
                if coincide_nombre or coincide_documento or coincide_codigo:
                    etiqueta = f"Cod: {codigo} - {documento} {nombre_completo}"
                    resultados.append(etiqueta)
                    st.session_state.acudientes_encontrados_mat[etiqueta] = r
            st.session_state["mat_acu_sin_resultados"] = len(resultados) == 0 and len(texto) > 2
            return resultados[:20]

        # Control de estado para el formulario de nuevo acudiente dentro de matrícula
        if "mat_creando_nuevo_acu" not in st.session_state:
            st.session_state.mat_creando_nuevo_acu = False

        # Función puente local para guardar desde matrícula y seleccionarlo de inmediato
        def guardar_acudiente_desde_matricula():
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
                # 1. Actualizamos la lista global de acudientes
                st.session_state.pop("data_acudientes", None)
                st.session_state.data_acudientes = web_buscar_acudiente_dinamico("")
                
                # 2. Consultamos de inmediato el acudiente recién creado por su número de documento
                acudiente_recien_creado = web_consultar_acudiente_por_documento(doc_l)
                if acudiente_recien_creado:
                    st.session_state.mat_acu_data = acudiente_recien_creado
                    st.session_state.id_acu_mat = str(acudiente_recien_creado[0])
                    p_nom = acudiente_recien_creado[3] if len(acudiente_recien_creado) > 3 else pnom_l
                    p_ape = acudiente_recien_creado[5] if len(acudiente_recien_creado) > 5 else pap_l
                    st.session_state.mat_acu_nom = f"{p_nom} {p_ape}".strip()
                    st.session_state["acudiente_actual"] = str(acudiente_recien_creado[0])

                # 3. Limpiamos el formulario y salimos del modo creación
                limpiar_formulario_acudiente()
                st.session_state.mat_creando_nuevo_acu = False
                st.success("¡Acudiente registrado y cargado con éxito!")
                st.rerun()
            else:
                st.error(mensaje)

        # 1. SI ESTÁ CREANDO UN NUEVO ACUDIENTE
        if st.session_state.mat_creando_nuevo_acu:
            st.markdown("---")
            st.markdown("### 📝 Registro de Nuevo Acudiente")
            st.write("Complete la información del padre, madre o tutor responsable.")
            
            acu_id = st.session_state.get("reg_acu_id_real", obtener_siguiente_codigo_acudiente())
            st.info(f"**Código Interno Asignado:** {acu_id}")

            # Botones de acción arriba (idéntico a tu función original)
            st.write("---")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 Guardar Nuevo Acudiente", use_container_width=True, type="primary", key="btn_guardar_acu_mat"):
                    guardar_acudiente_desde_matricula()
            with col_b2:
                if st.button("❌ Cancelar Registro", use_container_width=True, key="btn_cancelar_acu_mat"):
                    limpiar_formulario_acudiente()
                    st.session_state.mat_creando_nuevo_acu = False
                    st.rerun()
            st.write("---")

            # Cargamos los catálogos usando exactamente tu misma lógica de departamentos, municipios y sectores
            catalogos = cargar_catalogos_acudiente(
                st.session_state["reg_acu_depto"][0] if st.session_state.get("reg_acu_depto") else None
            )

            # Renderizamos el formulario completo respetando tu estructura exacta
            st.markdown("### 📋 1. Identificación")
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox(
                    "Tipo de documento*",
                    options=catalogos["tipos_documento"],
                    format_func=lambda x: f"{x[1]} - {x[2]}",
                    index=None if not st.session_state.get("reg_acu_tipo_doc") else catalogos["tipos_documento"].index(st.session_state["reg_acu_tipo_doc"]) if st.session_state["reg_acu_tipo_doc"] in catalogos["tipos_documento"] else None,
                    placeholder="Seleccione tipo de documento...",
                    key="reg_acu_tipo_doc"
                )
            with col2:
                st.text_input("Número de documento*", key="reg_acu_num_doc", placeholder="Ingrese número de documento...")

            col3, col4 = st.columns(2)
            with col3:
                st.text_input("Primer nombre*", key="reg_acu_pnom")
            with col4:
                st.text_input("Segundo nombre", key="reg_acu_snom")

            col5, col6 = st.columns(2)
            with col5:
                st.text_input("Primer apellido*", key="reg_acu_pap")
            with col6:
                st.text_input("Segundo apellido", key="reg_acu_sap")

            min_date = datetime.date(1930, 1, 1)
            max_date = datetime.date.today()
            st.date_input("Fecha de nacimiento*", min_value=min_date, max_value=max_date, format="DD/MM/YYYY", key="reg_acu_fecha")

            col7, col8 = st.columns(2)
            with col7:
                st.selectbox(
                    "Departamento de nacimiento*",
                    options=catalogos["departamentos"],
                    format_func=lambda x: x[2],
                    index=None if not st.session_state.get("reg_acu_depto") else catalogos["departamentos"].index(st.session_state["reg_acu_depto"]) if st.session_state["reg_acu_depto"] in catalogos["departamentos"] else None,
                    placeholder="Seleccione departamento...",
                    key="reg_acu_depto"
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
                        key="reg_acu_municipio"
                    )
                else:
                    st.selectbox("Municipio de nacimiento*", options=[], index=None, placeholder="Seleccione primero un departamento...", key="reg_acu_municipio_vacio", disabled=True)

            st.write("---")
            st.markdown("### 📞 2. Información de Contacto")
            col9, col10 = st.columns(2)
            with col9:
                st.text_input("Teléfono Principal*", key="reg_acu_tel")
                st.text_input("Dirección de Residencia", key="reg_acu_dir")
                st.selectbox(
                    "Barrio / Vereda / Corregimiento*",
                    options=catalogos["sectores"],
                    format_func=lambda x: f"{x[1]} ({x[2]})",
                    index=None if not st.session_state.get("reg_acu_sector") else catalogos["sectores"].index(st.session_state["reg_acu_sector"]) if st.session_state["reg_acu_sector"] in catalogos["sectores"] else None,
                    placeholder="Seleccione un sector...",
                    key="reg_acu_sector"
                )
            with col10:
                st.text_input("Correo Electrónico", key="reg_acu_correo")
                st.text_input("Ocupación", key="reg_acu_ocupacion")
                st.text_area("Observaciones", height=80, key="reg_acu_obs")

            st.info("💡 El parentesco (mamá, papá, tío…) se registra en la matrícula, ya que puede cambiar cada año lectivo.")

        # 2. SI NO ESTÁ CREANDO, MUESTRA EL BUSCADOR NORMAL
        if not st.session_state.mat_creando_nuevo_acu:
            col_busqueda, col_btn_nuevo = st.columns([4, 1])
            
            with col_busqueda:
                seleccion_acudiente = st_searchbox(
                    buscar_acudientes_matricula,
                    placeholder="Escriba código, nombre, apellido o documento...",
                    label="Buscar acudiente",
                    key="buscar_acudiente_matricula"
                )
                
            with col_btn_nuevo:
                st.markdown("<br>", unsafe_allow_html=True) 
                if st.button("➕ Nuevo", use_container_width=True, help="Registrar un acudiente nuevo"):
                    limpiar_formulario_acudiente()
                    st.session_state.mat_creando_nuevo_acu = True
                    st.rerun()

            if seleccion_acudiente:
                resultado_acu = st.session_state.get("acudientes_encontrados_mat", {}).get(seleccion_acudiente)
                if resultado_acu:
                    st.session_state.id_acu_mat = str(resultado_acu[0])
                    acudiente_completo = web_consultar_acudiente_por_documento(resultado_acu[2])
                    if acudiente_completo:
                        st.session_state.mat_acu_data = acudiente_completo
                        p_nom = acudiente_completo[3] if len(acudiente_completo) > 3 else ""
                        p_ape = acudiente_completo[5] if len(acudiente_completo) > 5 else ""
                        st.session_state.mat_acu_nom = f"{p_nom} {p_ape}".strip()
                        st.session_state["acudiente_actual"] = str(resultado_acu[0])
                    st.session_state["mat_acu_sin_resultados"] = False

            elif st.session_state.get("mat_acu_sin_resultados"):
                st.warning("⚠️ No se encontró ningún acudiente con ese criterio.")
                if st.button("➕ Registrar nuevo acudiente aquí", key="btn_crear_acu_mat_inline", type="primary"):
                    limpiar_formulario_acudiente()
                    st.session_state.mat_creando_nuevo_acu = True
                    st.rerun()

        # 3. SI YA HAY UN ACUDIENTE SELECCIONADO Y CARGADO
        if st.session_state.get("mat_acu_nom") and not st.session_state.mat_creando_nuevo_acu:
            acu = st.session_state.get("mat_acu_data")
            if not acu:
                st.session_state.mat_acu_nom = ""
                st.rerun()

            # Pestañas operativas: Ficha del Acudiente y Documentos del Acudiente
            tab_ficha_acu, tab_docs_acu = st.tabs(["📋 Ficha del Acudiente", "📄 Documentos del Acudiente"])

            with tab_ficha_acu:
                if st.session_state.get("mat_editando_acu", False):
                    if not st.session_state.get("modo_edicion", True) or not st.session_state.get("modo_edicion_acudiente", True):
                        st.session_state["mat_editando_acu"] = False
                        st.rerun()

                if st.session_state.get("mat_editando_acu", False):
                    st.markdown("### ✏️ Editar Acudiente")
                    mostrar_formulario_acudiente(modo="edicion")
                else:
                    ir_a_editar_acu = mostrar_ficha_acudiente(acu)
                    if ir_a_editar_acu:
                        st.session_state["mat_editando_acu"] = True
                        st.session_state["acudiente_actual"] = acu
                        st.session_state["nuevo_acudiente"] = False
                        st.session_state["modo_edicion"] = True
                        st.session_state["modo_edicion_acudiente"] = True

                        acu_mod = list(acu)
                        while len(acu_mod) < 30:
                            acu_mod.append("")

                        cargar_acudiente_en_session(acu_mod)
                        st.rerun()
                    else:
                        st.write("")
                        parentescos = [
                            "Padre", "Madre", "Abuelo", "Abuela", "Hermano", "Hermana",
                            "Tío", "Tía", "Primo", "Prima", "Padrastro", "Madrastra",
                            "Bisabuelo", "Bisabuela", "Esposo", "Esposa", "Tutor",
                            "Representante legal", "Cuidador", "Otro"
                        ]
                        idx_par = parentescos.index(st.session_state.get("mat_parentesco", "Madre")) if st.session_state.get("mat_parentesco") in parentescos else 1
                        mat_parentesco = st.selectbox("Parentesco del acudiente con el estudiante*", parentescos, index=idx_par)
                        st.session_state.mat_parentesco = mat_parentesco

            with tab_docs_acu:
                st.markdown("### 📂 Documentación del Acudiente")
                id_acu_actual = str(st.session_state.get("id_acu_mat", ""))
                
                if id_acu_actual:
                    documentos_acu = web_obtener_documentos_acudiente(id_acu_actual)
                    if documentos_acu:
                        for doc in documentos_acu:
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

                    st.markdown("#### 📤 Subir nuevo documento al acudiente")
                    with st.form(key="form_subir_doc_acudiente_mat", clear_on_submit=True):
                        nombre_doc_input = st.text_input("Nombre o tipo de documento (ej. Cédula, Certificado)")
                        archivo_subido = st.file_uploader("Seleccionar archivo (PDF o Imagen)", type=["pdf", "png", "jpg", "jpeg"])
                        
                        subir_btn = st.form_submit_button("Subir documento", type="primary")
                        if subir_btn:
                            if archivo_subido and nombre_doc_input:
                                with st.spinner("Subiendo a Google Drive y guardando..."):
                                    exito, mensaje = web_guardar_documento_acudiente(
                                        id_acudiente=id_acu_actual,
                                        tipo_documento=nombre_doc_input,
                                        archivo_subido=archivo_subido
                                    )
                                    if exito:
                                        st.success(f"✅ {mensaje}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {mensaje}")
                            else:
                                st.warning("⚠️ Ingrese el tipo de documento y seleccione un archivo.")

        st.divider()
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← Volver al Paso 1", key="p2_volver", use_container_width=True):
                st.session_state.mat_paso = 1
                st.rerun()
        with col_nav2:
            if st.button("Continuar al Paso 3 →", key="p2_siguiente", use_container_width=True, type="primary"):
                st.session_state.mat_paso = 3
                st.rerun()

   # =========================================================
    # PASO 3 — Datos académicos y administrativos
    # =========================================================
    elif paso_actual == 3:
        if not st.session_state.get("id_est_mat") or not st.session_state.get("mat_est_data"):
            flash_set("warning", "⚠️ Falta el estudiante. Regresando al Paso 1...")
            st.session_state.mat_paso = 1
            st.rerun()
        if not st.session_state.get("id_acu_mat") or not st.session_state.get("mat_acu_data"):
            flash_set("warning", "⚠️ Falta el acudiente. Regresando al Paso 2...")
            st.session_state.mat_paso = 2
            st.rerun()

        st.markdown("### 📑 Paso 3: Datos Académicos y Administrativos")
        st.info("Configure la información institucional y de grados para la matrícula.")

        with st.expander("👤 Ver resumen del Estudiante y Acudiente seleccionados", expanded=False):
            st.write(f"**Estudiante:** {st.session_state.mat_est_nom} — Código: `{st.session_state.get('id_est_mat','')}`")
            st.write(f"**Acudiente:** {st.session_state.mat_acu_nom} — Parentesco: {st.session_state.get('mat_parentesco','')}")

        # ── Cargar catálogos enriquecidos ─────────────────────────────────────
        grados_detalle = web_obtener_grados_con_detalle()  # [{id_grado, nombre_grado, nivel, orden}, ...]
        cursos_list    = web_obtener_cursos_completo()      # [{id_curso, grado, grupo, sede, jornada}, ...]

        if not grados_detalle:
            st.error("❌ No se pudieron cargar los grados. Verifique la conexión.")
            st.stop()

        # 1. Crear un mapa para saber a qué nivel pertenece cada nombre de grado (Ej: "Primero" -> "PRIMARIA")
        mapa_grado_nivel = {g["nombre_grado"].strip().lower(): str(g.get("nivel", "")).strip().lower() for g in grados_detalle}

        # 2. Extraer niveles únicos limpios para el selectbox
        niveles_disponibles = sorted(list(set(str(g.get("nivel", "")).strip() for g in grados_detalle if g.get("nivel"))))

        with st.container(border=True):
            st.markdown("##### 🏫 Configuración Académica y de Grado")
            
            col_adm1, col_adm2 = st.columns(2)
            with col_adm1:
                mat_ano = st.selectbox("📅 Año Lectivo*", [2026, 2027], index=0, key="mat_p3_ano")
                st.session_state.mat_ano = mat_ano
            with col_adm2:
                # Selector de Nivel Educativo
                mat_nivel = st.selectbox("🎓 Nivel Educativo*", niveles_disponibles, key="mat_p3_nivel")
                st.session_state.mat_nivel = mat_nivel

            # 3. Filtrar cursos cuyo campo 'grado' pertenezca al nivel seleccionado
            nivel_sel_lower = str(mat_nivel).strip().lower()
            cursos_filtrados = []
            for c in cursos_list:
                nombre_g_curso = str(c.get("grado", "")).strip().lower()
                nivel_del_grado = mapa_grado_nivel.get(nombre_g_curso, "")
                if nivel_del_grado == nivel_sel_lower:
                    cursos_filtrados.append(c)

            # 4. Mapear etiqueta amigable -> id_curso real
            mapa_cursos = {
                f"{c.get('grado', 'Grado')} - Grupo {c.get('grupo', '')} ({c.get('sede', '')} - {c.get('jornada', '')})": c['id_curso']
                for c in cursos_filtrados
            }

            st.write("")
            if mapa_cursos:
                opts_curso = list(mapa_cursos.keys())
                idx_cur = 0
                if st.session_state.get("mat_curso_label") in opts_curso:
                    idx_cur = opts_curso.index(st.session_state.get("mat_curso_label"))

                mat_curso_label = st.selectbox("📚 Curso / Grupo Asignado*", opts_curso, index=idx_cur, key="mat_p3_curso_label")
                st.session_state.mat_curso_label = mat_curso_label
                
                mat_curso_id = mapa_cursos[mat_curso_label]
                st.session_state.mat_curso = mat_curso_id

                curso_obj = next((c for c in cursos_filtrados if c['id_curso'] == mat_curso_id), None)
                if curso_obj:
                    st.session_state.mat_sede = curso_obj.get('sede', '')
                    st.session_state.mat_jornada = curso_obj.get('jornada', '')
                    st.info(f"📍 **Sede heredada del grupo:** {curso_obj.get('sede', '')}  |  ⏰ **Jornada:** {curso_obj.get('jornada', '')}")
            else:
                st.warning(f"⚠️ No hay grupos registrados para el nivel **{mat_nivel}**. Créelos primero en 'Gestionar Grupos'.")
                st.session_state.mat_curso = None
                st.session_state.mat_sede = ""
                st.session_state.mat_jornada = ""

            st.markdown("---")
            st.markdown("##### 📋 Estado y Fechas del Registro")

            col_adm5, col_adm6 = st.columns(2)
            with col_adm5:
                estados = ["Matriculado", "Inscrito", "Trasladado", "Retirado"]
                idx_est = estados.index(st.session_state.get("mat_estado", "Matriculado")) if st.session_state.get("mat_estado") in estados else 0
                mat_estado = st.selectbox("📌 Estado Actual*", estados, index=idx_est, key="mat_p3_estado")
                st.session_state.mat_estado = mat_estado
            with col_adm6:
                mat_fecha = st.date_input("📆 Fecha de Matrícula*", value=st.session_state.get("mat_fecha", date.today()), format="DD/MM/YYYY", key="mat_p3_fecha")
                st.session_state.mat_fecha = mat_fecha

            st.write("")
            mat_observaciones = st.text_area(
                "📝 Observaciones (opcional)",
                value=st.session_state.get("mat_observaciones", ""),
                placeholder="Ingrese cualquier novedad, condición médica o observación relevante...",
                key="mat_p3_observaciones"
            )
            st.session_state.mat_observaciones = mat_observaciones

        st.write("")
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← Volver", key="p3_volver", use_container_width=True):
                st.session_state.mat_paso = 2
                st.rerun()
        with col_nav2:
            if st.session_state.get("mat_curso"):
                if st.button("Repositorio Documental →", key="p3_siguiente", use_container_width=True, type="primary"):
                    st.session_state.mat_paso = 4
                    st.rerun()
            else:
                st.warning("Seleccione un curso válido para continuar.")

    # =========================================================
    # PASO 4 — Repositorio Documental de Matrícula
    # =========================================================
    elif paso_actual == 4:
        id_est = st.session_state.get("id_est_mat")
        if not id_est or not st.session_state.get("mat_est_data"):
            flash_set("warning", "⚠️ Falta el estudiante. Regresando al Paso 1...")
            st.session_state.mat_paso = 1
            st.rerun()

        st.markdown("### 📁 Paso 4: Repositorio Documental")
        st.info("Cargue los documentos obligatorios de soporte para este proceso de matrícula.")

        with st.expander("👤 Ver estudiante en proceso", expanded=False):
            st.write(f"**Estudiante:** {st.session_state.mat_est_nom} — Código: `{id_est}`")

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
                key=f"tipo_mat_{id_est}"
            )

        with col2:
            archivo = st.file_uploader(
                "Seleccionar documento",
                type=["pdf", "jpg", "jpeg", "png"],
                key=f"doc_mat_{id_est}"
            )

            st.write("")
            subir = st.button("📤 Subir documento", use_container_width=True, key=f"subir_mat_{id_est}")

        if subir:
            if archivo is None:
                st.warning("Seleccione un documento.")
            else:
                drive = DriveManager()
                carpeta_estudiante = drive.obtener_carpeta_estudiante(id_est)

                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo.name)[1]) as temp:
                    temp.write(archivo.getbuffer())
                    ruta_temporal = temp.name

                resultado = drive.subir_archivo(ruta_temporal, archivo.name, carpeta_estudiante)

                guardar_documento(
                    id_estudiante=id_est,
                    tipo_documento=tipo,
                    nombre_archivo=archivo.name,
                    drive_id=resultado["id"],
                    drive_url=resultado["webViewLink"],
                    carpeta_drive=carpeta_estudiante
                )

                os.remove(ruta_temporal)
                st.success("Documento cargado correctamente.")
                st.rerun()

        st.divider()

        documentos = obtener_documentos_estudiante(id_est)

        if not documentos:
            st.info("Este estudiante aún no tiene documentos registrados en este proceso.")
        else:
            col_t1, col_t2, col_t3 = st.columns([8, 1.2, 1.2])
            with col_t1:
                st.subheader("📁 Documentos registrados")
            with col_t2:
                st.markdown("<center><b>Ver</b></center>", unsafe_allow_html=True)
            with col_t3:
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
                        st.link_button("👁️", url_drive, use_container_width=True, key=f"link_ver_mat_{doc[0]}")
                    else:
                        st.button("👁️", key=f"ver_disabled_mat_{doc[0]}", disabled=True, use_container_width=True)

                with col_d3:
                    if st.button("🗑️", key=f"eliminar_doc_mat_{doc[0]}", use_container_width=True):
                        # Opcional: Aquí puedes agregar tu lógica para eliminar el documento si ya la tienes en la app
                        st.warning("Función de eliminar pendiente de confirmar.")
                st.markdown("---")

        st.write("")
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← Volver a Académico", key="p4_volver", use_container_width=True):
                st.session_state.mat_paso = 3
                st.rerun()
        with col_nav2:
            if st.button("Revisar y confirmar →", key="p4_siguiente", use_container_width=True, type="primary"):
                st.session_state.mat_paso = 5  # Te lleva al último paso de confirmación
                st.rerun()




    # =========================================================
    # PASO 5 — Resumen y confirmación
    # =========================================================
    elif paso_actual == 5:
        if not st.session_state.get("id_est_mat") or not st.session_state.get("mat_est_data"):
            flash_set("warning", "⚠️ Falta el estudiante. Regresando al Paso 1...")
            st.session_state.mat_paso = 1
            st.rerun()
        if not st.session_state.get("id_acu_mat") or not st.session_state.get("mat_acu_data"):
            flash_set("warning", "⚠️ Falta el acudiente. Regresando al Paso 2...")
            st.session_state.mat_paso = 2
            st.rerun()
        if not st.session_state.get("mat_curso") or not st.session_state.get("mat_sede"):
            flash_set("warning", "⚠️ Faltan datos académicos. Regresando al Paso 3...")
            st.session_state.mat_paso = 3
            st.rerun()

        st.markdown("### ✅ Paso 4: Revisar y Confirmar la Matrícula")
        st.info("Verifique todos los datos antes de guardar la matrícula de forma definitiva.")

        folio_generado = web_generar_folio_matricula(st.session_state.get("mat_ano", 2026))

        # Función auxiliar para renderizar cada tarjeta de resumen con icono
        def tarjeta_resumen(icon, label, value):
            return f"""
            <div style="
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 14px;
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            ">
                <div style="
                    background: #e2e8f0;
                    border-radius: 6px;
                    width: 36px;
                    height: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 12px;
                    flex-shrink: 0;
                    font-size: 18px;
                ">
                    {icon}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-size: 12px; color: #64748b; font-weight: 500;">{label}</div>
                    <div style="font-size: 14px; color: #1e293b; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{value}</div>
                </div>
            </div>
            """

        with st.container(border=True):
            # Tarjeta destacada para el Folio
            st.markdown(
                f"""
                <div style="
                    background: #e1effe;
                    border-left: 6px solid #0d6efd;
                    padding: 12px 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <div style="font-size: 16px; font-weight: 700; color: #1e40af;">
                        🗂 Folio Asignado
                    </div>
                    <div style="font-size: 18px; font-weight: 800; color: #1d4ed8;">
                        {folio_generado or '⚠ Error al generar'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("##### 👨‍🎓 Información del Estudiante")
                st.markdown(tarjeta_resumen("👤", "Nombre", st.session_state.mat_est_nom), unsafe_allow_html=True)
                st.markdown(tarjeta_resumen("🆔", "Código", str(st.session_state.get('id_est_mat', '—'))), unsafe_allow_html=True)
                if st.session_state.get("mat_est_data"):
                    est = st.session_state.mat_est_data
                    st.markdown(tarjeta_resumen("📄", "Documento", f"{est[1]} {est[2]}"), unsafe_allow_html=True)

            with col_r2:
                st.markdown("##### 👤 Información del Acudiente")
                st.markdown(tarjeta_resumen("👤", "Nombre", st.session_state.mat_acu_nom), unsafe_allow_html=True)
                st.markdown(tarjeta_resumen("🆔", "Código", str(st.session_state.get('id_acu_mat', '—'))), unsafe_allow_html=True)
                st.markdown(tarjeta_resumen("🤝", "Parentesco", str(st.session_state.get('mat_parentesco', '—'))), unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 📚 Datos Académicos y Administrativos")
            
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                st.markdown(tarjeta_resumen("📅", "Año Lectivo", str(st.session_state.get('mat_ano', '—'))), unsafe_allow_html=True)
                st.markdown(tarjeta_resumen("📚", "Curso Asignado", str(st.session_state.get('mat_curso', '—'))), unsafe_allow_html=True)
            with ac2:
                st.markdown(tarjeta_resumen("🏫", "Sede Educativa", str(st.session_state.get('mat_sede', '—'))), unsafe_allow_html=True)
                st.markdown(tarjeta_resumen("📋", "Estado Actual", str(st.session_state.get('mat_estado', '—'))), unsafe_allow_html=True)
            with ac3:
                st.markdown(tarjeta_resumen("⏰", "Jornada", str(st.session_state.get('mat_jornada', '—'))), unsafe_allow_html=True)
                st.markdown(tarjeta_resumen("📆", "Fecha de Matrícula", str(st.session_state.get('mat_fecha', '—'))), unsafe_allow_html=True)

            obs_val = st.session_state.get("mat_observaciones", "").strip()
            if obs_val:
                st.markdown(tarjeta_resumen("📝", "Observaciones", obs_val), unsafe_allow_html=True)

        st.markdown("---")

        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← Volver y corregir", key="p4_volver", use_container_width=True):
                st.session_state.mat_paso = 3
                st.rerun()
        with col_nav2:
            boton_guardar_mat = st.button("💾 Guardar Matrícula", key="p4_guardar", use_container_width=True, type="primary")

        if boton_guardar_mat:
            est_c = st.session_state.get("id_est_mat", "")
            acu_c = st.session_state.get("id_acu_mat", "")
            folio_l = (folio_generado or "").strip()

            if not folio_l:
                st.error("❌ No se pudo generar el folio. Verifique la conexión a la base de datos.")
            elif not est_c:
                st.error("❌ Falta el estudiante. Regrese al Paso 1.")
            elif not acu_c:
                st.error("❌ Falta el acudiente. Regrese al Paso 2.")
            else:
                with st.spinner("Registrando matrícula en el sistema institucional..."):
                    exito, mensaje = web_registrar_matricula(
                        est_c, acu_c, folio_l,
                        st.session_state.mat_ano,
                        st.session_state.mat_fecha,
                        st.session_state.mat_parentesco,
                        st.session_state.mat_sede,
                        st.session_state.mat_jornada,
                        st.session_state.mat_estado,
                        st.session_state.mat_curso,
                        "INST-DICA",
                        st.session_state.get("mat_observaciones")
                    )
                if exito:
                    st.session_state["mat_registro_exitoso"] = mensaje
                    claves_limpiar = [
                        "id_est_mat", "id_acu_mat", "mat_est_nom", "mat_acu_nom",
                        "mat_est_data", "mat_acu_data", "mat_paso", "mat_parentesco",
                        "mat_ano", "mat_sede", "mat_jornada", "mat_curso",
                        "mat_estado", "mat_fecha", "mat_observaciones",
                        "mat_est_sin_resultados", "mat_acu_sin_resultados"
                    ]
                    for clave in claves_limpiar:
                        if clave in st.session_state:
                            del st.session_state[clave]
                    st.rerun()
                else:
                    st.error(f"❌ {mensaje}")

def gestionar_matriculas():    
    st.title("📋 Gestionar Matrículas")
    st.write("Consulte, filtre y cambie el estado de las matrículas registradas.")

    ESTADOS_MATRICULA = ["Matriculado", "Inscrito", "Trasladado", "Retirado", "Anulado"]
    ESTADO_COLOR = {
        "Matriculado": "🟢",
        "Inscrito":    "🔵",
        "Trasladado":  "🟡",
        "Retirado":    "🟠",
        "Anulado":     "🔴",
    }

    st.markdown("### 🔍 Filtros de búsqueda")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        gm_ano = st.number_input("Año lectivo", min_value=2000, max_value=2100,
                                  value=date.today().year, step=1, key="gm_ano")
    with fc2:
        # Cargamos los cursos en caché una sola vez (ya sin depender del año)
        if "gm_cursos_cache" not in st.session_state:
            st.session_state.gm_cursos_cache = web_obtener_cursos_completo()
            
        cursos_disponibles = st.session_state.gm_cursos_cache
        opciones_curso = {"Todos los grupos": None}
        for c in cursos_disponibles:
            grado_corto = abreviar_grado(c['grado'])
            # Formato sintetizado: 5-02 (ID)
            label = f"{grado_corto}-{c['grupo']} ({c['id_curso']})"
            opciones_curso[label] = c["id_curso"]
            
        sel_curso_label = st.selectbox("Grupo", list(opciones_curso.keys()), key="gm_curso")
        gm_id_curso = opciones_curso[sel_curso_label]
    with fc3:
        opciones_estado = ["Todos los estados"] + ESTADOS_MATRICULA
        sel_estado = st.selectbox("Estado", opciones_estado, key="gm_estado")
        gm_estado = None if sel_estado == "Todos los estados" else sel_estado

    col_bus, col_ref = st.columns([3, 1])
    with col_bus:
        btn_buscar = st.button("🔍 Buscar matrículas", use_container_width=True,
                                key="gm_buscar", type="primary")
    with col_ref:
        if st.button("🔄 Limpiar", use_container_width=True, key="gm_limpiar"):
            for k in ["gm_resultados", "gm_edit_id", "gm_confirm_id"]:
                st.session_state.pop(k, None)
            st.rerun()

    if btn_buscar:
        with st.spinner("Buscando..."):
            st.session_state["gm_resultados"] = web_buscar_matriculas(
                ano_lectivo=int(gm_ano),
                id_curso=gm_id_curso,
                estado=gm_estado
            )
        st.session_state.pop("gm_edit_id", None)
        st.session_state.pop("gm_confirm_id", None)

    resultados = st.session_state.get("gm_resultados")

    if resultados is None:
        st.info("Configure los filtros y haga clic en **Buscar matrículas**.")
    elif len(resultados) == 0:
        st.warning("No se encontraron matrículas con los filtros seleccionados.")
    else:
        st.write("---")
        st.markdown(f"### 📄 Resultados — {len(resultados)} matrícula(s)")

        ids_res = {r["id_matricula"] for r in resultados}
        if st.session_state.get("gm_edit_id") not in ids_res:
            st.session_state.pop("gm_edit_id", None)
        if st.session_state.get("gm_confirm_id") not in ids_res:
            st.session_state.pop("gm_confirm_id", None)

        # Iteramos cada resultado creando una tarjeta visual optimizada
        for r in resultados:
            mid = r["id_matricula"]

            # Contenedor tipo tarjeta para cada estudiante
            with st.container(border=True):
                col_foto, col_info, col_estado, col_acciones = st.columns([1, 4, 2, 2])

                # 1. Columna de la Foto del estudiante
                # 1. Columna de la Foto del estudiante (desde Google Drive)
                # 1. Columna de la Foto del estudiante (Adaptada para Google Drive)
                # 1. Columna de la Foto del estudiante (Método robusto igual al de la ficha de matrícula)
                with col_foto:
                    foto_url = r.get("foto_url")
                    
                    def obtener_url_imagen_drive(url):
                        if not url:
                            return None
                        url_str = str(url).strip()
                        if not url_str or url_str.lower() == "none":
                            return None
                            
                        # Si ya es una URL directa (como lh3 o una imagen web externa)
                        if "lh3.googleusercontent.com" in url_str or "http" in url_str and not "drive.google.com" in url_str:
                            return url_str
                            
                        file_id = None
                        try:
                            # Formato 1: /file/d/ID/view o /file/d/ID/edit
                            if "/file/d/" in url_str:
                                file_id = url_str.split("/file/d/")[1].split("/")[0]
                            # Formato 2: ?id=ID o &id=ID
                            elif "id=" in url_str:
                                partes = url_str.split("id=")
                                file_id = partes[1].split("&")[0]
                            # Formato 3: Si guardaron directamente el ID del archivo en crudo
                            elif len(url_str) > 20 and "/" not in url_str:
                                file_id = url_str
                                
                            if file_id:
                                # Usamos el endpoint de visualización directa de Google
                                return f"https://lh3.googleusercontent.com/d/{file_id}"
                        except Exception:
                            pass
                            
                        return url_str if url_str.startswith("http") else None

                    url_final = obtener_url_imagen_drive(foto_url)

                    if url_final:
                        try:
                            st.image(url_final, width=65)
                        except Exception:
                            st.markdown("<div style='font-size: 35px; text-align: center;'>👤</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='font-size: 35px; text-align: center;'>👤</div>", unsafe_allow_html=True)
                # 
                # 2. Información principal resumida con grado abreviado (ej: 5-02)
                with col_info:
                    st.markdown(f"**{r['nombre_estudiante']}**")
                    grado_corto = abreviar_grado(r.get('nombre_grado', ''))
                    grupo_num = r.get('grupo', '')
                    st.caption(f"Folio: `{r['folio']}` | Grupo: **{grado_corto}-{grupo_num}** | Año: {r['ano_lectivo']}")
                    
                    if r.get("observaciones"):
                        st.caption(f"📝 {r['observaciones']}")

                # 3. Estado con su respectivo ícono de color
                with col_estado:
                    icono = ESTADO_COLOR.get(r["estado"], "⚪")
                    st.markdown(f"{icono} **{r['estado']}**")

                # 4. Botones de acción compactos (Editar / Anular)
                with col_acciones:
                    b_edit, b_del = st.columns(2)
                    if b_edit.button("✏️", key=f"gm_edit_{mid}", help="Cambiar estado de matrícula"):
                        st.session_state["gm_edit_id"] = mid
                        st.rerun()
                    if b_del.button("🗑️", key=f"gm_del_{mid}", help="Anular matrícula"):
                        st.session_state["gm_confirm_id"] = mid
                        st.rerun()

            # --- Formulario desplegable si se hizo clic en Editar (✏️) ---
            if st.session_state.get("gm_edit_id") == mid:
                with st.container(border=True):
                    st.markdown(f"**✏️ Cambiar estado — Folio {r['folio']} · {r['nombre_estudiante']}**")
                    ec1, ec2 = st.columns([2, 3])
                    with ec1:
                        idx_actual = ESTADOS_MATRICULA.index(r["estado"]) if r["estado"] in ESTADOS_MATRICULA else 0
                        nuevo_estado = st.selectbox("Nuevo estado*", ESTADOS_MATRICULA, index=idx_actual, key=f"gm_ns_{mid}")
                    with ec2:
                        observacion = st.text_input("Observación (opcional)", value=r.get("observaciones") or "", key=f"gm_obs_{mid}")
                    
                    ba1, ba2 = st.columns(2)
                    if ba1.button("💾 Guardar cambio", key=f"gm_save_{mid}", use_container_width=True, type="primary"):
                        ok, msg = web_actualizar_estado_matricula(mid, nuevo_estado, observacion.strip() if observacion.strip() else None)
                        if ok:
                            flash_set("success", f"✅ {msg}")
                        else:
                            flash_set("error", f"❌ {msg}")
                        st.session_state.pop("gm_edit_id", None)
                        st.session_state.pop("gm_resultados", None)
                        st.rerun()
                    if ba2.button("✖ Cancelar", key=f"gm_cancel_{mid}", use_container_width=True):
                        st.session_state.pop("gm_edit_id", None)
                        st.rerun()

            # --- Formulario desplegable si se hizo clic en Anular (🗑️) ---
            if st.session_state.get("gm_confirm_id") == mid:
                with st.container(border=True):
                    st.warning(f"⚠️ ¿Anular la matrícula **{r['folio']}** de **{r['nombre_estudiante']}**? Esto cambiará el estado a **Anulado**.")
                    cc1, cc2 = st.columns(2)
                    obs_anul = cc1.text_input("Motivo de anulación (opcional)", key=f"gm_obs_anul_{mid}")
                    
                    if cc1.button("🗑️ Sí, anular", key=f"gm_anular_{mid}", use_container_width=True, type="primary"):
                        ok, msg = web_actualizar_estado_matricula(mid, "Anulado", obs_anul.strip() if obs_anul.strip() else None)
                        if ok:
                            flash_set("success", f"✅ {msg}")
                        else:
                            flash_set("error", f"❌ {msg}")
                        st.session_state.pop("gm_confirm_id", None)
                        st.session_state.pop("gm_resultados", None)
                        st.rerun()
                    if cc2.button("✖ Cancelar", key=f"gm_anul_cancel_{mid}", use_container_width=True):
                        st.session_state.pop("gm_confirm_id", None)
                        st.rerun()

        # Resumen inferior de contadores limpio
        st.write("---")
        from collections import Counter
        resumen = Counter(r.get("estado", "Desconocido") for r in resultados)
        cols_res = st.columns(len(resumen) if len(resumen) > 0 else 1)
        for col, (estado, cnt) in zip(cols_res, resumen.items()):
            icono = ESTADO_COLOR.get(estado, "⚪")
            col.metric(f"{icono} {estado}", cnt)