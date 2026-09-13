"""Utilidades pequeñas para mejorar la navegación de formularios Streamlit."""

import json

import streamlit.components.v1 as components


def activar_navegacion_enter(etiquetas, boton_final=None):
    """Avanza por etiquetas visibles y opcionalmente activa un botón final."""
    orden = json.dumps(list(etiquetas), ensure_ascii=False)
    boton = json.dumps(boton_final, ensure_ascii=False)

    components.html(
        f"""
        <script>
        (() => {{
            const ordenFormulario = {orden};
            const textoBotonFinal = {boton};
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

            const camposVisibles = () => Array.from(
                obtenerRaiz().querySelectorAll(selectorCampos)
            ).filter((campo) => {{
                const rect = campo.getBoundingClientRect();
                return !campo.disabled && rect.width > 0 && rect.height > 0;
            }});

            const buscarCampo = (etiqueta) => {{
                const etiquetaNormalizada = normalizar(etiqueta);
                const candidatos = camposVisibles();
                const exacto = candidatos.find((campo) =>
                    normalizar(campo.getAttribute("aria-label")) === etiquetaNormalizada
                );
                if (exacto) return exacto;

                if (etiquetaNormalizada === "fecha de nacimiento") {{
                    const fecha = candidatos.find((campo) =>
                        campo.getAttribute("data-testid") === "stDateInputField"
                    );
                    if (fecha) return fecha;
                }}

                return candidatos.find((campo) =>
                    normalizar(campo.getAttribute("aria-label"))
                        .startsWith(`${{etiquetaNormalizada}} `)
                );
            }};

            const buscarSiguiente = (posicion) => {{
                for (let indice = posicion + 1; indice < ordenFormulario.length; indice += 1) {{
                    const siguiente = buscarCampo(ordenFormulario[indice]);
                    if (siguiente) return siguiente;
                }}
                return null;
            }};

            const instalar = () => {{
                ordenFormulario.forEach((etiqueta, posicion) => {{
                    const campo = buscarCampo(etiqueta);
                    if (!campo || campo.dataset.enterFormularioInstalado === "1") return;

                    campo.dataset.enterFormularioInstalado = "1";
                    campo.addEventListener("keydown", (evento) => {{
                        if (evento.key !== "Enter") return;

                        const siguiente = buscarSiguiente(posicion);
                        if (siguiente) {{
                            evento.preventDefault();
                            evento.stopPropagation();
                            siguiente.focus();
                            siguiente.scrollIntoView({{block: "center", behavior: "smooth"}});
                            return;
                        }}

                        if (textoBotonFinal) {{
                            const boton = Array.from(obtenerRaiz().querySelectorAll("button"))
                                .find((elemento) => elemento.innerText.trim() === textoBotonFinal);
                            if (boton) {{
                                evento.preventDefault();
                                evento.stopPropagation();
                                // Esperar a que Streamlit registre el último
                                // carácter escrito en el campo de contraseña.
                                window.setTimeout(() => {{
                                    const botonActual = Array.from(
                                        obtenerRaiz().querySelectorAll("button")
                                    ).find((elemento) =>
                                        elemento.innerText.trim() === textoBotonFinal
                                    );
                                    if (botonActual) botonActual.click();
                                }}, 200);
                            }}
                        }}
                    }}, true);
                }});
            }};

            instalar();
            const observador = new MutationObserver(instalar);
            observador.observe(window.parent.document.body, {{childList: true, subtree: true}});
            window.setTimeout(() => observador.disconnect(), 30000);
        }})();
        </script>
        """,
        height=0,
    )
