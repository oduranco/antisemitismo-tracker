
import streamlit as st
import pandas as pd
import datetime
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Cargar credenciales desde secrets
info = json.loads(os.environ["GOOGLE_CREDS"])
creds = service_account.Credentials.from_service_account_info(info, scopes=[
    "https://www.googleapis.com/auth/spreadsheets"
])

SPREADSHEET_ID = "1Tu0yijVrbl3I2hkGgHXUgR9kwbSbxMRmaM2oaVxRCJ8"
sheet_service = build("sheets", "v4", credentials=creds)

def add_row_to_sheet(data):
    sheet_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="A1",
        valueInputOption="USER_ENTERED",
        body={"values": [data]}
    ).execute()

st.title("📋 Organizador de enlaces antisemitas")

st.markdown("Pegá un enlace y completá los campos para organizar la información en la tabla.")

url = st.text_input("🔗 Enlace (X, Instagram o Facebook)")
texto = st.text_area("📝 Texto del post (si lo tiene)")
clasificacion = st.selectbox("🧠 Clasificación", ["", "Burla", "Negacionismo", "Conspiración", "Otro"])
hashtags = st.text_input("🏷️ Hashtags (opcional)")
autor = st.text_input("👤 Usuario (opcional)")

if st.button("Guardar"):
    if url:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        fila = [now, "X/IG/FB", autor or "@usuario", texto, hashtags, url, clasificacion, "", ""]
        add_row_to_sheet(fila)
        st.success("✅ Enlace guardado correctamente.")
    else:
        st.warning("⚠️ El enlace es obligatorio.")
