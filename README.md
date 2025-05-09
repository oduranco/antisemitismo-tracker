# 🧠 Antisemitismo Tracker

Esta app de Streamlit permite ingresar enlaces de redes sociales con contenido antisemita, clasificarlos, y guardar toda la información organizada en una hoja de cálculo de Google Sheets.

## 🚀 ¿Qué hace?

- Pega un enlace de X (Twitter), Instagram o Facebook
- Ingresa texto, hashtags, usuario y categoría
- Guarda automáticamente en una Google Sheet conectada
- Todo sin necesidad de usar bases de datos

## 🛠️ Cómo desplegar

1. Subí este repositorio a GitHub
2. En [streamlit.io/cloud](https://streamlit.io/cloud), conectá tu cuenta de GitHub y seleccioná este repo
3. En el apartado `Secrets`, agregá lo siguiente:

```toml
GSHEET_CREDENTIALS = '''
{ ...contenido completo del archivo JSON de tu cuenta de servicio... }
'''
```

4. Hacé Deploy y listo.

## 📁 Estructura

```
app.py              # Código principal de la app Streamlit
requirements.txt    # Dependencias necesarias para que funcione
README.md           # Este archivo
```

---

Hecho con 💥 y guanábanas por Mando + ChatGPT.