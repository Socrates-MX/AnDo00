import unicodedata

def clean_text(t):
    if not t: return ""
    return "".join(c for c in t if c.isalnum()).replace(" ", "").lower()

def get_tokens(text):
    if not text: return set()
    try:
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    except: pass
    text = "".join(c if c.isalnum() else " " for c in text.lower())
    return set(text.split())

def analyze_impersonation(pages_data, detailed_report):
    alerts = []
    
    # 1. ANALISIS DE METADATOS DE ANOTACIONES
    if pages_data:
        for page in pages_data:
            for annot in page.get('annots', []):
                content = annot.get('content', '').lower()
                detail = annot.get('detail', '').lower()
                user = annot.get('user', '')
                
                if user and (content or detail):
                    c_clean = clean_text(content)
                    d_clean = clean_text(detail)
                    u_clean = clean_text(user)
                    
                    is_date_only = len(c_clean) < 15 and c_clean.isdigit()
                    
                    if not is_date_only:
                        if u_clean not in c_clean and u_clean not in d_clean:
                            alerts.append({
                                "source": "Metadatos PDF",
                                "page": page['page_number'],
                                "user_system": user,
                                "name_document": annot.get('content') or annot.get('detail'), 
                                "description": "El usuario técnico del sello digital no coincide con el nombre en el documento.",
                                "severity": "warning"
                            })

    # 2. VALIDACIÓN CRUZADA: FIRMA VISUAL vs TABLA
    if detailed_report:
        revisores = detailed_report.get('revisado_aprobado', [])
        for rev in revisores:
            firma_txt = rev.get('firma', '')
            nombre_titular = rev.get('nombre', '')
            
            if "Firmado Electrónicamente por:" in firma_txt:
                nombre_sello = firma_txt.replace("Firmado Electrónicamente por:", "").strip()
                tokens_titular = get_tokens(nombre_titular)
                tokens_sello = get_tokens(nombre_sello)
                match = tokens_titular.issubset(tokens_sello) or tokens_sello.issubset(tokens_titular)
                
                if not match and tokens_titular and tokens_sello:
                     alerts.append({
                        "source": "Discrepancia Visual",
                        "page": "Tabla Firmas",
                        "user_system": nombre_sello,
                        "name_document": nombre_titular,
                        "description": "El titular listado no coincide con la identidad de la firma electrónica visual.",
                        "severity": "critical"
                    })
                    
    return alerts
