import os
import shutil
import tempfile
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.database.session import engine, Base, SessionLocal
from app.database.models import Project, File
from app.indexing.incremental_indexer import run_incremental_index

def run_test():
    print("=== Testing Incremental Indexer ===")
    
    # 1. Create a temporary folder to serve as dummy workspace
    temp_dir = tempfile.mkdtemp(prefix="peis_test_ws_")
    print(f"Created temporary test workspace: {temp_dir}")
    
    file_a = os.path.join(temp_dir, "app.py")
    file_b = os.path.join(temp_dir, "utils.py")
    
    # Write initial files
    with open(file_a, "w", encoding="utf-8") as f:
        f.write("def main():\n    print('Hello World')\n")
    with open(file_b, "w", encoding="utf-8") as f:
        f.write("def add(a, b):\n    return a + b\n")

    # 2. Setup SQLite tables
    print("Initializing test database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 3. Perform First Index
        print("\n--- Running First Index (Initial Sync) ---")
        res1 = run_incremental_index(db, temp_dir)
        print(f"Index 1 Result: {res1}")
        
        project = db.query(Project).filter(Project.path == temp_dir).first()
        assert project is not None, "Project record was not created!"
        print(f"Registered project ID: {project.id}")
        
        files = db.query(File).filter(File.project_id == project.id).all()
        assert len(files) == 2, f"Expected 2 file records in DB, found {len(files)}!"
        print("Initial Sync verification PASSED.")
        
        # 4. Modify Workspace (Add file_c, Modify file_a, Delete file_b)
        print("\n--- Modifying Workspace ---")
        file_c = os.path.join(temp_dir, "routes.py")
        with open(file_c, "w", encoding="utf-8") as f:
            f.write("def get_routes():\n    return []\n")
            
        with open(file_a, "w", encoding="utf-8") as f:
            f.write("def main():\n    print('Hello Modified World')\n")
        # Offset modification time by +10 seconds to ensure the scanner detects the change
        stat = os.stat(file_a)
        os.utime(file_a, (stat.st_atime, stat.st_mtime + 10))
            
        os.remove(file_b)
        print("Workspace modifications completed.")
        
        # 5. Perform Second Index
        print("\n--- Running Second Index (Incremental Sync) ---")
        res2 = run_incremental_index(db, temp_dir)
        print(f"Index 2 Result: {res2}")
        
        assert res2["new_count"] == 1, f"Expected 1 new file, got {res2['new_count']}!"
        assert res2["modified_count"] == 1, f"Expected 1 modified file, got {res2['modified_count']}!"
        assert res2["deleted_count"] == 1, f"Expected 1 deleted file, got {res2['deleted_count']}!"
        
        files_after = db.query(File).filter(File.project_id == project.id).all()
        assert len(files_after) == 2, f"Expected 2 file records after sync, found {len(files_after)}!"
        
        # Ensure file_b is gone, and file_c is added
        paths_in_db = {f.relative_path for f in files_after}
        assert "routes.py" in paths_in_db, "routes.py not found in DB!"
        assert "utils.py" not in paths_in_db, "utils.py was not deleted from DB!"
        
        print("\nIncremental Sync verification PASSED.")
        print("=== TEST COMPLETED SUCCESSFULLY ===")
        
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
    finally:
        # Cleanup
        db.close()
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary workspace: {temp_dir}")

if __name__ == "__main__":
    run_test()
