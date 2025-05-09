import streamlit as st
import pandas as pd
import datetime
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from playwright.sync_api import sync_playwright
from transformers import pipeline

# Cargar clasificador de emociones con backend TensorFlow (compatible con Streamlit Cloud)
classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=1, framework="tf")

# Leer credenciales desde variable secreta
info = json.loads(os.environ["GOOGLE_CREDS"])
creds = service_account.Credentials.from_service_account_info(info, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

# IDs de Google Sheets y Google Drive
SPREADSHEET_ID = "1Tu0yijVrbl3I2hkGgHXUgR9kwbSbxMRmaM2oaVxRCJ8"
DRIVE_FOLDER_ID = "1fzHj5SMZ2ipk-mcGhp_RhllQdQBocg65"

# Clientes de Google API
sheet_service = build("sheets", "v4", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)

# Clasificación del texto por emoción
def classify_text(text):
    result = classifier(text)[0]
    label = result['label'].lower()
    if 'disgust' in label or 'anger' in label:
        return "Negacionismo"
    elif 'fear' in label or 'surprise' in label:
        return "Conspiración"
    else:
        return "Burla"

# Captura automática de pantalla
def take_screenshot(url, filename="captura.png"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.screenshot(path=filename, full_page=True)
        browser.close()

# Subir imagen a Google Drive
def upload_to_drive(file_path):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [DRIVE_FOLDER_ID]
    }
    media = {
        'mimeType': 'image/png',
        'body': open(file_path, 'rb')
    }
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    file_id = uploaded.get("id")
    return f"https://drive.google.com/uc?id={file_id}"

# Agregar fila a hoja de cálculo
def add_row_to_sheet(data):
    sheet_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="A1",
        valueInputOption="USER_ENTERED",
        body={"values": [data]}
    ).execute()

# ===== INTERFAZ STREAMLIT =====
st.title("🕵️ Antisemitismo Tracker")
url = st.text_input("📎 Pega un enlace de X, Instagram o Facebook:")

if st.button("Analizar"):
    if url:
        st.info("Procesando el enlace...")

        filename = "captura.png"
        take_screenshot(url, filename)
        img_url = upload_to_drive(filename)

        # Simulación básica de datos
        user = "@usuario"
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        texto = "Texto extraído automáticamente del post"
        hashtags = "#hashtag1 #hashtag2"
        clasificacion = classify_text(texto)

        # Guardar fila
        fila = [fecha, "X/IG/FB", user, texto, hashtags, url, clasificacion, "", img_url]
        add_row_to_sheet(fila)

        st.success("¡Listo! Clasificación y captura completadas.")
        st.image(filename)
        st.markdown(f"📄 **Clasificación:** `{clasificacion}`")
        st.markdown(f"[📂 Ver captura en Drive]({img_url})")
    else:
        st.warning("Por favor, ingresá un enlace válido.")
