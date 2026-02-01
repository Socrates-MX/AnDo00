from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw
import os

def create_image(filename="data/test_chart.png"):
    img = Image.new('RGB', (200, 100), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 50, 90], fill=(255, 0, 0)) # Red bar
    d.rectangle([60, 30, 100, 90], fill=(0, 255, 0)) # Green bar
    d.rectangle([110, 50, 150, 90], fill=(0, 0, 255)) # Blue bar
    img.save(filename)
    print(f"Imagen generada: {filename}")

def create_pdf_with_image(pdf_filename="data/dummy_with_image.pdf", img_filename="data/test_chart.png"):
    c = canvas.Canvas(pdf_filename)
    
    c.drawString(100, 750, "Documento con Imágenes - Prueba AnDo")
    c.drawString(100, 730, "A continuación se muestra un gráfico de prueba:")
    
    # Draw the image
    if os.path.exists(img_filename):
        c.drawImage(img_filename, 100, 500, width=200, height=100)
    else:
        print(f"Error: No se encontró la imagen {img_filename}")

    c.showPage()
    c.save()
    print(f"PDF con imagen generado en: {pdf_filename}")

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    create_image()
    create_pdf_with_image()
