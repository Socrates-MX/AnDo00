import requests
import time
import os
import sys

# Configuration
API_URL = "http://localhost:8000"
PDF_PATH = "/Volumes/GITHUB/AnDo00/data/temp/TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"

def main():
    print(f"🚀 Starting API Test (Headless Flow)")
    print(f"📄 Testing with file: {os.path.basename(PDF_PATH)}")
    
    if not os.path.exists(PDF_PATH):
        print("❌ Error: Test file not found!")
        return

    # 1. Upload
    print("\n[1] Uploading Document...")
    with open(PDF_PATH, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post(f"{API_URL}/analyze/upload", files=files)
            response.raise_for_status()
            data = response.json()
            task_id = data["task_id"]
            print(f"✅ Upload Successful! Task ID: {task_id}")
        except Exception as e:
            print(f"❌ Upload Failed: {e}")
            return

    # 2. Poll Status
    print("\n[2] Polling Status...")
    while True:
        try:
            status_res = requests.get(f"{API_URL}/analyze/{task_id}")
            status_data = status_res.json()
            status = status_data["status"]
            
            print(f"   ... Status: {status.upper()}")
            
            if status == "completed":
                print("\n✅ Analysis COMPLETED!")
                result = status_data["data"]
                print(f"   - Pages Processed: {result.get('page_count')}")
                print(f"   - Metadata: {result.get('metadata')}")
                
                # Check first page
                if result.get("pages"):
                    p1 = result["pages"][0]
                    text_preview = p1.get("text_content", "")[:100].replace("\n", " ")
                    print(f"   - Page 1 Preview: {text_preview}...")
                break
            
            elif status == "failed":
                print(f"\n❌ Analysis FAILED: {status_data.get('error')}")
                break
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Polling Error: {e}")
            break

if __name__ == "__main__":
    main()
