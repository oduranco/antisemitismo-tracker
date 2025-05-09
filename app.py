import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import datetime

st.set_page_config(page_title="Organizador de enlaces antisemitas", page_icon="📋")

st.title("📋 Organizador de enlaces antisemitas")
st.markdown("Pegá un enlace y completá los campos para organizar la información en la tabla.")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GSHEET_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1Tu0yijVrbl3I2hkGgHXUgR9kwbSbxMRmaM2oaVxRCJ8/edit#gid=0").sheet1

with st.form("entry_form"):
    url = st.text_input("🔗 Enlace (X, Instagram o Facebook)")
    texto = st.text_area("📝 Texto del post (si lo tiene)")
    clasificacion = st.selectbox("🧠 Clasificación", ["Negacionismo", "Conspiración", "Antisionismo", "Tropo clásico", "Otro"])
    hashtags = st.text_input("📙 Hashtags (opcional)")
    usuario = st.text_input("👤 Usuario (opcional)")
    submitted = st.form_submit_button("Guardar")

    if submitted:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, url, texto, clasificacion, hashtags, usuario]
        sheet.append_row(row)
        st.success("✅ Enlace guardado correctamente.")