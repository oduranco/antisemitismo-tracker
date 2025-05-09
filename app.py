
import streamlit as st
import pandas as pd
import datetime
import os
import json
from textblob import TextBlob
from google.oauth2 import service_account
from googleapiclient.discovery import build
from playwright.sync_api import sync_playwright

def classify_text(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.3:
        return "Burla"
    elif polarity < -0.3:
        return "Negacionismo"
    else:
        return "Conspiración"

info = json.loads(os.environ["GOOGLE_CREDS"])
creds = service_account.Credentials.from_service_account_info(info, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

SPREADSHEET_ID = "1Tu0yijVrbl3I2hkGgHXUgR9kwbSbxMRmaM2oaVxRCJ8"
DRIVE_FOLDER_ID = "1fzHj5SMZ2ipk-mcGhp_RhllQdQBocg65"

sheet_service = build("sheets", "v4", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)

def take_screenshot(url, filename="captura.png"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.screenshot(path=filename, full_page=True)
        browser.close()

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

def add_row_to_sheet(data):
    sheet_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="A1",
        valueInputOption="USER_ENTERED",
        body={"values": [data]}
    ).execute()

st.title("🕵️ Antisemitismo Tracker (versión ligera)")
url = st.text_input("📎 Pega un enlace de X, Instagram o Facebook:")

if st.button("Analizar"):
    if url:
        st.info("Procesando el enlace...")

        filename = "captura.png"
        take_screenshot(url, filename)
        img_url = upload_to_drive(filename)

        user = "@usuario"
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        texto = "Texto extraído automáticamente del post"
        hashtags = "#hashtag1 #hashtag2"
        clasificacion = classify_text(texto)

        fila = [fecha, "X/IG/FB", user, texto, hashtags, url, clasificacion, "", img_url]
        add_row_to_sheet(fila)

        st.success("¡Listo! Clasificación y captura completadas.")
        st.image(filename)
        st.markdown(f"📄 **Clasificación:** `{clasificacion}`")
        st.markdown(f"[📂 Ver captura en Drive]({img_url})")
    else:
        st.warning("Por favor, ingresá un enlace válido.")
