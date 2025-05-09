import streamlit as st
import gspread
import json
import pandas as pd
from datetime import datetime

# Nombre de tu hoja de cálculo
SHEET_NAME = "Registro Publicaciones Antisemitas"

# Columnas esperadas en la hoja de cálculo
EXPECTED_COLUMNS = [
    "Fecha de Registro en App", # Fecha en que se añade a la app
    "Fecha de Publicación Original", # Fecha del post original
    "Red Social", 
    "Usuario", 
    "Texto Extraído", 
    "Hashtags", 
    "Enlace", 
    "Clasificación IA"
]

def authenticate_google_sheets():
    """Autentica con Google Sheets usando los secrets de Streamlit."""
    try:
        creds_json_str = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
        creds_dict = json.loads(creds_json_str)
        gc = gspread.service_account_from_dict(creds_dict)
        return gc
    except KeyError:
        st.error("Error: Secret 'GOOGLE_SHEETS_CREDENTIALS' no encontrado.")
        st.info("Por favor, configura este secret en Streamlit Cloud con el contenido de tu archivo JSON de credenciales de Google.")
        return None
    except Exception as e:
        st.error(f"Error al autenticar con Google Sheets: {e}")
        return None

def get_worksheet(gc, sheet_name):
    """Obtiene la hoja de trabajo. Si no existe, la crea con encabezados."""
    if not gc:
        return None
    try:
        spreadsheet = gc.open(sheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        try:
            spreadsheet = gc.create(sheet_name)
            # Comparte la hoja con el email de tu cuenta de servicio para que pueda editarla
            # Esto es importante si la cuenta de servicio no es la propietaria.
            # El email se encuentra en tu archivo JSON como "client_email"
            creds_json_str = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
            creds_dict = json.loads(creds_json_str)
            client_email = creds_dict.get("client_email")
            if client_email:
                 spreadsheet.share(client_email, perm_type='user', role='writer')
            st.success(f"Hoja de cálculo '{sheet_name}' creada. Por favor, verifica los permisos si es necesario.")
        except Exception as e_create:
            st.error(f"No se pudo abrir ni crear la hoja de cálculo '{sheet_name}': {e_create}")
            return None
            
    try:
        worksheet = spreadsheet.sheet1
        # Verificar encabezados
        if not worksheet.row_values(1): # Si la primera fila está vacía
            worksheet.update('A1', [EXPECTED_COLUMNS])
            st.info(f"Encabezados añadidos a la hoja '{sheet_name}'.")
        elif worksheet.row_values(1) != EXPECTED_COLUMNS:
             # Podrías añadir lógica para actualizar/corregir encabezados si son diferentes
             # Por ahora, solo lo notificamos si son distintos a lo esperado y no están vacíos
             pass # st.warning("Los encabezados existentes son diferentes a los esperados.")
        return worksheet
    except Exception as e_ws:
        st.error(f"Error al acceder a la hoja de trabajo: {e_ws}")
        return None


def append_to_sheet(data_row_dict):
    """
    Añade una fila de datos a la hoja de cálculo especificada.
    data_row_dict es un diccionario con los datos.
    """
    gc = authenticate_google_sheets()
    if not gc:
        return False

    worksheet = get_worksheet(gc, SHEET_NAME)
    if not worksheet:
        return False

    try:
        # Asegurar el orden de las columnas según EXPECTED_COLUMNS
        ordered_row = [data_row_dict.get(col, "") for col in EXPECTED_COLUMNS]
        worksheet.append_row(ordered_row)
        return True
    except Exception as e:
        st.error(f"Error al añadir datos a Google Sheets: {e}")
        return False
