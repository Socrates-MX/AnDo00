from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
import io

def create_dummy_pdf(filename="data/dummy.pdf"):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Documento de Prueba AnDo")
    c.drawString(100, 730, "Página 1: Introducción")
    c.drawString(100, 710, "Este es un texto de ejemplo para validar la extracción.")
    c.showPage()
    
    c.drawString(100, 750, "Página 2: Contenido")
    c.drawString(100, 730, "Aquí habría una imagen teóricamente.")
    c.showPage()
    
    c.save()
    print(f"PDF de prueba creado en: {filename}")

if __name__ == "__main__":
    create_dummy_pdf()
