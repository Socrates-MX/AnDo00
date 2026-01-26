from analyzers import index_analyzer

def generate_index_card(pages_data):
    """
    Analyzes page content to build a Table of Contents (Index) using AI.
    """
    ai_index = index_analyzer.extract_index_and_congruence(pages_data)
    
    if ai_index:
        return ai_index
    
    # Fallback if AI fails
    return {
        "title": "Índice (Generación Fallida)",
        "sections": [],
        "congruence": {"score": 0, "analysis": "No se pudo generar el análisis de índice."}
    }

def generate_executive_summary(pages_data, index_card):
    """
    Generates a text summary based on all analysis data.
    """
    return "Resumen Ejecutivo: Este documento trata sobre..."
