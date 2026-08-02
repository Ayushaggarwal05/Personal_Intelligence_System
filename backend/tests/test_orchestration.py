import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.database.session import engine, Base, SessionLocal
from app.orchestrator.workflow import WorkflowEngine
from app.agents.planner_agent import PlannerAgent

def run_test():
    print("=== Testing Planning & Orchestration Workflow ===")
    
    # 1. Initialize SQLite
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 2. Verify Planner Agent Heuristics-First intent classification
        print("\nVerifying Heuristics-First Classifier in PlannerAgent...")
        planner = PlannerAgent()
        
        # Test greetings
        greet_res = planner.classify_intent("hello ASTA")
        print(f"Query: 'hello ASTA' -> Mode: {greet_res['mode']}, Objective: {greet_res['objective']}")
        assert greet_res["mode"] == "casual"
        
        # Test codebase exploration
        explore_res = planner.classify_intent("so whats in this folder i have")
        print(f"Query: 'so whats in this folder i have' -> Mode: {explore_res['mode']}, Objective: {explore_res['objective']}")
        assert explore_res["mode"] == "codebase_explore"
        
        # Test architecture discussion
        arch_res = planner.classify_intent("why react instead of vanilla js?")
        print(f"Query: 'why react instead of vanilla js?' -> Mode: {arch_res['mode']}, Objective: {arch_res['objective']}")
        assert arch_res["mode"] == "architecture_discuss"
        
        # Test learning guidance
        guidance_res = planner.classify_intent("give me a study plan")
        print(f"Query: 'give me a study plan' -> Mode: {guidance_res['mode']}, Objective: {guidance_res['objective']}")
        assert guidance_res["mode"] == "learning_guidance"
        
        print("Heuristics-First intent classification checks PASSED.")

        # 3. Test WorkflowEngine instantiation
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
