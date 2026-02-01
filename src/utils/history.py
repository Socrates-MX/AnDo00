import json
import os
import hashlib
from datetime import datetime

HISTORY_FILE = "data/history.json"

def get_file_hash(file_path):
    """Calculates SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_history():
    """Loads history from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_history(history_data):
    """Saves history to JSON file."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)

def register_document(file_path):
    """Registers a new document or returns existing info."""
    file_hash = get_file_hash(file_path)
    history = load_history()
    
    current_time = "25 de enero del 2026"  # Fixed date per rules for this session context
    # In a real dynamic system we'd use: datetime.now().strftime("%d de %B del %Y")
    
    if file_hash in history:
        return history[file_hash], False # Existing

    # New entry
    doc_info = {
        "id": file_hash,
        "filename": os.path.basename(file_path),
        "first_seen": current_time,
        "versions": []
    }
    history[file_hash] = doc_info
    save_history(history)
    return doc_info, True # New

def log_analysis(file_hash, version_data):
    """Logs a specific analysis version."""
    history = load_history()
    if file_hash in history:
        history[file_hash]["versions"].append(version_data)
        save_history(history)
