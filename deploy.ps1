# Script de Despliegue para AnDo en Google Cloud Run
$PROJECT_ID = "getauditupcompliance"
$REGION = "us-central1"
$SERVICE_NAME = "ando-compliance-app"

Write-Host "--- Iniciando Despliegue de AnDo ---" -ForegroundColor Cyan

# 1. Asegurar que estamos en el proyecto correcto
gcloud config set project $PROJECT_ID

# 2. Habilitar APIs necesarias (solo por si acaso)
Write-Host "Verificando APIs de Google Cloud..."
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com

# 3. Leer variables de .env para el despliegue
# Nota: Esto es para facilitar el despliegue del prototipo.
Write-Host "Cargando configuración de .env..."
$envVars = ""
if (Test-Path ".env") {
    $lines = Get-Content ".env"
    foreach ($line in $lines) {
        if ($line -match "^([^#\s][^=]+)=(.*)$") {
            if ($envVars -ne "") { $envVars += "," }
            $envVars += "$($Matches[1])=$($Matches[2])"
        }
    }
}

# 4. Desplegar en Cloud Run
Write-Host "Subiendo código y desplegando en Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --source . `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --set-env-vars $envVars

Write-Host "--- Despliegue Finalizado ---" -ForegroundColor Green
Write-Host "Siguiente paso: Mapear el subdominio 'compliance.getauditup.com' en la consola de Cloud Run."
