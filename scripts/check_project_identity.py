import sys
import os
import requests
import json

# Define the two environments found
envs = [
    {
        "name": "AnDo Current (.env)",
        "url": "https://jfcnxjxifpbllkwpduhw.supabase.co",
        "key": os.getenv("SUPABASE_KEY", "") # Fallback if needed, but I'll hardcode from what I read earlier or read file
    },
    {
        "name": "LandingPage (.env)",
        "url": "https://kdjpwknxthfypcmrfzwl.supabase.co",
        "key": "" # Will fill from reading LandingPage .env
    }
]

def check_env(name, url, key):
    print(f"\n--- Checking {name} ---")
    print(f"URL: {url}")
    
    if not key:
        print("No Valid Key found.")
        return

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    # 1. Check for 'ando_documents' (Key table in screenshot)
    target_table = "ando_documents"
    endpoint = f"{url}/rest/v1/{target_table}?select=count"
    
    try:
        res = requests.get(endpoint, headers=headers)
        if res.status_code == 200:
            print(f"✅ Tabla '{target_table}' ENCONTRADA.")
        elif res.status_code == 404:
            print(f"❌ La tabla '{target_table}' NO EXISTE en este proyecto.")
        else:
            print(f"⚠️ Error consultando '{target_table}': {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Error de conexión: {e}")

    # 2. Check for 'organizations'
    target_table = "organizations"
    endpoint = f"{url}/rest/v1/{target_table}?select=count"
    try:
        res = requests.get(endpoint, headers=headers)
        if res.status_code == 200:
            print(f"✅ Tabla '{target_table}' ENCONTRADA.")
        elif res.status_code == 404:
            print(f"❌ La tabla '{target_table}' NO EXISTE.")
    except:
        pass

# Read Keys manually to be sure
def read_keys():
    ando_key = ""
    landing_key = ""
    
    try:
        with open("c:/Repo/AnDo00/.env", "r") as f:
            for line in f:
                if "SUPABASE_KEY=" in line:
                    ando_key = line.split("=")[1].strip()
    except: pass

    try:
        with open("c:/Repo/LandingPage00/.env", "r") as f:
            for line in f:
                if "VITE_SUPABASE_ANON_KEY=" in line:
                    landing_key = line.split("=")[1].strip()
    except: pass

    return ando_key, landing_key

if __name__ == "__main__":
    ak, lk = read_keys()
    
    # Update envs
    envs[0]["key"] = ak
    envs[1]["key"] = lk
    
    for e in envs:
        check_env(e["name"], e["url"], e["key"])
