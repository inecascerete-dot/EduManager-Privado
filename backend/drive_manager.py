from pathlib import Path

from tempfile import NamedTemporaryFile
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from backend.config import (
    GOOGLE_DESKTOP_CLIENT,
    GOOGLE_TOKEN,
    GOOGLE_DRIVE_ROOT,
)

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]


class DriveManager:

    def __init__(self):

        self.service = None
        self.root_folder = GOOGLE_DRIVE_ROOT

        self.autenticar()


    def autenticar(self):

        creds = None
        print("TOKEN =", GOOGLE_TOKEN)
        print("EXISTE =", Path(GOOGLE_TOKEN).exists())

        if Path(GOOGLE_TOKEN).exists():

            creds = Credentials.from_authorized_user_file(
                str(GOOGLE_TOKEN),
                SCOPES
            )

        if not creds or not creds.valid:

            if creds and creds.expired and creds.refresh_token:
                print("INTENTANDO REFRESCAR TOKEN")

                creds.refresh(Request())

            else:
                print("ENTRANDO A NUEVA AUTENTICACIÓN")

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(GOOGLE_DESKTOP_CLIENT),
                    SCOPES
                )

                creds = flow.run_local_server(port=0)

            with open(GOOGLE_TOKEN, "w") as token:
                token.write(creds.to_json())

        self.service = build(
            "drive",
            "v3",
            credentials=creds
        )


    def subir_archivo(self, archivo_local, nombre_archivo, carpeta_id=None):

        carpeta = carpeta_id or self.root_folder

        metadata = {
            "name": nombre_archivo,
            "parents": [carpeta]
        }

        media = MediaFileUpload(
            archivo_local,
            resumable=True
        )

        archivo = self.service.files().create(
            body=metadata,
            media_body=media,
            fields="id,name,webViewLink"
        ).execute()

        return archivo

    def buscar_carpeta(self, nombre_carpeta, carpeta_padre=None):

        padre = carpeta_padre or self.root_folder

        consulta = (
            f"name='{nombre_carpeta}' "
            f"and mimeType='application/vnd.google-apps.folder' "
            f"and '{padre}' in parents "
            f"and trashed=false"
        )

        resultados = self.service.files().list(
            q=consulta,
            fields="files(id,name)"
        ).execute()

        carpetas = resultados.get("files", [])

        if carpetas:
            return carpetas[0]["id"]

        return None


    def crear_carpeta(self, nombre_carpeta, carpeta_padre=None):

        padre = carpeta_padre or self.root_folder

        existente = self.buscar_carpeta(
            nombre_carpeta,
            padre
        )

        if existente:
            return existente

        metadata = {
            "name": nombre_carpeta,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [padre]
        }

        carpeta = self.service.files().create(
            body=metadata,
            fields="id,name"
        ).execute()

        return carpeta["id"]

    def obtener_carpeta_estudiante(self, id_estudiante):

        carpeta_estudiantes = self.crear_carpeta(
            "ESTUDIANTES"
        )

        carpeta_estudiante = self.crear_carpeta(
            id_estudiante,
            carpeta_estudiantes
        )

        return carpeta_estudiante

    def obtener_carpeta_acudiente(self, id_acudiente):
        carpeta_acudientes = self.crear_carpeta(
            "ACUDIENTES"
        )

        carpeta_acudiente = self.crear_carpeta(
            id_acudiente,
            carpeta_acudientes
        )

        return carpeta_acudiente

    def subir_foto_estudiante(self, archivo_streamlit, id_estudiante):

        carpeta = self.obtener_carpeta_estudiante(id_estudiante)

        extension = Path(archivo_streamlit.name).suffix

        with NamedTemporaryFile(delete=False, suffix=extension) as temp:

            temp.write(archivo_streamlit.getbuffer())

            ruta_temporal = temp.name

        try:

            archivo = self.subir_archivo(
                ruta_temporal,
                f"FOTO_ESTUDIANTE{id_estudiante}{extension}",
                carpeta
            )

            self.service.permissions().create(
                fileId=archivo["id"],
                body={
                    "type": "anyone",
                    "role": "reader"
                }
            ).execute()

            archivo = self.service.files().get(
                fileId=archivo["id"],
                fields="id,webViewLink,webContentLink"
            ).execute()

            return f"https://drive.google.com/uc?id={archivo['id']}&export=view"

        finally:

            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)