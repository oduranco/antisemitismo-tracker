# Sistema de Monitoreo de Publicaciones Antisemitas

Este proyecto permite pegar enlaces de X, Instagram o Facebook y:
- Tomar una captura de pantalla
- Clasificar automáticamente el contenido (burla, negacionismo, conspiración)
- Guardar los datos y la captura en Google Sheets y Google Drive

## Requisitos

1. Python 3.9+
2. Instalar dependencias:
```
pip install -r requirements.txt
playwright install
```

3. Colocar tu archivo de credenciales como `credentials.json` en la raíz del proyecto

## Ejecutar

```
streamlit run app.py
```

## Despliegue

Podés subir este proyecto a [https://streamlit.io/cloud](https://streamlit.io/cloud) y vincular tu archivo `credentials.json` como secreto o variable protegida.