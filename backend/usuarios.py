import streamlit as st
import bcrypt

from backend.db_manager import (
    obtener_usuarios,
    crear_usuario,
    actualizar_usuario,
    cambiar_password_usuario,
    cambiar_estado_usuario,
    restablecer_password_usuario
)


ROLES = [
    "ADMIN",
    "DIRECTIVO",
    "DOCENTE",
    "ESTUDIANTE",
    "ACUDIENTE"
]

ESTADOS = [
    "ACTIVO",
    "INACTIVO"
]


def mostrar_modulo_usuarios():

    st.title("👤 Administración de Usuarios")

    # =====================================================
    # NUEVO USUARIO
    # =====================================================

    with st.form("frm_usuario"):

        st.subheader("➕ Nuevo usuario")

        col1, col2 = st.columns(2)

        with col1:

            usuario = st.text_input("Usuario")

            password = st.text_input(
                "Contraseña",
                type="password"
            )

            confirmar = st.text_input(
                "Confirmar contraseña",
                type="password"
            )

        with col2:

            rol = st.selectbox("Rol", ROLES)

            estado = st.selectbox("Estado", ESTADOS)

        guardar = st.form_submit_button(
            "💾 Guardar usuario",
            use_container_width=True
        )

        if guardar:

            if usuario.strip() == "":

                st.error("Debe ingresar un usuario.")

            elif password == "":

                st.error("Debe ingresar una contraseña.")

            elif password != confirmar:

                st.error("Las contraseñas no coinciden.")

            else:

                password_hash = bcrypt.hashpw(
                    password.encode(),
                    bcrypt.gensalt()
                ).decode()

                ok, mensaje = crear_usuario(
                    usuario,
                    password_hash,
                    rol,
                    estado
                )

                if ok:

                    st.success(mensaje)
                    st.rerun()

                else:

                    st.error(mensaje)

    st.divider()

    # =====================================================
    # TABLA
    # =====================================================

    usuarios = obtener_usuarios()

    if not usuarios:

        st.info("No existen usuarios registrados.")
        return

    tabla = []

    for u in usuarios:

        ultimo = "Nunca"

        if u[4]:

            ultimo = u[4].strftime("%d/%m/%Y %I:%M %p")

        tabla.append({
            "Usuario": u[1],
            "Rol": u[2],
            "Estado": u[3],
            "Último acceso": ultimo
        })

    st.subheader("Usuarios registrados")

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    usuario_seleccionado = st.selectbox(
        "Seleccione un usuario",
        usuarios,
        format_func=lambda x: x[1]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if st.button(
            "✏️ Editar usuario",
            use_container_width=True
        ):

            st.session_state["editar_usuario"] = usuario_seleccionado[0]


    with col2:

        if st.button(
            "🔑 Cambiar contraseña",
            use_container_width=True
        ):

            st.session_state["password_usuario"] = usuario_seleccionado[0]


    with col3:

        texto_boton = (
            "🚫 Inactivar"
            if usuario_seleccionado[3] == "ACTIVO"
            else "✅ Activar"
        )

        if st.button(
            texto_boton,
            use_container_width=True
        ):

            ok, mensaje = cambiar_estado_usuario(
                usuario_seleccionado[0]
            )

            if ok:

                st.success(mensaje)
                st.rerun()

            else:

                st.error(mensaje)
   
    with col4:

        if st.button(
            "🔄 Restablecer",
            use_container_width=True
        ):

            if usuario_seleccionado[3] == "INACTIVO":

                st.warning(
                    "⚠️ El usuario está inactivo.\n\n"
                    "Primero actívelo para poder restablecer la contraseña."
                )

            else:

                password_hash = bcrypt.hashpw(
                    "123456".encode(),
                    bcrypt.gensalt()
                ).decode()

                ok, mensaje = restablecer_password_usuario(
                    usuario_seleccionado[0],
                    password_hash
                )

                if ok:

                    st.success(
                        "✅ Contraseña restablecida.\n\n"
                        "Contraseña temporal: 123456"
                    )

                else:

                    st.error(mensaje)

    # =====================================================
    # EDITAR USUARIO
    # =====================================================

    if "editar_usuario" in st.session_state:

        usuario_actual = next(
            u for u in usuarios
            if u[0] == st.session_state["editar_usuario"]
        )

        st.divider()

        st.subheader("✏️ Editar usuario")

        with st.form("frm_editar"):

            nuevo_usuario = st.text_input(
                "Usuario",
                value=usuario_actual[1]
            )

            nuevo_rol = st.selectbox(
                "Rol",
                ROLES,
                index=ROLES.index(usuario_actual[2])
            )

            nuevo_estado = st.selectbox(
                "Estado",
                ESTADOS,
                index=ESTADOS.index(usuario_actual[3])
            )

            guardar = st.form_submit_button(
                "💾 Guardar cambios"
            )

            if guardar:

                ok, mensaje = actualizar_usuario(
                    usuario_actual[0],
                    nuevo_usuario,
                    nuevo_rol,
                    nuevo_estado
                )

                if ok:

                    del st.session_state["editar_usuario"]

                    st.success(mensaje)

                    st.rerun()

                else:

                    st.error(mensaje)

    # =====================================================
    # CAMBIAR CONTRASEÑA
    # =====================================================

    if "password_usuario" in st.session_state:

        usuario_actual = next(
            u for u in usuarios
            if u[0] == st.session_state["password_usuario"]
        )

        st.divider()

        st.subheader(f"🔑 Cambiar contraseña - {usuario_actual[1]}")

        with st.form("frm_password"):

            nueva = st.text_input(
                "Nueva contraseña",
                type="password"
            )

            confirmar = st.text_input(
                "Confirmar contraseña",
                type="password"
            )

            guardar = st.form_submit_button(
                "Actualizar contraseña"
            )

            if guardar:

                if nueva == "":

                    st.error("Debe ingresar una contraseña.")

                elif nueva != confirmar:

                    st.error("Las contraseñas no coinciden.")

                else:

                    password_hash = bcrypt.hashpw(
                        nueva.encode(),
                        bcrypt.gensalt()
                    ).decode()

                    ok, mensaje = cambiar_password_usuario(
                        usuario_actual[0],
                        password_hash
                    )

                    if ok:

                        del st.session_state["password_usuario"]

                        st.success(mensaje)

                        st.rerun()

                    else:

                        st.error(mensaje)