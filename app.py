
import streamlit as st
import json
import datetime
import re
import requests
from transformers import pipeline
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Organizador de enlaces antisemitas", page_icon="📋")

st.title("📋 Organizador de enlaces antisemitas")
st.write("Pegá un enlace de X, Instagram o Facebook. El sistema extraerá y clasificará automáticamente la información para cargarla en la tabla.")

# Cargar credenciales
import os
import json
creds_dict = json.loads(st.secrets["GSHEET_CREDENTIALS"])
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Abrir la hoja
sheet = client.open_by_url(st.secrets["GSHEET_URL"]).sheet1

# Clasificador
classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=None)

# Funciones
def detectar_red_social(enlace):
    if "x.com" in enlace or "twitter.com" in enlace:
        return "X"
    elif "instagram.com" in enlace:
        return "Instagram"
    elif "facebook.com" in enlace:
        return "Facebook"
    return "Desconocida"

def extraer_usuario(enlace, red):
    if red == "X":
        match = re.search(r"x.com/(\w+)", enlace)
        return match.group(1) if match else ""
    elif red == "Instagram":
        match = re.search(r"instagram.com/p/[^/]+/", enlace)
        return ""  # Instagram no tiene user directo en enlace
    elif red == "Facebook":
        return ""
    return ""

def extraer_texto(enlace, red):
    if red == "X":
        try:
            response = requests.get(enlace)
            match = re.search(r'<meta name="description" content="([^"]+)"', response.text)
            return match.group(1) if match else ""
        except:
            return ""
    return ""

def extraer_hashtags(texto):
    return ", ".join(re.findall(r"#\w+", texto))

# Formulario
with st.form("formulario"):
    enlace = st.text_input("🔗 Enlace (X, Instagram o Facebook)")
    submitted = st.form_submit_button("Guardar")

    if submitted and enlace:
        red = detectar_red_social(enlace)
        usuario = extraer_usuario(enlace, red)
        texto = extraer_texto(enlace, red)
        hashtags = extraer_hashtags(texto)
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")

        try:
            clasificacion = classifier(texto)[0][0]["label"]
        except:
            clasificacion = "No detectado"

        fila = [fecha, red, usuario, texto, hashtags, enlace, clasificacion, "", ""]
        sheet.append_row(fila)
        st.success("✅ Enlace guardado automáticamente.")
