import streamlit as st

from backend.db_manager import (
    web_registrar_sede,
    web_obtener_sedes_completo,
    web_actualizar_sede,
    web_eliminar_sede,
)


def mostrar_modulo_sedes():

    st.title("🏫 Sedes")

    tab1, tab2,  = st.tabs([
        "📋 Sedes Registradas",
        "➕ Nueva Sede"
       
    ])

    # =====================================================
    # TAB 1 - LISTADO
    # =====================================================

    with tab1:

        st.markdown("### 📋 Sedes registradas")

        if "sedes_cache" not in st.session_state:
            st.session_state.sedes_cache = web_obtener_sedes_completo()

        sedes = st.session_state.sedes_cache

        if not sedes:
            st.info("No hay sedes registradas.")
        else:

            for sede in sedes:

                sid = sede["id_sede"]
                edit_key = f"sede_edit_{sid}"

                with st.container():

                    c1, c2, c3, c4, c5 = st.columns([3,3,2,1,1])

                    c1.markdown(
                        f"**{sede['nombre_sede']}**  \n`{sid}`"
                    )

                    c2.markdown(
                        sede["direccion"] or "_Sin dirección_"
                    )

                    c3.markdown(
                        f"📞 {sede['telefono_sede']}"
                        if sede["telefono_sede"] else ""
                    )

                    with c4:

                        if st.button(
                            "✏️",
                            key=f"btn_edit_{sid}",
                            help="Editar sede"
                        ):
                            st.session_state[edit_key] = \
                                not st.session_state.get(edit_key, False)
                            st.rerun()

                    with c5:

                        if st.button(
                            "🗑️",
                            key=f"btn_del_{sid}",
                            help="Eliminar sede"
                        ):

                            ok, msg = web_eliminar_sede(sid)

                            if ok:

                                st.success(msg)

                                if "sedes_cache" in st.session_state:
                                    del st.session_state["sedes_cache"]

                                st.rerun()

                            else:
                                st.error(msg)

                    if st.session_state.get(edit_key, False):

                        with st.form(f"frm_edit_{sid}"):

                            st.markdown(
                                f"#### ✏️ Editando {sede['nombre_sede']}"
                            )

                            ec1, ec2 = st.columns(2)

                            with ec1:

                                e_nombre = st.text_input(
                                    "Nombre",
                                    value=sede["nombre_sede"]
                                )

                            with ec2:

                                e_tel = st.text_input(
                                    "Teléfono",
                                    value=sede["telefono_sede"] or ""
                                )

                            e_dir = st.text_input(
                                "Dirección",
                                value=sede["direccion"] or ""
                            )

                            colg, colc = st.columns(2)

                            with colg:

                                guardar = st.form_submit_button(
                                    "💾 Guardar",
                                    use_container_width=True
                                )

                            with colc:

                                cancelar = st.form_submit_button(
                                    "Cancelar",
                                    use_container_width=True
                                )

                        if guardar:

                            ok, msg = web_actualizar_sede(
                                sid,
                                e_nombre,
                                e_dir,
                                e_tel
                            )

                            if ok:

                                st.success(msg)

                                st.session_state[edit_key] = False

                                if "sedes_cache" in st.session_state:
                                    del st.session_state["sedes_cache"]

                                st.rerun()

                            else:

                                st.error(msg)

                        if cancelar:

                            st.session_state[edit_key] = False
                            st.rerun()

                st.divider()

            st.caption(f"Total: {len(sedes)} sede(s)")

        if st.button("🔄 Actualizar lista"):

            if "sedes_cache" in st.session_state:
                del st.session_state["sedes_cache"]

            st.rerun()

    # =====================================================
    # TAB 2 - NUEVA SEDE
    # =====================================================

    with tab2:

        st.markdown("### ➕ Agregar sede")

        with st.form("frm_nueva_sede", clear_on_submit=True):

            c1, c2 = st.columns(2)

            with c1:

                nombre = st.text_input(
                    "Nombre de la sede*"
                )

            with c2:

                telefono = st.text_input(
                    "Teléfono"
                )

            direccion = st.text_input(
                "Dirección"
            )

            guardar = st.form_submit_button(
                "💾 Guardar sede",
                use_container_width=True
            )

        if guardar:

            if not nombre.strip():

                st.error(
                    "Debe escribir el nombre de la sede."
                )

            else:

                ok, msg, _ = web_registrar_sede(
                    nombre,
                    direccion,
                    telefono
                )

                if ok:

                    st.success(msg)

                    if "sedes_cache" in st.session_state:
                        del st.session_state["sedes_cache"]

                    st.rerun()

                else:

                    st.error(msg)

    