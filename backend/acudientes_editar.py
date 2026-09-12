import streamlit as st

from backend.acudientes_db import (
    web_consultar_acudiente_por_documento,
)

from backend.acudientes import (
    mostrar_acudientes
)

def mostrar_edicion_acudiente():

    st.title("✏️ Editar Acudiente")

    numero = st.text_input(
        "Número de documento del acudiente",
        key="editar_doc_acu"
    )

    if st.button(
        "🔍 Buscar",
        use_container_width=True
    ):

        acudiente = web_consultar_acudiente_por_documento(numero)

        if acudiente:

            st.session_state["acu_edicion"] = acudiente

        else:

            st.error("No existe un acudiente con ese documento.")

    if "acu_edicion" in st.session_state:

        mostrar_acudientes(
            modo="editar"
        )