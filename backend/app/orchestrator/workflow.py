import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.exceptions import PEISException, ProjectNotFoundException
from app.database.repositories.project_repository import ProjectRepository
from app.database.repositories.file_repository import FileRepository
from app.database.repositories.symbol_repository import SymbolRepository
from app.database.repositories.interview_repository import InterviewRepository, InterviewQARepository
from app.agents.project_agent import ProjectAgent
from app.agents.interview_agent import InterviewAgent
from app.agents.review_agent import ReviewAgent
from app.agents.reflection_agent import ReflectionAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.memory_agent import MemoryAgent
from app.utils.helpers import get_utc_now
import uuid

class WorkflowEngine:
    """Core workflow engine executing multi-agent steps for chat, mock interview, and codebase comparison."""
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.file_repo = FileRepository(db)
        self.symbol_repo = SymbolRepository(db)
        self.interview_repo = InterviewRepository(db)
        self.qa_repo = InterviewQARepository(db)
        
        # Instantiate Agents
        self.planner = PlannerAgent()
        self.project_agent = ProjectAgent()
        self.interview_agent = InterviewAgent()
        self.review_agent = ReviewAgent()
        self.reflection_agent = ReflectionAgent()
        self.memory_agent = MemoryAgent(db)

    def run_explain_workflow(self, project_id: str, query: str) -> str:
        """Executes explanation workflow: Retrieval -> History Context -> Project Agent -> Memory Record."""
        logger.info(f"[WorkflowEngine] Starting Project Explanation Workflow for project: {project_id}")
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        # 1. Fetch recent chat history context
        history_context = self.memory_agent.get_conversation_context(project_id, limit=6)

        # 2. Retrieval Layer (Deterministic symbol lookup)
        symbols = self.symbol_repo.search_in_project(project_id, search_query="", limit=15)
        symbols_context = "\n".join([
            f"- [{s.type.upper()}] {s.name}: {s.signature or ''}" 
            for s in symbols
        ]) or "No structures indexed yet."

        # 3. Project Intelligence Agent Layer
        response = self.project_agent.answer_user_query(
            project_name=project.name,
            framework=project.framework or "Python/FastAPI",
            database_type=project.database_type or "SQLite",
            symbols_context=symbols_context,
            user_query=query,
            chat_history=history_context
        )

        # Log to conversational memory
        self.memory_agent.record_chat_message(project_id, "user", query)
        self.memory_agent.record_chat_message(project_id, "assistant", response)
        
        return response

    def run_explain_stream_workflow(self, project_id: str, query: str):
        """Streams project explanation tokens and records final output into SQLite chat memory."""
        logger.info(f"[WorkflowEngine] Starting Project Explanation Streaming Workflow for project: {project_id}")
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        history_context = self.memory_agent.get_conversation_context(project_id, limit=6)
        symbols = self.symbol_repo.search_in_project(project_id, search_query="", limit=15)
        symbols_context = "\n".join([
            f"- [{s.type.upper()}] {s.name}: {s.signature or ''}" 
            for s in symbols
        ]) or "No structures indexed yet."

        full_response_chunks = []
        for token in self.project_agent.answer_user_query_stream(
            project_name=project.name,
            framework=project.framework or "Python/FastAPI",
            database_type=project.database_type or "SQLite",
            symbols_context=symbols_context,
            user_query=query,
            chat_history=history_context
        ):
            full_response_chunks.append(token)
            yield token

        # Record to memory upon completion
        complete_response = "".join(full_response_chunks)
        self.memory_agent.record_chat_message(project_id, "user", query)
        self.memory_agent.record_chat_message(project_id, "assistant", complete_response)

    def run_interview_generate_workflow(self, project_id: str) -> Dict[str, Any]:
        """Executes interview question workflow: Planner -> Retrieval -> Interview Coach -> Reflection."""
        logger.info(f"[WorkflowEngine] Starting Interview Generation Workflow for project: {project_id}")
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        # 1. Check if active interview session exists, otherwise create one
        active_interviews = self.interview_repo.list_by_project(project_id)
        if active_interviews:
            interview = active_interviews[-1] # reuse last session
        else:
            interview = self.interview_repo.create(
                self.interview_repo.model(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    created_at=get_utc_now()
                )
            )

        # 2. Retrieval Layer (Fetch structures & past weak areas)
        symbols = self.symbol_repo.search_in_project(project_id, search_query="", limit=15)
        symbols_context = "\n".join([
            f"- [{s.type.upper()}] {s.name}" 
            for s in symbols
        ])
        
        # 3. Interview Coach execution
        context = {"db": self.db, "project_path": project.path}
        q_data = self.interview_agent.generate_question(context)

        # 4. Save question to session history
        qa_id = str(uuid.uuid4())
        qa_rec = self.qa_repo.model(
            id=qa_id,
            interview_id=interview.id,
            question=q_data["question"],
            timestamp=get_utc_now()
        )
        self.qa_repo.create(qa_rec)

        return {
            "interview_id": interview.id,
            "qa_id": qa_id,
            "question": q_data["question"],
            "focus_area": q_data.get("focus_area", "Architecture"),
            "type": q_data.get("type", "technical")
        }

    def run_interview_review_workflow(self, interview_id: str, qa_id: str, user_answer: str, project_id: str) -> Dict[str, Any]:
        """Executes response grading workflow: Planner -> Retrieval -> Review -> Reflection -> Response."""
        logger.info(f"[WorkflowEngine] Starting Response Grading Review Workflow for session: {interview_id}")
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        qa_rec = self.qa_repo.get_by_id(qa_id)
        if not qa_rec:
            raise PEISException(f"Interview Question QA ID '{qa_id}' not found.", status_code=404)

        # 1. Review Agent scoring
        context = {"db": self.db, "project_path": project.path}
        scorecard = self.review_agent.score_answer(context, qa_rec.question, user_answer)

        # 2. Reflection Agent audit verification (purge hallucinated symbols suggestion)
        audited_scorecard = self.reflection_agent.validate_review_scorecard(context, scorecard)

        # 3. Persist review results in SQLite
        qa_rec.user_answer = user_answer
        qa_rec.scorecard = json.dumps(audited_scorecard)
        qa_rec.score = audited_scorecard.get("score", 0)
        self.db.commit()

        return audited_scorecard

    def run_compare_workflow(self, project_id_a: str, project_id_b: str) -> str:
        """Executes project comparison workflow: Planner -> Retrieval -> Project Intel -> Response."""
        logger.info(f"[WorkflowEngine] Starting Project Comparison Workflow...")
        project_a = self.project_repo.get_by_id(project_id_a)
        project_b = self.project_repo.get_by_id(project_id_b)
        
        if not project_a or not project_b:
            raise PEISException("One of the project IDs for comparison was not found.", status_code=404)

        profile_a = {
            "name": project_a.name,
            "framework": project_a.framework or "Unknown",
            "database": project_a.database_type or "SQLite"
        }
        profile_b = {
            "name": project_b.name,
            "framework": project_b.framework or "Unknown",
            "database": project_b.database_type or "SQLite"
        }

        # Project Agent compares systems
        comparison_res = self.project_agent.compare_projects(profile_a, profile_b)
        return comparison_res
