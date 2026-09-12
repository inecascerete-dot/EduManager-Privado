import os

import streamlit as st

from backend.config import (
    ID_INSTITUCION,
    RUTA_INSTITUCION,
    NOMBRE_LOGO,
    NOMBRE_ESCUDO,
)

from backend.institucion_db import (
    web_obtener_institucion,
    web_actualizar_institucion
)

from backend.catalogos_db import (
    obtener_departamentos,
    obtener_municipios,
)


def obtener_carpeta_institucion(id_institucion):
    """Devuelve/crea la carpeta de recursos de la institución."""
    carpeta = os.path.join(
        "assets",
        "instituciones",
        str(id_institucion),
    )

    os.makedirs(carpeta, exist_ok=True)

    return carpeta


def _cargar_catalogo_departamentos():
    """
    Carga los departamentos y crea:
        - nombres: lista para mostrar en el selectbox.
        - por_nombre: nombre -> ID.
        - por_id: ID -> nombre.
    """
    departamentos = obtener_departamentos() or []

    por_nombre = {}
    por_id = {}

    for departamento in departamentos:
        if len(departamento) < 3:
            continue

        id_departamento = departamento[0]
        nombre = str(departamento[2]).strip()

        if not nombre:
            continue

        por_nombre[nombre] = id_departamento
        por_id[str(id_departamento)] = nombre

    return {
        "nombres": list(por_nombre.keys()),
        "por_nombre": por_nombre,
        "por_id": por_id,
    }


def _cargar_catalogo_municipios(id_departamento):
    """
    Carga los municipios correspondientes al departamento seleccionado.
    """
    if not id_departamento:
        return {
            "nombres": [],
            "por_nombre": {},
            "por_id": {},
        }

    municipios = obtener_municipios(id_departamento) or []

    por_nombre = {}
    por_id = {}

    for municipio in municipios:
        if len(municipio) < 3:
            continue

        id_municipio = municipio[0]
        nombre = str(municipio[2]).strip()

        if not nombre:
            continue

        por_nombre[nombre] = id_municipio
        por_id[str(id_municipio)] = nombre

    return {
        "nombres": list(por_nombre.keys()),
        "por_nombre": por_nombre,
        "por_id": por_id,
    }


def _guardar_institucion(
    datos,
    nombre=None,
    nit=None,
    resolucion=None,
    direccion=None,
    telefono=None,
    id_municipio=None,
    id_departamento=None,
    email=None,
    rector=None,
    correo_rector=None,
    mision=None,
    vision=None,
    logo_url=None,
    eslogan=None,
    escudo_url=None,
):
    """
    Guarda la institución utilizando los nuevos campos:
        id_departamento
        id_municipio

    Los demás datos se conservan de la ficha actual cuando no se
    modifican desde la pestaña correspondiente.
    """

    nombre = datos["nombre_institucion"] if nombre is None else nombre
    nit = datos["nit_dane"] if nit is None else nit
    resolucion = (
        datos["resolucion_aprobacion"]
        if resolucion is None
        else resolucion
    )
    direccion = (
        datos["direccion_principal"]
        if direccion is None
        else direccion
    )
    telefono = (
        datos["telefono_principal"]
        if telefono is None
        else telefono
    )
    id_municipio = (
        datos.get("id_municipio")
        if id_municipio is None
        else id_municipio
    )
    id_departamento = (
        datos.get("id_departamento")
        if id_departamento is None
        else id_departamento
    )
    email = (
        datos["email_institucional"]
        if email is None
        else email
    )
    rector = (
        datos["nombre_rector"]
        if rector is None
        else rector
    )
    correo_rector = (
        datos["correo_rector"]
        if correo_rector is None
        else correo_rector
    )
    mision = datos["mision"] if mision is None else mision
    vision = datos["vision"] if vision is None else vision
    logo_url = datos["logo_url"] if logo_url is None else logo_url
    eslogan = datos["eslogan"] if eslogan is None else eslogan
    escudo_url = datos["escudo_url"] if escudo_url is None else escudo_url

    return web_actualizar_institucion(
        ID_INSTITUCION,
        nombre,
        nit,
        resolucion,
        direccion,
        telefono,
        id_municipio,
        id_departamento,
        email,
        rector,
        correo_rector,
        mision,
        vision,
        logo_url,
        eslogan,
        escudo_url,
    )

def web_recargar_institucion():
    """
    Recarga desde la base de datos la institución actualmente configurada.
    Actualiza la información almacenada en session_state.
    """

    datos = web_obtener_institucion(ID_INSTITUCION)

    if datos is not None:
        st.session_state["institucion_actual"] = datos

    return datos

