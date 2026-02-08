# Usamos una imagen base de Python oficial, ligera (Slim)
FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos de requerimientos primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instalamos las dependencias del sistema necesarias para PDF/OCR (Poppler, Tesseract) y herramientas de compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    poppler-utils \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Actualizamos pip e instalamos las librerías de Python
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente de la API
COPY api/ ./api/
COPY src/ ./src/

# Exponemos el puerto que usará Cloud Run (por defecto 8080)
ENV PORT 8080

# Comando para ejecutar la aplicación con Uvicorn (Servidor de Producción)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
