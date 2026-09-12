import os
import pandas as pd

from backend.db_manager import obtener_conexion_directa


# Ruta del archivo limpio
BASE_DIR = os.path.dirname(__file__)
EXCEL_DIVIPOLA = os.path.join(
    BASE_DIR,
    "datos",
    "DIVIPOLA_LIMPIO.xlsx"
)


def importar_departamentos():

    con = obtener_conexion_directa()

    if not con:
        print("No fue posible conectar a la base de datos.")
        return

    try:

        df = pd.read_excel(
            EXCEL_DIVIPOLA,
            sheet_name="Departamentos"
        )

        with con.cursor() as cur:

            for _, fila in df.iterrows():

                codigo = str(fila["codigo_dane"]).zfill(2)
                nombre = str(fila["nombre"]).strip().upper()

                cur.execute(
                    """
                    INSERT INTO departamentos
                    (
                        codigo_dane,
                        nombre
                    )
                    VALUES (%s,%s)
                    ON CONFLICT (codigo_dane)
                    DO NOTHING;
                    """,
                    (
                        codigo,
                        nombre
                    )
                )

        con.commit()

        print("✅ Departamentos importados correctamente.")

    except Exception as e:

        con.rollback()
        print(f"❌ Error importando departamentos: {e}")

    finally:

        con.close()


def importar_municipios():

    con = obtener_conexion_directa()

    if not con:
        print("No fue posible conectar.")
        return

    try:

        df = pd.read_excel(
            EXCEL_DIVIPOLA,
            sheet_name="Municipios"
        )

        with con.cursor() as cur:

            for _, fila in df.iterrows():

                codigo_departamento = str(fila["codigo_departamento"]).zfill(2)
                codigo_municipio = str(fila["codigo_dane"]).zfill(5)
                nombre = str(fila["nombre"]).strip().upper()

                # Buscar el id interno del departamento
                cur.execute(
                    """
                    SELECT id_departamento
                    FROM departamentos
                    WHERE codigo_dane = %s;
                    """,
                    (codigo_departamento,)
                )

                resultado = cur.fetchone()

                if not resultado:
                    print(f"⚠ Departamento no encontrado: {codigo_departamento}")
                    continue

                id_departamento = resultado[0]

                cur.execute(
                    """
                    INSERT INTO municipios
                    (
                        codigo_dane,
                        nombre,
                        id_departamento
                    )
                    VALUES (%s,%s,%s)
                    ON CONFLICT (codigo_dane)
                    DO NOTHING;
                    """,
                    (
                        codigo_municipio,
                        nombre,
                        id_departamento
                    )
                )

        con.commit()

        print("✅ Municipios importados correctamente.")

    except Exception as e:

        con.rollback()
        print(f"❌ Error importando municipios: {e}")

    finally:

        con.close()


if __name__ == "__main__":

    importar_departamentos()

    importar_municipios()

    print("🎉 Proceso terminado.")