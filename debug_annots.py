
import os
import sys
import pypdf

def debug_annots():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    if not target_path: return

    reader = pypdf.PdfReader(target_path)
    page = reader.pages[0]
    
    if "/Annots" in page:
        print(f"Total anotaciones encontradas: {len(page['/Annots'])}")
        for i, annot in enumerate(page["/Annots"]):
            obj = annot.get_object()
            content = obj.get("/Contents")
            user = obj.get("/T")
            print(f"--- Anotación {i+1} ---")
            print(f"Content: {content}")
            print(f"User (/T): {user}")
            
            # Check AP (Appearance Stream) for text
            if "/AP" in obj:
                ap = obj["/AP"]
                if "/N" in ap:
                    appearance = ap["/N"].get_object()
                    if hasattr(appearance, "extract_text"):
                        print(f"AP Text: {appearance.extract_text().strip()}")

if __name__ == "__main__":
    debug_annots()
