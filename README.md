# Organizador de enlaces antisemitas

Esta aplicación en Streamlit permite pegar un enlace de X (Twitter), Instagram o Facebook y automáticamente:

- Extrae el texto del post
- Clasifica el texto con un modelo de IA
- Completa los campos de un Google Sheet

## Cómo usar

1. Sube este repositorio a tu GitHub.
2. Crea una app en https://share.streamlit.io/
3. En los "Secrets", agrega:

```
[GSHEET_CREDENTIALS]
<tu json aquí, todo en una sola línea>

GSHEET_URL = "https://docs.google.com/spreadsheets/d/XXX/edit"
```

4. ¡Listo! Pega enlaces y guarda directamente en la hoja.