import streamlit as st
from transformers import pipeline

# Categorías basadas en la IHRA (ajustadas para ser descriptivas para el modelo)
IHRA_CATEGORIES = [
    "Incitación directa a la violencia o daño contra judíos.",
    "Alegaciones estereotípicas, deshumanizantes, demonizadoras o difamatorias sobre judíos como colectivo, o mitos sobre conspiraciones judías mundiales o control judío.",
    "Culpar a los judíos como pueblo por fechorías (reales o imaginarias) cometidas por individuos o grupos judíos (no relacionado directamente con Israel).",
    "Negación o distorsión del Holocausto (negar hechos, alcance, mecanismos o intencionalidad; o acusar a judíos/Israel de inventarlo/exagerarlo).",
    "Acusaciones a ciudadanos judíos de ser más leales a Israel o a prioridades judías mundiales que a sus propias naciones (doble lealtad).",
    "Negación del derecho del pueblo judío a la autodeterminación, por ejemplo, afirmando que la existencia del Estado de Israel es una empresa racista.",
    "Aplicar un doble rasero a Israel exigiendo un comportamiento no esperado ni demandado a ninguna otra nación democrática.",
    "Uso de símbolos e imágenes del antisemitismo clásico (ej. libelo de sangre, deicidio) para caracterizar a Israel o a los israelíes.",
    "Comparar la política israelí contemporánea con la de los nazis.",
    "Considerar a los judíos colectivamente responsables de las acciones del Estado de Israel.",
    "Expresiones generales de odio hacia los judíos no cubiertas específicamente por otras categorías."
]

# Nombres cortos de las categorías para mostrar en la hoja de cálculo (deben corresponder en orden con IHRA_CATEGORIES)
IHRA_SHORT_NAMES = [
    "Incitación a la Violencia/Daño",
    "Estereotipos/Conspiraciones",
    "Culpa Colectiva (No-Israel)",
    "Negación/Distorsión del Holocausto",
    "Acusaciones de Doble Lealtad",
    "Deslegitimación de Israel/Negación Autodeterminación",
    "Doble Rasero contra Israel",
    "Tropos Antisemitas Clásicos contra Israel",
    "Comparaciones Políticas Israelíes con Nazis",
    "Culpa Colectiva (Israel)",
    "Odio Explícito General"
]


@st.cache_resource # Cache para no recargar el modelo en cada interacción
def load_classifier():
    """
    Carga el modelo de clasificación zero-shot.
    Puedes cambiar 'facebook/bart-large-mnli' por otro si lo prefieres,
    por ejemplo, uno más enfocado en español o multilingüe como 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli'.
    """
    try:
        return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    except Exception as e:
        st.error(f"Error al cargar el modelo de IA: {e}")
        st.error("Esto puede deberse a problemas de red o a que el modelo no está disponible. Intenta recargar la página.")
        return None

def classify_text(text_to_classify, classifier_pipeline):
    """
    Clasifica el texto usando el pipeline de Hugging Face y las categorías IHRA.
    Devuelve una cadena con las categorías que superan un umbral.
    """
    if not text_to_classify or not classifier_pipeline:
        return "Clasificación no disponible"

    try:
        # El modelo 'facebook/bart-large-mnli' funciona mejor con la hipótesis formulada como una frase.
        # Aunque aquí pasamos directamente las categorías, la librería maneja la plantilla adecuada.
        results = classifier_pipeline(text_to_classify, IHRA_CATEGORIES, multi_label=True)
        
        # Umbral de confianza para considerar una categoría como relevante
        threshold = 0.6 # Puedes ajustar este umbral
        
        relevant_categories = []
        if results and 'labels' in results and 'scores' in results:
            for label, score in zip(results['labels'], results['scores']):
                if score >= threshold:
                    # Buscamos el índice de la descripción completa para obtener el nombre corto
                    try:
                        idx = IHRA_CATEGORIES.index(label)
                        relevant_categories.append(IHRA_SHORT_NAMES[idx])
                    except ValueError:
                        # Si la etiqueta no se encuentra (raro), simplemente la añadimos
                        relevant_categories.append(label) 
        
        if not relevant_categories:
            return "Ninguna categoría de antisemitismo detectada (según umbral)"
        
        return ", ".join(relevant_categories)

    except Exception as e:
        st.error(f"Error durante la clasificación del texto: {e}")
        return "Error en clasificación"
