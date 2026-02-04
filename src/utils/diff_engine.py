import json

def compare_analyses(old_payload, new_payload):
    """
    Compares two analysis payloads and returns a summary of differences.
    Simplified for version V1.00.
    """
    diffs = []
    
    # Compare main fields
    old_main = old_payload.get("contenido_principal", {})
    new_main = new_payload.get("contenido_principal", {})
    
    for key in set(old_main.keys()) | set(new_main.keys()):
        if old_main.get(key) != new_main.get(key):
            diffs.append({
                "campo": f"Contenido Principal: {key}",
                "anterior": old_main.get(key, "N/A"),
                "nuevo": new_main.get(key, "N/A")
            })
            
    # Compare Objective/Scope
    if old_payload.get("objetivo_completo") != new_payload.get("objetivo_completo"):
        diffs.append({
            "campo": "Objetivo",
            "anterior": old_payload.get("objetivo_completo", "N/A"),
            "nuevo": new_payload.get("objetivo_completo", "N/A")
        })
        
    return diffs
