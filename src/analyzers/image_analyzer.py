import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def analyze_images_on_page(page_content):
    """
    Analyzes images on a page.
    Currently a placeholder for extraction logic, but connected to generation.
    """
    # In a real scenario, we would extract image bytes here.
    # For this prototype, we return an empty list or mock data to valid integration.
    return []

def generate_image_description(image_data):
    """
    Sends an image to Google Gemini for description.
    """
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        return "[MOCK] Configura tu GOOGLE_API_KEY en .env para usar Gemini Real."

    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        # Note: image_data should be PIL Image or bytes. 
        # For this prototype step, we assume image_data is valid input or handle error.
        # response = model.generate_content(["Describe this image for a business audit.", image_data])
        # return response.text
        return "[MOCK CONNECTED] Gemini API Configurada. (Falta pasar imagen real)"
    except Exception as e:
        return f"[ERROR] Falló la llamada a Gemini: {e}"
