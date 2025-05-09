
import streamlit as st
import requests
import re
import json
import pandas as pd
from transformers import pipeline
from google.oauth2 import service_account
import gspread

# --- Autenticación Google ---
creds_dict = json.loads(st.secrets["GOOGLE_CREDS"])
creds = service_account.Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Tu0yijVrbl3I2hkGgHXUgR9kwbSbxMRmaM2oaVxRCJ8/edit#gid=0"
SPREADSHEET_ID = SHEET_URL.split("/d/")[1].split("/")[0]

# --- Cargar modelo compatible ---
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def get_metadata_from_link(url):
    text = ""
    username = ""
    hashtags = []

    if "x.com" in url or "twitter.com" in url:
        tweet_id = url.split("/")[-1].split("?")[0]
        oembed_url = f"https://publish.twitter.com/oembed?url=https://twitter.com/anyuser/status/{tweet_id}"
        response = requests.get(oembed_url)
        if response.ok:
            raw = response.json()["html"]
            clean = re.sub("<[^<]+?>", "", raw)
            text = clean.strip()
            username_match = re.search(r"twitter.com/([^/]+)/status", url)
            if username_match:
                username = username_match.group(1)
            hashtags = re.findall(r"#\w+", text)
    elif "instagram.com" in url:
        text = "Publicación de Instagram"
    elif "facebook.com" in url:
        text = "Publicación de Facebook"
    
    return text, username, hashtags

def classify_text(text):
    try:
        result = classifier(text)[0]
        return result["label"]
    except:
        return "No detectado"

# --- Interfaz ---
st.set_page_config(page_title="Organizador de enlaces antisemitas", page_icon="🗂️", layout="centered")
st.title("🗂️ Organizador de enlaces antisemitas")
st.write("Pegá un enlace y automáticamente se completará la información disponible.")

with st.form("formulario"):
    url = st.text_input("🔗 Enlace (X, Instagram o Facebook)", placeholder="https://x.com/...")
    submitted = st.form_submit_button("Analizar y guardar")

    if submitted and url:
        with st.spinner("Procesando..."):
            texto, usuario, hashtags = get_metadata_from_link(url)
            clasificacion = classify_text(texto)

            data = [url, texto, clasificacion, ", ".join(hashtags), usuario]
            try:
                sh = gc.open_by_key(SPREADSHEET_ID)
                sh.sheet1.append_row(data)
                st.success("✅ Enlace guardado correctamente.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# --- Mostrar tabla con datos actuales ---
try:
    df = pd.DataFrame(gc.open_by_key(SPREADSHEET_ID).sheet1.get_all_records())
    st.subheader("📊 Enlaces registrados")
    st.dataframe(df)
except:
    st.warning("No se pudo cargar la hoja. Verificá permisos o conexión.")
