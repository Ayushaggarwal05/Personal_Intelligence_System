import os
import sys
import shutil
import tempfile
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app
from app.core.settings import settings
from app.core.workspace_config import workspace_config
from app.core.model_config import model_config
from app.database.session import SessionLocal, Base, engine
from app.database.repositories.project_repository import ProjectRepository
from app.database.repositories.file_repository import FileRepository
from app.database.repositories.diagram_repository import DiagramRepository
from app.database.models.project import Project
from app.database.models.file import File
from app.database.models.diagram import Diagram
from app.services.prompt_loader import prompt_loader
from app.utils.helpers import calculate_sha256, get_utc_now, format_bytes

def run_test():
    print("=== Testing PEIS Backend Foundation (Phase 1) ===")
    
    # 1. Verify Settings Loading
    print("\nVerifying configurations...")
    assert settings.PROJECT_NAME == "Personal Engineering Intelligence System"
    assert workspace_config.token_character_ratio == 4
    assert model_config.local.model_name == "qwen2.5:3b-instruct"
    print("Configurations loaded successfully.")

    # 2. Verify Logging File Creation
    print("\nVerifying logger writes...")
    logger_file = os.path.join(settings.LOGS_DIR, "peis.log")
    from app.core.logging import logger
    logger.info("Test log entry from verification suite.")
    assert os.path.exists(logger_file), f"Log file not created at {logger_file}"
    print(f"Log file exists and was written successfully at: {logger_file}")

    # 3. Verify Helper Utilities
    print("\nVerifying helper utilities...")
    h = calculate_sha256("test-content")
    assert len(h) == 64, "SHA-256 calculation failed."
    t = get_utc_now()
    assert isinstance(t, int), "UTC timestamp format incorrect."
    s = format_bytes(2048 * 1024)
    assert s == "2.00 MB", f"Expected '2.00 MB', got '{s}'"
    print("Helper utilities verified successfully.")

    # 4. Verify Prompt Loader
    print("\nVerifying Prompt Loader Service...")
    prompt = prompt_loader.load_prompt("interview", "test_prompt.txt")
    assert "System Prompt" in prompt, "Prompt placeholder not loaded correctly."
    print("Prompt loader service verified successfully.")

    # 5. Verify Database & Repositories CRUD Operations
    print("\nVerifying SQLite Database Repositories...")
    db = SessionLocal()
    project_repo = ProjectRepository(db)
    file_repo = FileRepository(db)
    diagram_repo = DiagramRepository(db)

    # Clean up any residual data first
    Base.metadata.create_all(bind=engine)
    
    try:
        # Create Project
        p_id = "test-project-uuid"
        proj = Project(id=p_id, name="Test Foundation Codebase", path="/home/user/test_project")
        project_repo.create(proj)
        
        fetched_proj = project_repo.get_by_id(p_id)
        assert fetched_proj is not None, "Failed to retrieve project by ID."
        assert fetched_proj.name == "Test Foundation Codebase"
        
        # Create File
        f_id = "test-file-uuid"
        file_rec = File(
            id=f_id,
            project_id=p_id,
            relative_path="main.py",
            file_hash="abcdef123456",
            last_modified=get_utc_now(),
            token_count=100
        )
        file_repo.create(file_rec)
        
        fetched_file = file_repo.get_by_relative_path(p_id, "main.py")
        assert fetched_file is not None, "Failed to retrieve file by relative path."
        
        # Create Diagram
        d_id = "test-diagram-uuid"
        diag = Diagram(
            id=d_id,
            project_id=p_id,
            type="architecture",
            mermaid_code="graph TD; A-->B"
        )
        diagram_repo.create(diag)
        
        fetched_diag = diagram_repo.get_by_project_and_type(p_id, "architecture")
        assert fetched_diag is not None, "Failed to retrieve diagram."
        
        print("Database Repositories CRUD operations PASSED.")
        
        # Clean up database test entries
        diagram_repo.delete(d_id)
        file_repo.delete(f_id)
        project_repo.delete(p_id)
        
    finally:
        db.close()

    # 6. Verify FastAPI TestClient routes
    print("\nVerifying FastAPI Status routes...")
    client = TestClient(app)
    
    # Health endpoint
    h_res = client.get("/health")
    assert h_res.status_code == 200
    assert h_res.json() == {"status": "healthy"}
    
    # Version endpoint
    v_res = client.get("/version")
    assert v_res.status_code == 200
    assert "version" in v_res.json()
    
    # Status endpoint
    s_res = client.get("/status")
    assert s_res.status_code == 200
    assert s_res.json()["status"] == "online"
    
    print("FastAPI routes validation PASSED.")
    print("\n=== PHASE 1 FOUNDATION TEST SUCCESSFUL ===")

if __name__ == "__main__":
    run_test()
