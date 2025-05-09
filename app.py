import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Organizador de enlaces antisemitas", layout="centered")
st.title("📋 Organizador de enlaces antisemitas")
st.markdown("Pegá un enlace de X, Instagram o Facebook. El sistema extraerá y clasificará automáticamente la información para cargarla en la tabla.")

# Clasificador IA
classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=1)

# Función para extraer texto del enlace
def extract_text(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs if p.get_text()])
        return re.sub(r"\s+", " ", text).strip()[:1000]
    except Exception as e:
        return ""

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GSHEET_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Acceder a la hoja de cálculo
sheet = client.open_by_url(st.secrets["GSHEET_URL"]).sheet1

# UI
url = st.text_input("🔗 Enlace (X, Instagram o Facebook)")
if url:
    extracted_text = extract_text(url)
    classification = classifier(extracted_text)[0]["label"] if extracted_text else "Sin texto"
    user_guess = "@" + url.split("/")[-2] if "x.com" in url or "twitter.com" in url else ""
else:
    extracted_text = ""
    classification = ""
    user_guess = ""

user = st.text_input("👤 Usuario", value=user_guess)
text = st.text_area("📝 Texto extraído", value=extracted_text, height=100)
hashtags = st.text_input("📙 Hashtags")
clasif = st.text_input("🧠 Clasificación IA", value=classification)
comentario = st.text_area("💬 Comentario manual")
fecha = datetime.today().strftime("%Y-%m-%d")

if st.button("Guardar"):
    sheet.append_row([fecha, "", user, text, hashtags, url, clasif, comentario, ""])
    st.success("✅ Enlace guardado correctamente.")