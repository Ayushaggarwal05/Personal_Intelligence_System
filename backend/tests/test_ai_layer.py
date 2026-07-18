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
from app.services.workspace_service import WorkspaceService
from app.orchestrator.model_router import model_router
from app.agents.planner_agent import PlannerAgent
from app.database.models import Project

def run_test():
    print("=== Testing PEIS AI Layer (Phase 3) ===")

    # 1. Setup mock workspace files on disk
    temp_dir = tempfile.mkdtemp(prefix="peis_ai_layer_")
    print(f"Created temporary mock project workspace: {temp_dir}")
    
    with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
        f.write("fastapi>=0.100.0\n")
        
    py_file = os.path.join(temp_dir, "app.py")
    with open(py_file, "w") as f:
        f.write('''
from fastapi import FastAPI
app = FastAPI()

@app.get("/items")
def list_items():
    return []
''')

    client = TestClient(app)

    try:
        # 2. Verify Model Router local health checks fallback logic
        print("\nVerifying Model Router health checks falling back routes...")
        # Force local provider
        from app.core.settings import settings
        original_provider = settings.ACTIVE_LLM_PROVIDER
        settings.ACTIVE_LLM_PROVIDER = "local"
        
        # Test generation triggers fallback mock since local Ollama is likely offline/unconfigured
        res = model_router.generate("Generate a mock scorecard details.", json_format=True)
        assert "score" in res, "Fallback scoring template failed."
        print("Model Router fallback check PASSED.")
        
        # 3. Verify Planner Agent structures intent steps
        print("\nVerifying Planner Agent intent steps parsing...")
        planner = PlannerAgent()
        plan = planner.plan_execution("Explain my fastapi project details.")
        assert plan["intent"] == "explain"
        assert len(plan["steps"]) >= 1
        print("Planner Agent intent parsing PASSED.")

        # 4. Register and scan the project first to seed SQLite
        reg_res = client.post("/api/workspace/register", json={"path": temp_dir})
        assert reg_res.status_code == 200
        project_id = reg_res.json()["id"]
        
        scan_res = client.post("/api/projects/scan", json={"path": temp_dir})
        assert scan_res.status_code == 200
        print("Workspace seed indexed successfully.")

        # 5. Verify Project Explanation Workflow Endpoint (POST /api/chat/query)
        print("\nVerifying POST /api/chat/query explanation workflow...")
        query_payload = {
            "project_id": project_id,
            "message": "Explain the API overview of my project."
        }
        query_res = client.post("/api/chat/query", json=query_payload)
        assert query_res.status_code == 200, f"Chat failed: {query_res.text}"
        chat_data = query_res.json()
        assert "response" in chat_data
        print(f"Chat response length: {len(chat_data['response'])}")
        print("Chat Query Workflow PASSED.")

        # 6. Verify Mock Interview Cycle (POST /api/interview/start & submit)
        print("\nVerifying POST /api/interview/start...")
        start_payload = {"project_path": temp_dir}
        start_res = client.post("/api/interview/start", json=start_payload)
        assert start_res.status_code == 200, f"Start failed: {start_res.text}"
        interview_data = start_res.json()
        
        assert "interview_id" in interview_data
        assert "qa_id" in interview_data
        assert "question" in interview_data
        
        interview_id = interview_data["interview_id"]
        qa_id = interview_data["qa_id"]
        print(f"Interview Question generated: '{interview_data['question']}'")
        print("Interview Generation Workflow PASSED.")

        print("\nVerifying POST /api/interview/submit answer reviews...")
        submit_payload = {
            "interview_id": interview_id,
            "qa_id": qa_id,
            "user_answer": "I used FastAPI to implement REST endpoints returning items.",
            "project_path": temp_dir
        }
        submit_res = client.post("/api/interview/submit", json=submit_payload)
        assert submit_res.status_code == 200, f"Submit failed: {submit_res.text}"
        submit_data = submit_res.json()
        
        assert "evaluation" in submit_data
        assert "next_question" in submit_data
        evaluation = submit_data["evaluation"]
        assert "score" in evaluation
        assert "suggestions" in evaluation
        assert "missing_keywords" in evaluation
        
        print(f"Developer Scorecard: Score={evaluation['score']} | Suggestions={evaluation['suggestions']}")
        print(f"Next generated Question: '{submit_data['next_question']['question']}'")
        print("Interview Response Review Workflow PASSED.")

        # Restore original LLM provider settings
        settings.ACTIVE_LLM_PROVIDER = original_provider
        print("\n=== ALL AI LAYER WORKFLOW TESTS PASSED ===")

    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
    finally:
        shutil.rmtree(temp_dir)
        print("\nCleaned up test temp files.")

if __name__ == "__main__":
    run_test()
