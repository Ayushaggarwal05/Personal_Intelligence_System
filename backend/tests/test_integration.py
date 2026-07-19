import os
import sys
import tempfile
import shutil
import json
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal, Base, engine

def run_test():
    print("=== Testing PEIS Integration & API hardeners (Phase 4) ===")
    
    # 1. Setup mock workspace files on disk
    temp_dir = tempfile.mkdtemp(prefix="peis_integration_")
    print(f"Created temporary mock project workspace: {temp_dir}")
    
    with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
        f.write("fastapi>=0.100.0\nrequests\n")
        
    py_file = os.path.join(temp_dir, "checkout.py")
    with open(py_file, "w") as f:
        f.write('''
class OrderModel:
    id: str

def checkout_orders():
    pass
''')

    client = TestClient(app)

    try:
        # Register and scan project first to populate SQLite symbols
        reg_res = client.post("/api/workspace/register", json={"path": temp_dir})
        assert reg_res.status_code == 200
        project_id = reg_res.json()["id"]
        
        scan_res = client.post("/api/projects/scan", json={"path": temp_dir})
        assert scan_res.status_code == 200
        print("Indexed temporary workspace database records successfully.")

        # 2. Test System API diagnostics (/api/system/diagnostics)
        print("\nVerifying GET /api/system/diagnostics...")
        sys_res = client.get("/api/system/diagnostics")
        assert sys_res.status_code == 200
        sys_data = sys_res.json()
        assert sys_data["status"] == "online"
        assert sys_data["database"]["engine"] == "SQLite"
        print("System Diagnostics API PASSED.")

        # 3. Test Prompts API list (/api/prompts/list)
        print("\nVerifying GET /api/prompts/list...")
        prompt_res = client.get("/api/prompts/list")
        assert prompt_res.status_code == 200
        prompt_data = prompt_res.json()
        assert len(prompt_data["registered_templates"]) >= 3
        print("Prompts Registry API PASSED.")

        # 4. Test Settings API (/api/settings)
        print("\nVerifying GET /api/settings & POST /api/settings/keys...")
        set_res = client.get("/api/settings")
        assert set_res.status_code == 200
        assert set_res.json()["project_name"] == "Personal Engineering Intelligence System"
        
        prov_res = client.post("/api/settings/keys", json={"gemini_key": "AIzaSyTestKey", "groq_key": "gsk_TestKey"})
        assert prov_res.status_code == 200
        assert prov_res.json()["has_gemini_key"] is True
        assert prov_res.json()["has_groq_key"] is True
        print("Settings configurations APIs PASSED.")

        # 5. Test Diagram APIs (/api/diagrams)
        print("\nVerifying Diagrams Mermaid generators APIs...")
        # ER diagram
        er_res = client.get(f"/api/diagrams/er/{project_id}")
        assert er_res.status_code == 200
        assert "erDiagram" in er_res.json()["mermaid_code"]
        
        # Sequence diagram
        seq_res = client.get(f"/api/diagrams/sequence/{project_id}")
        assert seq_res.status_code == 200
        assert "sequenceDiagram" in seq_res.json()["mermaid_code"]
        
        # API Flow diagram
        flow_res = client.get(f"/api/diagrams/api-flow/{project_id}")
        assert flow_res.status_code == 200
        assert "graph" in flow_res.json()["mermaid_code"]
        print("Diagram markup builders APIs PASSED.")

        # 6. Test Search APIs (/api/search)
        print("\nVerifying GET /api/search hybrid keyword-semantic lookups...")
        # Search match
        search_res = client.get(f"/api/search?project_id={project_id}&query=checkout")
        assert search_res.status_code == 200
        results = search_res.json()["results"]
        assert len(results) >= 1
        assert "checkout" in results[0]["title"].lower()
        
        # Autocomplete suggestions
        sug_res = client.get(f"/api/search/suggestions?project_id={project_id}&prefix=che")
        assert sug_res.status_code == 200
        assert len(sug_res.json()["suggestions"]) >= 1
        print("Hybrid search and Autocomplete APIs PASSED.")

        # 7. Test Memory logs APIs (/api/memory)
        print("\nVerifying GET /api/memory logs and history managers...")
        # Log mock message to test retrieval
        db = SessionLocal()
        from app.agents.memory_agent import MemoryAgent
        mem_agent = MemoryAgent(db)
        mem_agent.record_chat_message(project_id, "user", "What are REST trade-offs?")
        db.close()
        
        # History
        hist_res = client.get(f"/api/memory/history/{project_id}")
        assert hist_res.status_code == 200
        assert len(hist_res.json()["history"]) >= 1
        
        # Topics
        top_res = client.get(f"/api/memory/topics/{project_id}")
        assert top_res.status_code == 200
        assert "tradeoffs" in top_res.json()["frequently_discussed_topics"]
        
        # Clear history
        del_res = client.delete(f"/api/memory/history/{project_id}")
        assert del_res.status_code == 200
        assert del_res.json()["success"] is True
        
        # Check cleared
        hist_check = client.get(f"/api/memory/history/{project_id}")
        assert len(hist_check.json()["history"]) == 0
        print("Conversational memory and history APIs PASSED.")

        # 8. Test WebSocket streaming endpoint
        print("\nVerifying WebSocket streaming connection tunnel...")
        with client.websocket_connect("/api/ws") as websocket:
            websocket.send_text("ping")
            data = websocket.receive_text()
            assert data == "pong", f"Expected 'pong', got '{data}'"
            
            websocket.send_text("hello-echo")
            data = websocket.receive_text()
            assert data == "echo: hello-echo"
        print("WebSocket ping-pong transmissions PASSED.")

        print("\n=== ALL SYSTEM INTEGRATION TESTS PASSED ===")

    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
    finally:
        shutil.rmtree(temp_dir)
        print("\nCleaned up test temp files.")

if __name__ == "__main__":
    run_test()
