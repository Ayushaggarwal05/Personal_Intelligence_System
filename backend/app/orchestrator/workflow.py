import json
import uuid
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
from app.tools.project.detect_dependencies import extract_dependencies, extract_dependencies_categorized
from app.utils.helpers import get_utc_now

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

        # Get categorized libraries list using dependencies tool
        frontend_deps = []
        backend_deps = []
        try:
            categorized_deps = extract_dependencies_categorized(project_path)
            frontend_deps = categorized_deps.get("frontend", [])
            backend_deps = categorized_deps.get("backend", [])
        except Exception:
            pass
        
        frontend_deps_str = ", ".join(frontend_deps) if frontend_deps else "None detected."
        backend_deps_str = ", ".join(backend_deps) if backend_deps else "None detected."

        # Generate a clean, visual directory tree of the workspace
        def build_visual_tree(files) -> str:
            structure = {}
            for path in files:
                parts = path.replace("\\", "/").split("/")
                if len(parts) == 1:
                    structure[parts[0]] = None
                else:
                    top_dir = parts[0]
                    if top_dir not in structure or not isinstance(structure[top_dir], dict):
                        structure[top_dir] = {}
                    if len(parts) == 2:
                        structure[top_dir][parts[1]] = None
                    else:
                        sub_dir = parts[1]
                        if sub_dir not in structure[top_dir]:
                            structure[top_dir][sub_dir] = []
                        if isinstance(structure[top_dir][sub_dir], list):
                            structure[top_dir][sub_dir].append(parts[-1])
            
            lines = []
            for top_dir, contents in sorted(structure.items()):
                if contents is None:
                    lines.append(f"├── {top_dir}")
                else:
                    lines.append(f"├── {top_dir}/")
                    sub_keys = sorted(contents.keys())
                    for i, sub in enumerate(sub_keys):
                        is_last_sub = (i == len(sub_keys) - 1)
                        sub_char = "└── " if is_last_sub else "├── "
                        sub_prefix = "    " if is_last_sub else "│   "
                        val = contents[sub]
                        if val is None:
                            lines.append(f"│   {sub_char}{sub}")
                        elif isinstance(val, list):
                            lines.append(f"│   {sub_char}{sub}/")
                            for j, file in enumerate(val[:3]):
                                is_last_file = (j == len(val[:3]) - 1 and len(val) <= 3)
                                file_char = "└── " if is_last_file else "├── "
                                lines.append(f"│   {sub_prefix}{file_char}{file}")
                            if len(val) > 3:
                                lines.append(f"│   {sub_prefix}└── ... (and {len(val) - 3} more files)")
            return "\n".join(lines)

        project_files_paths = [f.relative_path for f in all_project_files]
        files_tree_str = build_visual_tree(project_files_paths)
        
        # Search for a single README/overview file to read its contents
        overview_content = ""
        for f in all_project_files:
            name_lower = f.relative_path.lower()
            if "readme" in name_lower or "setup.md" in name_lower or "combinedata" in name_lower:
                try:
                    content = read_workspace_file_content(project_path, f.relative_path)
                    overview_content = f"### Project Overview File ({f.relative_path}):\n{content[:2000]}"
                    break
                except Exception:
                    pass

        context_parts = []
        if overview_content:
            context_parts.append(overview_content)
            
        context_parts.append(
            f"### Project Directory Structure (Indexed Files):\n{files_tree_str}"
        )

        context_parts.append(
            f"### Codebase Tech Stack & Library Segregation:\n"
            f"- **Frontend Stack Libraries (from package.json)**: {frontend_deps_str}\n"
            f"- **Backend Stack Libraries (from requirements.txt/go.mod/etc)**: {backend_deps_str}"
        )

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

        # 0. Fetch recent chat history context
        if history is not None:
            history_context = self._format_conversation_history(history)
        else:
            history_context = self.memory_agent.get_conversation_context(project_id, limit=6)

        # Extract top-level folder names dynamically from SQLite project files
        all_project_files = self.file_repo.list_by_project(project_id)
        project_folders = []
        for f in all_project_files:
            parts = f.relative_path.replace("\\", "/").split("/")
            if len(parts) > 1:
                project_folders.append(parts[0])
        project_folders = list(set(project_folders))

        # 1. Check query intent mode and learning objective
        intent_data = self.planner.classify_intent(query, project_folders=project_folders)
        mode = intent_data["mode"]
        objective = intent_data["objective"]
        is_casual = (mode == "casual")

        # 2. Retrieval Layer (Bypassed if casual)
        if is_casual:
            symbols_context = ""
        else:
            symbols_context = self._retrieve_relevant_code_context(project_id, project.path, query)

        # Determine framework and database strings, filtering out "Unknown" and "None" strings
        fw_str = project.framework if (project.framework and project.framework not in {"Unknown", "None"}) else "General Workspace (No specific framework detected)"
        db_str = project.database_type if (project.database_type and project.database_type != "None") else "None (No database detected)"

        # 3. Project Intelligence Agent Layer
        response = self.project_agent.answer_user_query(
            project_name=project.name,
            framework=fw_str,
            database_type=db_str,
            symbols_context=symbols_context,
            user_query=query,
            chat_history=history_context,
            is_casual=is_casual,
            mode=mode,
            objective=objective
        )

        # 4. Generate codebase-specific follow-up learning path questions (All technical modes)
        if not is_casual:
            context_data = {
                "project_name": project.name,
                "framework": fw_str,
                "database_type": db_str,
                "symbols": symbols_context
            }
            try:
                followups = self.interview_agent.generate_chat_followup_questions(context_data, response)
                response += f"\n\n{followups}"
            except Exception as e:
                logger.error(f"Failed to generate followups: {str(e)}")

        # Record to memory upon completion if technical or casual query
        if self.memory_agent.is_important_technical_query(query) or is_casual:
            self.memory_agent.record_chat_message(project_id, "user", query)
            self.memory_agent.record_chat_message(project_id, "assistant", response)

        return response

    def run_explain_stream_workflow(self, project_id: str, query: str, history: Optional[List[Dict[str, str]]] = None):
        """Streams project explanation tokens and records final output into SQLite chat memory."""
        logger.info(f"[WorkflowEngine] Starting Project Explanation Streaming Workflow for project: {project_id}")
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        # 0. Fetch recent chat history context
        if history is not None:
            history_context = self._format_conversation_history(history)
        else:
            history_context = self.memory_agent.get_conversation_context(project_id, limit=6)

        # 1. Check query intent mode and learning objective
        intent_data = self.planner.classify_intent(query)
        mode = intent_data["mode"]
        objective = intent_data["objective"]
        is_casual = (mode == "casual")

        # 2. Retrieval Layer (Bypassed if casual)
        if is_casual:
            symbols_context = ""
        else:
            symbols_context = self._retrieve_relevant_code_context(project_id, project.path, query)

        # Determine framework and database strings, filtering out "Unknown" and "None" strings
        fw_str = project.framework if (project.framework and project.framework not in {"Unknown", "None"}) else "General Workspace (No specific framework detected)"
        db_str = project.database_type if (project.database_type and project.database_type != "None") else "None (No database detected)"

        # 3. Project Intelligence Agent Layer
        full_response_chunks = []
        for token in self.project_agent.answer_user_query_stream(
            project_name=project.name,
            framework=fw_str,
            database_type=db_str,
            symbols_context=symbols_context,
            user_query=query,
            chat_history=history_context,
            is_casual=is_casual,
            mode=mode,
            objective=objective
        ):
            full_response_chunks.append(token)
            yield token

        complete_explanation = "".join(full_response_chunks)

        # 4. Generate codebase-specific follow-up learning path questions (All technical modes)
        if not is_casual:
            yield "[EXPLAIN_DONE]"
            context_data = {
                "project_name": project.name,
                "framework": fw_str,
                "database_type": db_str,
                "symbols": symbols_context
            }
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

        # Record to memory upon completion if technical or casual query
        if self.memory_agent.is_important_technical_query(query) or is_casual:
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
