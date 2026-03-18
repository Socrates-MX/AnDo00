import hashlib
import os
import re
import time
from collections import defaultdict
from fastapi import HTTPException

# --- CONSTANTS ---
MAX_REQUESTS_PER_WINDOW = 5
WINDOW_SECONDS = 60
ORG_RATE_LIMITS = defaultdict(list)

def calculate_file_hash(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def normalize_filename(filename: str) -> str:
    """Normaliza el nombre del archivo para comparaciones."""
    name = os.path.splitext(filename)[0].lower().strip()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'\s*\(\d+\)$', '', name)
    name = re.sub(r'[\s_-]final$', '', name)
    name = re.sub(r'[\s_-]v\d+$', '', name)
    return name

def check_rate_limit(org_id: str):
    if not org_id: return
    current_time = time.time()
    ORG_RATE_LIMITS[org_id] = [t for t in ORG_RATE_LIMITS[org_id] if current_time - t < WINDOW_SECONDS]
    if len(ORG_RATE_LIMITS[org_id]) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(
            status_code=429, 
            detail=f"Límite de {MAX_REQUESTS_PER_WINDOW} análisis por minuto alcanzado."
        )
    ORG_RATE_LIMITS[org_id].append(current_time)
