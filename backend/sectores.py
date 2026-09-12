import streamlit as st

from backend.sectores_db import (
    web_registrar_sector,
    web_buscar_sectores
)

from backend.catalogos_db import (
    obtener_departamentos,
    obtener_municipios
)


TIPO = [
    "Barrio",
    "Vereda",
    "Corregimiento",
    "Caserío",
    "Centro poblado",
    "Urbanización",
    "Condominio",
    "Sector",
    "Otro"
]


def mostrar_registro_sector():

    st.title("🏘️ Administración de Sectores")

    st.info(
        "Los sectores serán utilizados posteriormente por estudiantes y acudientes."
    )

    # ============================================================
    # MOSTRAR MENSAJE PENDIENTE
    # ============================================================

    mensaje_exito = st.session_state.pop(
        "mensaje_exito_sector",
        None
    )

    if mensaje_exito:
        st.success(mensaje_exito)

    # ============================================================
    # PREPARAR LIMPIEZA DEL FORMULARIO
    #
    # Esta bandera se activa después de guardar.
    # En la siguiente ejecución limpiamos solamente:
    # - nombre del sector
    # - tipo
    #
    # Departamento y municipio NO se modifican.
    # ============================================================

    if st.session_state.pop(
        "limpiar_formulario_sector",
        False
    ):

        st.session_state["sector_nombre"] = ""
        st.session_state["sector_tipo"] = TIPO[0]

    # ============================================================
    # CARGAR DEPARTAMENTOS
    # ============================================================

    departamentos = obtener_departamentos()

    if not departamentos:

        st.error(
            "❌ No fue posible cargar el catálogo de departamentos."
        )
        return

    # ============================================================
    # DEPARTAMENTO
    # ============================================================

    opciones_departamentos = {
        d[2]: d
        for d in departamentos
    }

    nombres_departamentos = list(
        opciones_departamentos.keys()
    )

    # Intentar conservar el departamento actualmente seleccionado
    departamento_actual = st.session_state.get(
        "sector_departamento"
    )

    if (
        departamento_actual not in nombres_departamentos
        and nombres_departamentos
    ):
        departamento_actual = nombres_departamentos[0]
        st.session_state["sector_departamento"] = (
            departamento_actual
        )

    departamento_seleccionado = st.selectbox(
        "Departamento*",
        options=nombres_departamentos,
        key="sector_departamento"
    )

    datos_departamento = opciones_departamentos[
        departamento_seleccionado
    ]

    id_departamento = datos_departamento[0]

    # ============================================================
    # CARGAR MUNICIPIOS DEL DEPARTAMENTO
    # ============================================================

    municipios = obtener_municipios(
        id_departamento
    )

    if not municipios:

        st.warning(
            "⚠️ No existen municipios registrados "
            "para el departamento seleccionado."
        )
        return

    # ============================================================
    # MUNICIPIOS
    # ============================================================

    opciones_municipios = {
        m[2]: m
        for m in municipios
    }

    nombres_municipios = list(
        opciones_municipios.keys()
    )

    # ============================================================
    # CONSERVAR MUNICIPIO CUANDO SEA POSIBLE
    #
    # Si el usuario cambia de departamento y el municipio
    # anterior ya no pertenece al nuevo departamento,
    # seleccionamos automáticamente el primero.
    # ============================================================

    municipio_actual = st.session_state.get(
        "sector_municipio"
    )

    if (
        municipio_actual not in nombres_municipios
        and nombres_municipios
    ):
        municipio_actual = nombres_municipios[0]
        st.session_state["sector_municipio"] = (
            municipio_actual
        )

    municipio_seleccionado = st.selectbox(
        "Municipio*",
        options=nombres_municipios,
        key="sector_municipio"
    )

    datos_municipio = opciones_municipios[
        municipio_seleccionado
    ]

    id_municipio = datos_municipio[0]

    # ============================================================
    # INFORMACIÓN DE REFERENCIA
    # ============================================================

    st.caption(
        f"Departamento: {departamento_seleccionado} "
        f"(ID {id_departamento})  •  "
        f"Municipio: {municipio_seleccionado} "
        f"(ID {id_municipio})"
    )

    st.divider()

    # ============================================================
    # FORMULARIO DEL SECTOR
    # ============================================================

    st.subheader("➕ Registrar nuevo sector")

    with st.form("form_sector"):

        nombre_sector = st.text_input(
            "Nombre del sector*",
            key="sector_nombre",
            placeholder="Ejemplo: LAS PALMAS"
        )

        tipo = st.selectbox(
            "Tipo*",
            options=TIPO,
            key="sector_tipo"
        )

        observacion = st.text_area(
            "Observaciones",
            key="sector_observacion",
            placeholder="Información adicional del sector..."
        )

        guardar = st.form_submit_button(
            "💾 Guardar Sector",
            use_container_width=True,
            type="primary"
        )

    # ============================================================
    # PROCESAR GUARDADO
    # ============================================================

    if guardar:

        nombre_limpio = nombre_sector.strip()
        observacion_limpia = observacion.strip()

        # --------------------------------------------------------
        # VALIDAR NOMBRE
        # --------------------------------------------------------

        if not nombre_limpio:

            st.error(
                "❌ Debe escribir el nombre del sector."
            )

        else:

            # ----------------------------------------------------
            # REGISTRAR EN BASE DE DATOS
            # ----------------------------------------------------

            ok, mensaje = web_registrar_sector(
                id_municipio,
                nombre_limpio,
                tipo,
                observacion_limpia
            )

            if ok:

                # ------------------------------------------------
                # GUARDAR MENSAJE PARA LA SIGUIENTE EJECUCIÓN
                # ------------------------------------------------

                st.session_state[
                    "mensaje_exito_sector"
                ] = (
                    f"✅ Sector '{nombre_limpio}' "
                    f"registrado correctamente."
                )

                # ------------------------------------------------
                # PEDIR LIMPIEZA DEL FORMULARIO
                # ------------------------------------------------

                st.session_state[
                    "limpiar_formulario_sector"
                ] = True

                # ------------------------------------------------
                # RECARGAR
                #
                # Departamento y municipio permanecen porque
                # NO modificamos sus claves.
                # ------------------------------------------------

                st.rerun()

            else:

                st.error(
                    f"❌ {mensaje}"
                )

    # ============================================================
    # SECTORES REGISTRADOS
    # ============================================================

    st.divider()

    st.subheader("📋 Sectores registrados")

    st.write(
        f"**Municipio seleccionado:** "
        f"{municipio_seleccionado}"
    )

    sectores = web_buscar_sectores(
        id_municipio
    )

    if sectores:

        for s in sectores:

            id_sector = s[0]
            nombre = s[1]
            tipo_sector = s[2]

            st.write(
                f"**{nombre}**  •  "
                f"{tipo_sector}  •  "
                f"ID: `{id_sector}`"
            )

    else:

        st.info(
            "ℹ️ No hay sectores registrados "
            "para este municipio."
        )