from app.database.session import SessionLocal
from app.orchestrator.workflow import WorkflowEngine
from app.core.logging import logger

def run_async_interview_generation(project_id: str):
    """Triggers mock interview question generation asynchronously."""
    logger.info(f"[Task:Interview] Pre-generating question for project ID: {project_id}")
    db = SessionLocal()
    try:
        engine = WorkflowEngine(db)
        question_data = engine.run_interview_generate_workflow(project_id)
        logger.info(f"[Task:Interview] Pre-generation complete. Question: '{question_data['question']}'")
    except Exception as e:
        logger.error(f"[Task:Interview] Generation failed: {e}")
    finally:
        db.close()
