import json
from typing import Dict, Any, List, Optional
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
from app.tools.filesystem.read_file import read_workspace_file_content
from app.tools.project.detect_dependencies import extract_dependencies

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

    def _retrieve_relevant_code_context(self, project_id: str, project_path: str, query: str) -> str:
        """Dynamically retrieves relevant symbols and file contents based on user query keywords."""
        stop_words = {"how", "is", "the", "file", "working", "does", "what", "can", "you", "tell", "me", "in", "my", "project", "code", "explain", "where", "show"}
        words = [w.strip("?.,!\"'()[]{}").lower() for w in query.split() if len(w.strip("?.,!\"'()[]{}")) > 2]
        keywords = [w for w in words if w not in stop_words]

        matched_symbols = []
        matched_file_snippets = []
        seen_symbol_ids = set()
        missing_files = []

        # Get list of all indexed files to verify physical existence
        all_project_files = self.file_repo.list_by_project(project_id)
        existing_paths = [f.relative_path.lower() for f in all_project_files]

        # 1. Search symbols and files matching keywords
        for kw in keywords:
            is_file_query = kw.endswith((".py", ".ts", ".js", ".json", ".yml", ".yaml", ".md", ".txt")) or kw in {"dockerfile", "docker", "docker-compose"}
            if is_file_query:
                # If no matching path exists, report as missing in tool search
                if not any(kw in p for p in existing_paths):
                    missing_files.append(kw)

            syms = self.symbol_repo.search_in_project(project_id, search_query=kw, limit=10)
            for s in syms:
                if s.id not in seen_symbol_ids:
                    seen_symbol_ids.add(s.id)
                    matched_symbols.append(s)
                    
            files = self.file_repo.search_by_keyword(project_id, keyword=kw, limit=3)
            for f in files:
                try:
                    content = read_workspace_file_content(project_path, f.relative_path)
                    snippet = content[:1500] + ("\n... [truncated]" if len(content) > 1500 else "")
                    matched_file_snippets.append(f"--- File: {f.relative_path} ---\n{snippet}")
                except Exception:
                    pass

        # If no specific keyword matches, fallback to top project symbols
        if not matched_symbols:
            matched_symbols = self.symbol_repo.search_in_project(project_id, search_query="", limit=15)

        symbols_str = "\n".join([
            f"- [{s.type.upper()}] {s.name}: {s.signature or ''}" 
            for s in matched_symbols
        ]) or "No matching structures found."

        # Get libraries list using dependencies tool
        dependencies = []
        try:
            dependencies = extract_dependencies(project_path)
        except Exception:
            pass
        dependencies_str = ", ".join(dependencies) if dependencies else "None detected."

        context_parts = []
        context_parts.append(f"### Key Libraries / Dependencies Used:\n{dependencies_str}")

        if missing_files:
            alerts = [f"- [SEARCH TOOL ALERT]: The file/resource matching '{f}' was searched in the workspace but is NOT present on disk." for f in missing_files]
            context_parts.append("### TOOL EXECUTION RESULTS:\n" + "\n".join(alerts))

        if matched_file_snippets:
            context_parts.append("### Relevant File Code Snippets:\n" + "\n\n".join(matched_file_snippets))
            
        context_parts.append(f"### Relevant AST Symbols:\n{symbols_str}")

        return "\n\n".join(context_parts)

    def _format_conversation_history(self, history: Optional[List[Dict[str, str]]]) -> str:
        """Converts incoming frontend message list history to text context for prompt injection."""
        if not history:
            return "No previous messages."
            
        formatted_lines = []
        for msg in history:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "").strip()
            
            # Skip empty or initial greeting templates
            if not content or "Hello! I am ASTA" in content or "Hello! I am PEIS" in content:
                continue
            formatted_lines.append(f"{role}: {content}")
            
        if not formatted_lines:
            return "No previous messages."
            
        return "\n".join(formatted_lines[-6:])

    def run_explain_workflow(self, project_id: str, query: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Executes explanation workflow: Retrieval -> History Context -> Project Agent -> Memory Record."""
        logger.info(f"[WorkflowEngine] Starting Project Explanation Workflow for project: {project_id}")
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        # 0. Intercept answer submissions for ReviewAgent scoring
        query_lower = query.lower().strip()
        is_answer = False
        user_answer = query
        for prefix in ["answer:", "my response is:", "my answer is:"]:
            if query_lower.startswith(prefix):
                is_answer = True
                user_answer = query[len(prefix):].strip()
                break

        if is_answer:
            question = "Explain the system architecture, framework stack, and database setup of this codebase."
            if history:
                for msg in reversed(history):
                    if msg.get("role") == "assistant" and msg.get("content"):
                        question = msg.get("content", "").strip()
                        break
            context = {"db": self.db, "project_path": project.path}
            try:
                raw_scorecard = self.review_agent.score_answer(context, question, user_answer)
                audited_scorecard = self.reflection_agent.validate_review_scorecard(context, raw_scorecard)
                score = audited_scorecard.get("score", 0)
                feedback = audited_scorecard.get("feedback", "")
                model_answer = audited_scorecard.get("model_answer", "")
                missing_keywords = audited_scorecard.get("missing_keywords", [])
                matched_keywords = audited_scorecard.get("matched_keywords", [])
                scorecard_md = (
                    f"### 📊 ASTA Technical Answer Evaluation\n"
                    f"**Overall Score**: `{score}/100`\n\n"
                    f"#### 🔍 Detailed Feedback:\n"
                    f"{feedback}\n\n"
                    f"#### ✅ Key Terms Mentioned:\n"
                    f"{', '.join(f'`{k}`' for k in matched_keywords) if matched_keywords else '*None*'}\n\n"
                    f"#### ⚠️ Key Gaps (Missing Keywords):\n"
                    f"{', '.join(f'`{k}`' for k in missing_keywords) if missing_keywords else '*None*'}\n\n"
                    f"#### 💡 Recommended Model Pitch:\n"
                    f"{model_answer}\n"
                )
            except Exception as e:
                scorecard_md = f"### ❌ Evaluation Error\nFailed to evaluate answer: {str(e)}"
            if self.memory_agent.is_important_technical_query(query):
                self.memory_agent.record_chat_message(project_id, "user", query)
                self.memory_agent.record_chat_message(project_id, "assistant", scorecard_md)
            return scorecard_md

        # 1. Fetch recent chat history context (use passed state if available, else SQLite fallback)
        if history is not None:
            history_context = self._format_conversation_history(history)
        else:
            history_context = self.memory_agent.get_conversation_context(project_id, limit=6)

        # 2. Retrieval Layer (Dynamic keyword & symbol lookup)
        symbols_context = self._retrieve_relevant_code_context(project_id, project.path, query)

        # 3. Project Intelligence Agent Layer
        response = self.project_agent.answer_user_query(
            project_name=project.name,
            framework=project.framework or "Python/FastAPI",
            database_type=project.database_type or "SQLite",
            symbols_context=symbols_context,
            user_query=query,
            chat_history=history_context
        )

        # 4. Generate codebase-specific follow-up mock questions using InterviewAgent
        context_data = {
            "project_name": project.name,
            "framework": project.framework or "Python/FastAPI",
            "database_type": project.database_type or "SQLite",
            "symbols": symbols_context
        }
        try:
            followups = self.interview_agent.generate_chat_followup_questions(context_data, response)
            response += f"\n\n{followups}"
        except Exception as e:
            logger.error(f"Failed to generate followups: {str(e)}")

        # Log to conversational memory if technical query
        if self.memory_agent.is_important_technical_query(query):
            self.memory_agent.record_chat_message(project_id, "user", query)
            self.memory_agent.record_chat_message(project_id, "assistant", response)
        
        return response

    def run_explain_stream_workflow(self, project_id: str, query: str, history: Optional[List[Dict[str, str]]] = None):
        """Streams project explanation tokens and records final output into SQLite chat memory."""
        logger.info(f"[WorkflowEngine] Starting Project Explanation Streaming Workflow for project: {project_id}")
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        # 0. Intercept answer submissions for ReviewAgent scoring
        query_lower = query.lower().strip()
        is_answer = False
        user_answer = query
        for prefix in ["answer:", "my response is:", "my answer is:"]:
            if query_lower.startswith(prefix):
                is_answer = True
                user_answer = query[len(prefix):].strip()
                break

        if is_answer:
            question = "Explain the system architecture, framework stack, and database setup of this codebase."
            if history:
                for msg in reversed(history):
                    if msg.get("role") == "assistant" and msg.get("content"):
                        question = msg.get("content", "").strip()
                        break
            context = {"db": self.db, "project_path": project.path}
            try:
                raw_scorecard = self.review_agent.score_answer(context, question, user_answer)
                audited_scorecard = self.reflection_agent.validate_review_scorecard(context, raw_scorecard)
                score = audited_scorecard.get("score", 0)
                feedback = audited_scorecard.get("feedback", "")
                model_answer = audited_scorecard.get("model_answer", "")
                missing_keywords = audited_scorecard.get("missing_keywords", [])
                matched_keywords = audited_scorecard.get("matched_keywords", [])
                scorecard_md = (
                    f"### 📊 ASTA Technical Answer Evaluation\n"
                    f"**Overall Score**: `{score}/100`\n\n"
                    f"#### 🔍 Detailed Feedback:\n"
                    f"{feedback}\n\n"
                    f"#### ✅ Key Terms Mentioned:\n"
                    f"{', '.join(f'`{k}`' for k in matched_keywords) if matched_keywords else '*None*'}\n\n"
                    f"#### ⚠️ Key Gaps (Missing Keywords):\n"
                    f"{', '.join(f'`{k}`' for k in missing_keywords) if missing_keywords else '*None*'}\n\n"
                    f"#### 💡 Recommended Model Pitch:\n"
                    f"{model_answer}\n"
                )
            except Exception as e:
                scorecard_md = f"### ❌ Evaluation Error\nFailed to evaluate answer: {str(e)}"
            
            chunk_size = 15
            for i in range(0, len(scorecard_md), chunk_size):
                yield scorecard_md[i:i+chunk_size]

            if self.memory_agent.is_important_technical_query(query):
                self.memory_agent.record_chat_message(project_id, "user", query)
                self.memory_agent.record_chat_message(project_id, "assistant", scorecard_md)
            return

        if history is not None:
            history_context = self._format_conversation_history(history)
        else:
            history_context = self.memory_agent.get_conversation_context(project_id, limit=6)
            
        symbols_context = self._retrieve_relevant_code_context(project_id, project.path, query)

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

        # Generate codebase-specific follow-up mock questions using InterviewAgent
        context_data = {
            "project_name": project.name,
            "framework": project.framework or "Python/FastAPI",
            "database_type": project.database_type or "SQLite",
            "symbols": symbols_context
        }
        complete_explanation = "".join(full_response_chunks)
        try:
            followups = self.interview_agent.generate_chat_followup_questions(context_data, complete_explanation)
            yield "\n\n"
            # Stream the follow-up questions chunk by chunk
            chunk_size = 15
            for i in range(0, len(followups), chunk_size):
                yield followups[i:i+chunk_size]
            complete_explanation += f"\n\n{followups}"
        except Exception as e:
            logger.error(f"Failed to generate followups: {str(e)}")

        # Record to memory upon completion if technical query
        if self.memory_agent.is_important_technical_query(query):
            self.memory_agent.record_chat_message(project_id, "user", query)
            self.memory_agent.record_chat_message(project_id, "assistant", complete_explanation)

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
