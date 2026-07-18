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
from app.database.session import engine, Base, SessionLocal
from app.database.models import Project, File, Symbol

def run_test():
    print("=== Testing FastAPI PEIS Endpoints & Interview Pipeline ===")
    
    # 1. Initialize TestClient
    client = TestClient(app)
    
    # Create temp workspace
    temp_dir = tempfile.mkdtemp(prefix="peis_api_test_")
    mock_file = os.path.join(temp_dir, "auth.py")
    
    # Write mock codebase contents
    with open(mock_file, "w", encoding="utf-8") as f:
        f.write('''
def verify_access_token(token: str):
    """Parses JWT token and validates signature."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
''')

    try:
        # 2. Test Project Scan Endpoint
        print("\nTesting POST /api/projects/scan...")
        scan_res = client.post("/api/projects/scan", json={"path": temp_dir})
        print(f"Scan API Response: {scan_res.json()}")
        assert scan_res.status_code == 200, f"Expected status 200, got {scan_res.status_code}"
        
        # Verify db entries were updated
        db = SessionLocal()
        project = db.query(Project).filter(Project.path == temp_dir).first()
        assert project is not None, "Project not indexed in database."
        files = db.query(File).filter(File.project_id == project.id).all()
        assert len(files) == 1, "File metadata not registered."
        symbols = db.query(Symbol).filter(Symbol.file_id == files[0].id).all()
        assert len(symbols) == 1, "verify_access_token symbol was not parsed."
        print(f"Index check: parsed route/symbol '{symbols[0].name}' successfully.")
        db.close()
        print("Project Scan Endpoint PASSED.")

        # 3. Test Start Interview Session Endpoint
        print("\nTesting POST /api/interview/start...")
        start_res = client.post("/api/interview/start", json={"project_path": temp_dir})
        print(f"Start Interview Response: {start_res.json()}")
        assert start_res.status_code == 200, f"Expected 200, got {start_res.status_code}"
        
        start_data = start_res.json()
        interview_id = start_data["interview_id"]
        qa_id = start_data["qa_id"]
        question = start_data["question"]
        
        assert interview_id is not None, "interview_id is missing."
        assert qa_id is not None, "qa_id is missing."
        assert question is not None, "First question was not generated."
        print("Start Interview Endpoint PASSED.")

        # 4. Test Submit Answer Endpoint
        print("\nTesting POST /api/interview/submit...")
        # Respond with answer missing key access token concepts to test grader evaluation fallback
        user_answer = "I verify the user has access. I check the token and then authorize them."
        submit_payload = {
            "interview_id": interview_id,
            "qa_id": qa_id,
            "user_answer": user_answer,
            "project_path": temp_dir
        }
        
        submit_res = client.post("/api/interview/submit", json=submit_payload)
        print(f"Submit Answer Response:")
        print(json.dumps(submit_res.json(), indent=2))
        
        assert submit_res.status_code == 200, f"Expected 200, got {submit_res.status_code}"
        submit_data = submit_res.json()
        
        evaluation = submit_data["evaluation"]
        assert "score" in evaluation, "Evaluation score is missing."
        assert "missing_keywords" in evaluation, "Keywords analysis is missing."
        
        next_q = submit_data["next_question"]
        assert next_q["question"] is not None, "Next interview question is missing."
        
        print("\nSubmit Answer Endpoint & Grader fallback PASSED.")
        print("\n=== ALL MOCK INTERVIEW API PIPELINE TESTS PASSED ===")

    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
    finally:
        shutil.rmtree(temp_dir)
        print("\nCleaned up temp files.")

if __name__ == "__main__":
    run_test()
