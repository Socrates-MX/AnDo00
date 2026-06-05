import os
import sys
import json
import asyncio

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api')))

from core.tasks import run_analysis_task, tasks_db

async def main():
    pdf_path = "/Volumes/GITHUB/AnDo00/temp_uploads/10be703a-8593-4e82-8682-35ca5ee5d43d_TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    task_id = "test_task_123"
    tasks_db[task_id] = {
        "status": "pending",
        "filename": "TRA-P-01.pdf"
    }

    print(f"Starting analysis for {pdf_path}...")
    # Mocking consume_credit to not fail
    import core.tasks
    core.tasks.consume_credit = lambda o, a, c: True
    
    await run_analysis_task(task_id, pdf_path)
    
    result = tasks_db[task_id]
    print("\n--- ANALYSIS COMPLETED ---")
    print(f"Status: {result.get('status')}")
    if 'error' in result:
        print(f"Error: {result['error']}")
    
    # Check if result has token usage
    # Since the analyzers just print to console or return json, we might need to grep the output
    print("\nSaving detailed report to test_output.json...")
    with open("test_output.json", "w", encoding="utf-8") as f:
        json.dump(result.get("result", {}), f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
