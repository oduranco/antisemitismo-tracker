
import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from transformers import pipeline
from datetime import datetime

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GSHEET_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Antisemitismo Tracker").sheet1

# Clasificador de texto (modelo liviano)
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Interfaz Streamlit
st.image("https://em-content.zobj.net/thumbs/120/apple/354/clipboard_1f4cb.png", width=40)
st.title("📋 Organizador de enlaces antisemitas")
st.write("Pegá un enlace de X, Instagram o Facebook. El sistema extraerá y clasificará automáticamente la información para cargarla en la tabla.")

enlace = st.text_input("🔗 Enlace (X, Instagram o Facebook)")
if enlace:
    red_social = "X" if "x.com" in enlace else "Instagram" if "instagram.com" in enlace else "Facebook"
    texto_extraido = enlace.split("/")[-1].replace("?", " ")  # Placeholder
    clasificacion = classifier(texto_extraido)[0]['label']
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = enlace.split("/")[-2] if "x.com" in enlace or "instagram.com" in enlace else ""
    if st.button("Guardar"):
        sheet.append_row([fecha, red_social, usuario, texto_extraido, "", enlace, clasificacion, "", ""])
        st.success("¡Guardado en la hoja de cálculo!")

