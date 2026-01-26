import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def test_multimodal_pdf(file_path):
    print(f"Probando visión multimodal de Gemini con PDF: {file_path}")
    
    # Subir el archivo
    sample_file = genai.upload_file(path=file_path, display_name="Auditoria")
    print(f"Archivo subido: {sample_file.uri}")
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([
        sample_file,
        "Observa la tabla 'REVISADO Y APROBADO ELECTRÓNICAMENTE' en la primera página. "
        "Dime los nombres, firmas y fechas que aparecen en ella."
    ])
    
    print("\n--- RESPUESTA GEMINI MULTIMODAL ---")
    print(response.text)

if __name__ == "__main__":
    test_multimodal_pdf("data/archivo_maestro.pdf")
