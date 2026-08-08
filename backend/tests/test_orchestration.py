import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.database.session import engine, Base, SessionLocal
from app.orchestrator.workflow import WorkflowEngine

def run_test():
    print("=== Testing Planning & Orchestration Workflow ===")
    
    # 1. Initialize SQLite
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 2. Test WorkflowEngine instantiation
        print("\nVerifying WorkflowEngine instantiation...")
        engine_inst = WorkflowEngine(db)
        assert engine_inst.db == db
        print("WorkflowEngine instantiation PASSED.")
        
        print("\n=== ORCHESTRATION TEST COMPLETED SUCCESSFULLY ===")

    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
