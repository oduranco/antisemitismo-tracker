import streamlit as st
from datetime import datetime, date
import pandas as pd

# Importar módulos locales
from utils import get_social_network
from ai_classifier import classify_text, load_classifier
from google_sheets_handler import append_to_sheet, EXPECTED_COLUMNS

# Configuración de la página de Streamlit
st.set_page_config(page_title="Detector de Antisemitismo", layout="wide")

st.title("Herramienta de Detección y Clasificación de Antisemitismo ✡️")
st.markdown("""
Esta aplicación te permite registrar y analizar publicaciones de redes sociales 
para identificar posibles manifestaciones de antisemitismo según la definición de la IHRA.
Ingresa los detalles del post manualmente.
""")

# --- Cargar Modelo de IA ---
# Se carga una vez y se cachea para mejorar el rendimiento.
classifier = load_classifier()
if classifier is None:
    st.error("El clasificador de IA no pudo cargarse. La funcionalidad de clasificación estará deshabilitada.")

# --- Formulario de Entrada de Datos ---
st.header("Registrar Nueva Publicación")

with st.form("new_post_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        url_post = st.text_input("🔗 Enlace del Post (URL)", placeholder="https://...")
        texto_post = st.text_area("📝 Texto del Post", height=200, placeholder="Copia y pega el texto completo del post aquí...")
    
    with col2:
        usuario_post = st.text_input("👤 Usuario", placeholder="@usuario o nombre de página")
        hashtags_post = st.text_input("️#️⃣ Hashtags (separados por coma)", placeholder="#tag1, #antisemitismo, #ejemplo")
        
        # Fecha de publicación original
        default_date = date.today()
        fecha_publicacion_original = st.date_input("🗓️ Fecha de Publicación Original del Post", value=default_date, max_value=default_date)

    submitted = st.form_submit_button("✅ Analizar y Guardar en Google Sheets")

# --- Lógica de Procesamiento ---
if submitted:
    if not url_post or not texto_post:
        st.error("⚠️ Por favor, completa al menos el Enlace del Post y el Texto del Post.")
    elif classifier is None:
         st.error("⚠️ El clasificador de IA no está disponible. No se puede procesar el post.")
    else:
        with st.spinner("Procesando y guardando... Por favor espera."):
            # 1. Determinar Red Social
            red_social = get_social_network(url_post)

            # 2. Clasificación con IA
            clasificacion_ia = classify_text(texto_post, classifier)

            # 3. Fecha de registro en la app (ahora)
            fecha_registro_app = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 4. Preparar datos para Google Sheets
            # Convertir fecha_publicacion_original (datetime.date) a string
            fecha_pub_str = fecha_publicacion_original.strftime("%Y-%m-%d")

            data_to_save = {
                "Fecha de Registro en App": fecha_registro_app,
                "Fecha de Publicación Original": fecha_pub_str,
                "Red Social": red_social,
                "Usuario": usuario_post,
                "Texto Extraído": texto_post,
                "Hashtags": hashtags_post,
                "Enlace": url_post,
                "Clasificación IA": clasificacion_ia
            }
            
            # 5. Guardar en Google Sheets
            success = append_to_sheet(data_to_save)

            if success:
                st.success("🎉 ¡Publicación analizada y guardada correctamente en Google Sheets!")
                st.balloons()
                
                # Mostrar un resumen de lo guardado
                st.subheader("Resumen de los Datos Guardados:")
                # Crear un DataFrame para mostrarlo bien formateado
                df_summary = pd.DataFrame([data_to_save])
                # Reordenar columnas para el display si es necesario, o usar EXPECTED_COLUMNS
                display_columns = [col for col in EXPECTED_COLUMNS if col in df_summary.columns]
                st.dataframe(df_summary[display_columns], use_container_width=True)
            else:
                st.error("❌ Hubo un error al guardar los datos en Google Sheets. Revisa los mensajes de error anteriores.")

st.markdown("---")
st.markdown("Desarrollado con cariño y preocupación.")
st.markdown("<p style='text-align: center;'>Si encuentras algún problema o tienes sugerencias, por favor contáctame.</p>", unsafe_allow_html=True)
