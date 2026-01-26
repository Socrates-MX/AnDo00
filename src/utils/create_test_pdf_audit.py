from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont
import os

def create_logo(filename="data/test_logo.png"):
    # Simular un logo corporativo simple
    img = Image.new('RGB', (100, 100), color = (200, 200, 200))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, 90, 90], outline=(0, 0, 0), fill=(100, 100, 255))
    d.text((35, 40), "LOGO", fill=(255, 255, 255))
    img.save(filename)
    print(f"Logo generado: {filename}")

def create_chart(filename="data/test_business_chart.png"):
    # Simular un gráfico de negocios con datos
    img = Image.new('RGB', (400, 200), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    # Ejes
    d.line([(50, 150), (350, 150)], fill=(0, 0, 0), width=2) # X
    d.line([(50, 50), (50, 150)], fill=(0, 0, 0), width=2)  # Y
    # Barras con valores
    d.rectangle([70, 100, 110, 150], fill=(255, 100, 100)) # Q1: 50
    d.text((75, 80), "Q1: 50", fill=(0, 0, 0))
    
    d.rectangle([150, 60, 190, 150], fill=(100, 255, 100)) # Q2: 90
    d.text((155, 40), "Q2: 90", fill=(0, 0, 0))
    
    d.rectangle([230, 40, 270, 150], fill=(100, 100, 255)) # Q3: 110
    d.text((235, 20), "Q3: 110", fill=(0, 0, 0))
    
    img.save(filename)
    print(f"Gráfico generado: {filename}")

def create_audit_pdf(pdf_filename="data/test_audit_with_logo.pdf"):
    c = canvas.Canvas(pdf_filename)
    
    # Encabezado con Logo
    c.drawString(200, 780, "REPORTE TRIMESTRAL DE AUDITORÍA - 2026")
    if os.path.exists("data/test_logo.png"):
        c.drawImage("data/test_logo.png", 50, 750, width=50, height=50)
    
    c.drawString(50, 700, "1. Resumen de Operaciones")
    c.drawString(50, 680, "Este documento contiene información confidencial de la empresa.")
    c.drawString(50, 660, "Se observa un crecimiento sostenido en los primeros tres trimestres.")

    # Gráfico Sustantivo
    if os.path.exists("data/test_business_chart.png"):
        c.drawImage("data/test_business_chart.png", 100, 400, width=350, height=175)
    
    c.drawString(50, 380, "Nota: Los datos del Q3 superan las expectativas iniciales en un 20%.")
    
    # Marca de Agua simulada (un texto muy suave o otra imagen pequeña)
    c.saveState()
    c.setFillAlpha(0.1)
    c.setFont("Helvetica", 80)
    c.drawCentredString(300, 300, "CONFIDENCIAL")
    c.restoreState()

    c.showPage()
    c.save()
    print(f"PDF de auditoría completa generado en: {pdf_filename}")

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    create_logo()
    create_chart()
    create_audit_pdf()
