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
from app.database.models import Project, File, Symbol
from app.tools.parsers.go_parser import parse_go_file
from app.tools.parsers.java_parser import parse_java_file
from app.tools.parsers.cpp_parser import parse_cpp_file
from app.tools.parsers.markdown_parser import parse_markdown_file
from app.tools.project.chunker import chunk_file_for_indexing
from app.indexing.watcher import workspace_watcher

def run_test():
    print("=== Testing PEIS Workspace Intelligence (Phase 2) ===")

    # 1. Setup mock workspace files on disk
    temp_dir = tempfile.mkdtemp(prefix="peis_ws_intel_")
    print(f"Created temporary mock project workspace: {temp_dir}")
    
    # requirements.txt
    with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
        f.write("fastapi>=0.100.0\nsqlalchemy>=2.0.0\n# comments\nrequests\n")
        
    # .gitignore
    with open(os.path.join(temp_dir, ".gitignore"), "w") as f:
        f.write("*.log\nbuild/\n")
        
    # mock log file (should be ignored by gitignore)
    with open(os.path.join(temp_dir, "app.log"), "w") as f:
        f.write("Some logging data\n")

    # Python file
    py_file = os.path.join(temp_dir, "main.py")
    with open(py_file, "w") as f:
        f.write('''
from fastapi import FastAPI
app = FastAPI()

class Order(Base):
    id: str

@app.get("/checkout")
def checkout_orders():
    return {}
''')

    # Go file
    go_file = os.path.join(temp_dir, "service.go")
    with open(go_file, "w") as f:
        f.write('''
package main
type Client struct {
    ID string
}
func (c *Client) FetchData(url string) error {
    return nil
}
''')

    # Markdown README
    readme_file = os.path.join(temp_dir, "README.md")
    with open(readme_file, "w") as f:
        f.write('''
# Project PEIS
This is a local AI memory.

## Getting Started
First steps:
1. run setup
2. scan

| Package | Status |
|---|---|
| Core | Active |
''')

    client = TestClient(app)

    try:
        # 2. Verify Go Symbol Parser
        print("\nVerifying Go AST Symbol Parser...")
        go_symbols = parse_go_file(go_file)
        assert len(go_symbols) == 2, f"Expected 2 Go symbols, got {len(go_symbols)}"
        go_names = {s["name"] for s in go_symbols}
        assert "Client" in go_names
        assert "Client.FetchData" in go_names
        print("Go Symbol Parser PASSED.")

        # 3. Verify Markdown Section splits
        print("\nVerifying Markdown Document Parser...")
        md_data = parse_markdown_file(readme_file)
        assert len(md_data["headings"]) == 2, "Expected 2 headings."
        assert len(md_data["tables"]) == 1, "Expected 1 table."
        assert len(md_data["sections"]) == 2, "Expected 2 sections."
        print("Markdown Document Parser PASSED.")

        # 4. Verify Chunking utility
        print("\nVerifying Chunk splitting formatting...")
        chunks = chunk_file_for_indexing(readme_file, "proj-id", "file-id")
        assert len(chunks) >= 1, "No chunks generated."
        print(f"Chunks Count: {len(chunks)}")
        print(f"First Chunk content snippet: '{chunks[0]['content'][:40]}...'")
        print("Chunk splitting formatting PASSED.")

        # 5. Verify Workspace Registration Endpoint
        print("\nVerifying POST /api/workspace/register...")
        reg_res = client.post("/api/workspace/register", json={"path": temp_dir})
        assert reg_res.status_code == 200, f"Register failed: {reg_res.text}"
        
        project_data = reg_res.json()
        project_id = project_data["id"]
        assert project_data["framework"] == "FastAPI", f"Expected 'FastAPI', got '{project_data['framework']}'"
        print("Workspace Registration API PASSED.")

        # 6. Verify Workspace Scan & Hashing Indexer
        print("\nVerifying POST /api/projects/scan...")
        scan_res = client.post("/api/projects/scan", json={"path": temp_dir})
        assert scan_res.status_code == 200
        print(f"Scan API Result: {scan_res.json()}")
        
        # Verify SQLite has the database metadata
        db = SessionLocal()
        files_db = db.query(File).filter(File.project_id == project_id).all()
        # Verify that app.log is ignored because of .gitignore matching
        relative_paths = {f.relative_path for f in files_db}
        assert "app.log" not in relative_paths, "app.log was not skipped by gitignore rules!"
        assert "main.py" in relative_paths
        assert "service.go" in relative_paths
        assert "README.md" in relative_paths
        db.close()
        print("Incremental Scanning & Gitignores validations PASSED.")

        # 7. Verify Workspace Watcher registration
        print("\nVerifying GET /api/workspace/status/{id}...")
        status_res = client.get(f"/api/workspace/status/{project_id}")
        assert status_res.status_code == 200
        assert status_res.json()["active"] is True, "Background watcher is not active on this workspace path!"
        print("Workspace Watcher active monitoring PASSED.")

        # 8. Verify Project Structure trees Compiler
        print("\nVerifying GET /api/projects/{id}/structure...")
        struct_res = client.get(f"/api/projects/{project_id}/structure")
        assert struct_res.status_code == 200
        struct_data = struct_res.json()
        
        assert "folder_tree" in struct_data
        assert "module_tree" in struct_data
        assert "dependencies" in struct_data
        print(f"Detected project package dependencies list: {struct_data['dependencies']}")
        assert "requests" in struct_data["dependencies"], "Package 'requests' not extracted from requirements.txt!"
        print("Project Structure compiler PASSED.")

        print("\n=== ALL WORKSPACE INTELLIGENCE PIPELINE TESTS PASSED ===")

    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
    finally:
        shutil.rmtree(temp_dir)
        print("\nCleaned up test temp files.")

if __name__ == "__main__":
    run_test()