def mostrar_modulo_institucion():
    """Módulo de administración de la información institucional."""

    st.title("🏫 Institución")

    # =====================================================
    # CARGAR INSTITUCIÓN
    # =====================================================

    datos = web_recargar_institucion()

    if datos is None:
        st.error(
            f"No fue posible cargar la información de la institución "
            f"'{ID_INSTITUCION}'."
        )
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🏫 Datos Generales",
            "👤 Rector",
            "📍 Ubicación",
            "🎯 Identidad",
            "🖼️ Imagen Institucional",
        ]
    )

    # =====================================================
    # TAB 1 — DATOS GENERALES
    # =====================================================

    with tab1:

        with st.form("frm_datos_generales"):

            nombre = st.text_input(
                "Nombre de la institución",
                value=datos.get("nombre_institucion") or "",
            )

            nit = st.text_input(
                "NIT / DANE",
                value=datos.get("nit_dane") or "",
            )

            resolucion = st.text_input(
                "Resolución de aprobación",
                value=datos.get("resolucion_aprobacion") or "",
            )

            eslogan = st.text_input(
                "Eslogan",
                value=datos.get("eslogan") or "",
            )

            guardar = st.form_submit_button(
                "💾 Guardar datos generales",
                use_container_width=True,
            )

        if guardar:

            ok, mensaje = _guardar_institucion(
                datos,
                nombre=nombre,
                nit=nit,
                resolucion=resolucion,
                eslogan=eslogan,
            )

            if ok:
                datos = web_recargar_institucion()
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)

    # =====================================================
    # TAB 2 — RECTOR
    # =====================================================

    with tab2:

        with st.form("frm_rector"):

            rector = st.text_input(
                "Nombre del rector",
                value=datos.get("nombre_rector") or "",
            )

            correo_rector = st.text_input(
                "Correo del rector",
                value=datos.get("correo_rector") or "",
            )

            guardar = st.form_submit_button(
                "💾 Guardar información del rector",
                use_container_width=True,
            )

        if guardar:

            ok, mensaje = _guardar_institucion(
                datos,
                rector=rector,
                correo_rector=correo_rector,
            )

            if ok:
                datos = web_recargar_institucion()
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)

    # =====================================================
    # TAB 3 — UBICACIÓN
    # =====================================================

    with tab3:

        catalogo_deptos = _cargar_catalogo_departamentos()

        nombres_deptos = catalogo_deptos["nombres"]

        if not nombres_deptos:

            st.error(
                "No fue posible cargar el catálogo de departamentos."
            )

        else:

            # =================================================
            # DETERMINAR DEPARTAMENTO ACTUAL
            # =================================================

            id_departamento_actual = datos.get(
                "id_departamento"
            )

            nombre_departamento_actual = datos.get(
                "departamento"
            )

            if id_departamento_actual is not None:

                try:

                    id_actual = str(
                        id_departamento_actual
                    )

                    if id_actual in catalogo_deptos["por_id"]:

                        nombre_departamento_actual = (
                            catalogo_deptos["por_id"][id_actual]
                        )

                except Exception:
                    pass

            # -------------------------------------------------
            # Validar que el departamento actual exista
            # -------------------------------------------------

            if (
                nombre_departamento_actual
                not in nombres_deptos
            ):

                nombre_departamento_actual = (
                    nombres_deptos[0]
                )

            # =================================================
            # DEPARTAMENTO
            #
            # IMPORTANTE:
            # NO ESTÁ DENTRO DE st.form()
            #
            # Al cambiarlo, Streamlit vuelve a ejecutar
            # inmediatamente y podremos cargar los municipios
            # correspondientes.
            # =================================================

            departamento_nombre = st.selectbox(
                "Departamento",
                options=nombres_deptos,
                index=nombres_deptos.index(
                    nombre_departamento_actual
                ),
                key="institucion_departamento"
            )

            id_departamento = catalogo_deptos[
                "por_nombre"
            ][departamento_nombre]

            # =================================================
            # CARGAR MUNICIPIOS DEL DEPARTAMENTO SELECCIONADO
            # =================================================

            catalogo_municipios = (
                _cargar_catalogo_municipios(
                    id_departamento
                )
            )

            nombres_municipios = (
                catalogo_municipios["nombres"]
            )

            # =================================================
            # DETERMINAR MUNICIPIO ACTUAL
            # =================================================

            id_municipio_actual = datos.get(
                "id_municipio"
            )

            nombre_municipio_actual = datos.get(
                "municipio"
            )

            # -------------------------------------------------
            # Si el municipio actual pertenece al nuevo
            # departamento, conservarlo.
            #
            # Si NO pertenece, seleccionar el primero.
            # -------------------------------------------------

            if id_municipio_actual is not None:

                try:

                    id_municipio_str = str(
                        id_municipio_actual
                    )

                    if (
                        id_municipio_str
                        in catalogo_municipios["por_id"]
                    ):

                        nombre_municipio_actual = (
                            catalogo_municipios["por_id"][
                                id_municipio_str
                            ]
                        )

                    else:

                        nombre_municipio_actual = None

                except Exception:

                    nombre_municipio_actual = None

            if (
                nombre_municipio_actual
                not in nombres_municipios
            ):

                if nombres_municipios:

                    nombre_municipio_actual = (
                        nombres_municipios[0]
                    )

                else:

                    nombre_municipio_actual = None

            # =================================================
            # MUNICIPIO
            # =================================================

            if nombres_municipios:

                municipio_nombre = st.selectbox(
                    "Municipio",
                    options=nombres_municipios,
                    index=nombres_municipios.index(
                        nombre_municipio_actual
                    ),
                    key="institucion_municipio"
                )

                id_municipio = (
                    catalogo_municipios[
                        "por_nombre"
                    ][municipio_nombre]
                )

            else:

                st.warning(
                    "No hay municipios registrados "
                    "para el departamento seleccionado."
                )

                municipio_nombre = ""
                id_municipio = None

            # =================================================
            # RESTO DE LOS DATOS DE UBICACIÓN
            # =================================================

            with st.form("frm_ubicacion_datos"):

                direccion = st.text_input(
                    "Dirección",
                    value=(
                        datos.get(
                            "direccion_principal"
                        ) or ""
                    )
                )

                telefono = st.text_input(
                    "Teléfono",
                    value=(
                        datos.get(
                            "telefono_principal"
                        ) or ""
                    )
                )

                email = st.text_input(
                    "Correo institucional",
                    value=(
                        datos.get(
                            "email_institucional"
                        ) or ""
                    )
                )

                guardar = st.form_submit_button(
                    "💾 Guardar ubicación",
                    use_container_width=True
                )

            # =================================================
            # GUARDAR
            # =================================================

            if guardar:

                if not id_departamento:

                    st.error(
                        "Debe seleccionar un departamento."
                    )

                elif not id_municipio:

                    st.error(
                        "Debe seleccionar un municipio."
                    )

                else:

                    ok, mensaje = _guardar_institucion(
                        datos,
                        direccion=direccion,
                        telefono=telefono,
                        id_municipio=id_municipio,
                        id_departamento=id_departamento,
                        email=email,
                    )

                    if ok:
                        datos = web_recargar_institucion()
                        st.success(mensaje)
                        st.rerun()
                    else:

                        st.error(mensaje)


    # =====================================================
    # TAB 4 — IDENTIDAD
    # =====================================================

    # =====================================================
    # TAB 4 — IDENTIDAD
    # =====================================================

    with tab4:

        with st.form("frm_identidad"):

            mision = st.text_area(
                "Misión",
                value=datos.get("mision") or "",
                height=180,
            )

            vision = st.text_area(
                "Visión",
                value=datos.get("vision") or "",
                height=180,
            )

            guardar = st.form_submit_button(
                "💾 Guardar identidad institucional",
                use_container_width=True,
            )

        if guardar:

            ok, mensaje = _guardar_institucion(
                datos,
                mision=mision,
                vision=vision,
            )

            if ok:
                datos = web_recargar_institucion()
                st.success(mensaje)
                st.rerun()

            else:
                st.error(mensaje)

    # =====================================================
    # TAB 5 — IMAGEN INSTITUCIONAL
    # =====================================================

    with tab5:

        st.subheader("🖼️ Recursos Institucionales")

        os.makedirs(RUTA_INSTITUCION, exist_ok=True)

        ruta_logo = os.path.join(
            RUTA_INSTITUCION,
            NOMBRE_LOGO,
        )

        ruta_escudo = os.path.join(
            RUTA_INSTITUCION,
            NOMBRE_ESCUDO,
        )

        col1, col2 = st.columns(2)

        # ===================================================
        # LOGO
        # ===================================================

        with col1:

            st.markdown("### 🏫 Logo Institucional")

            if os.path.exists(ruta_logo):
                st.image(
                    ruta_logo,
                    width=180,
                )
            else:
                st.info(
                    "No existe un logo cargado."
                )

            nuevo_logo = st.file_uploader(
                "Seleccionar Logo",
                type=["png", "jpg", "jpeg"],
                key="logo",
            )

            if st.button(
                "💾 Actualizar Logo",
                use_container_width=True,
            ):

                if nuevo_logo is not None:

                    with open(
                        ruta_logo,
                        "wb",
                    ) as archivo:

                        archivo.write(
                            nuevo_logo.getbuffer()
                        )

                    st.success(
                        "Logo actualizado correctamente."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Seleccione un archivo."
                    )

        # ===================================================
        # ESCUDO
        # ===================================================

        with col2:

            st.markdown("### 🛡️ Escudo Institucional")

            if os.path.exists(ruta_escudo):
                st.image(
                    ruta_escudo,
                    width=180,
                )
            else:
                st.info(
                    "No existe un escudo cargado."
                )

            nuevo_escudo = st.file_uploader(
                "Seleccionar Escudo",
                type=["png", "jpg", "jpeg"],
                key="escudo",
            )

            if st.button(
                "💾 Actualizar Escudo",
                use_container_width=True,
            ):

                if nuevo_escudo is not None:

                    with open(
                        ruta_escudo,
                        "wb",
                    ) as archivo:

                        archivo.write(
                            nuevo_escudo.getbuffer()
                        )

                    st.success(
                        "Escudo actualizado correctamente."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Seleccione un archivo."
                    )