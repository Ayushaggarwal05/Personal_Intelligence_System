import json
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.exceptions import PEISException, ProjectNotFoundException
from app.database.repositories.project_repository import ProjectRepository
from app.database.repositories.file_repository import FileRepository
from app.database.repositories.symbol_repository import SymbolRepository
from app.agents.project_agent import ProjectAgent
from app.agents.interview_agent import InterviewAgent
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
        
        # Instantiate Agents
        self.project_agent = ProjectAgent()
        self.interview_agent = InterviewAgent()
        self.memory_agent = MemoryAgent(db)

    def _classify_intent(self, query: str, project_folders: Optional[List[str]] = None) -> Dict[str, str]:
        """Classifies the user query intent (mode) and the learning objective."""
        query_lower = query.lower().strip("?.,!\"' ")
        
        # 1. Fast heuristic checks for common greetings
        greetings = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "sup", "hi asta", "yo", "wave"}
        if query_lower in greetings or any(query_lower.startswith(g) for g in ["who are you", "how are you", "introduce yourself"]):
            return {"mode": "casual", "objective": "concept_explain"}

        # Heuristics-First keyword pass
        explore_kws = {"folder", "directory", "directories", "files in", "structure of", "whats in", "what's in", "show me files", "where is", "how to find", "find file", "find class", "find route", "locate"}
        specific_dirs = {"backend", "frontend", "app", "src", "docs", "prompts", "tests", "components", "pages", "services"}
        if project_folders:
            specific_dirs = specific_dirs | {f.lower() for f in project_folders}
            
        if any(kw in query_lower for kw in explore_kws):
            if any(d in query_lower for d in specific_dirs) and "structure" not in query_lower and "tree" not in query_lower:
                return {"mode": "project_explain", "objective": "project_pitch"}
            return {"mode": "codebase_explore", "objective": "project_pitch"}

        # Architecture discussion
        arch_kws = {"why react", "why django", "why sqlite", "why fastapi", "trade-off", "tradeoff", "scalability", "alternatives", "design critique", "scale"}
        if any(kw in query_lower for kw in arch_kws):
            return {"mode": "architecture_discuss", "objective": "design_critique"}

        # Conceptual general technical
        tech_kws = {"what is jwt", "what is oauth", "what is rest", "what is clean architecture", "concept of", "definition of", "explain docker"}
        if any(kw in query_lower for kw in tech_kws):
            return {"mode": "general_technical", "objective": "concept_explain"}

        # Learning guidance
        guidance_kws = {"study plan", "learning path", "how to prepare", "prepare for", "career advice", "guide me", "mock interview"}
        if any(kw in query_lower for kw in guidance_kws):
            return {"mode": "learning_guidance", "objective": "concept_explain"}

        # Explicit project explanation
        explain_kws = {"explain how", "route logic", "database schema", "model design", "login flow", "auth logic"}
        if any(kw in query_lower for kw in explain_kws):
            return {"mode": "project_explain", "objective": "project_pitch"}
            
        # 2. Direct ModelRouter classification fallback
        from app.orchestrator.model_router import ModelRouter
        router = ModelRouter()
        prompt = (
            f"Analyze the following user query: '{query}'.\n"
            f"Classify the user intent and learning objective into exactly one category for each:\n\n"
            f"MODE CATEGORIES:\n"
            f"- \"casual\": Greetings, social talk, introductions, general banter.\n"
            f"- \"project_explain\": Explaining codebase concepts, files, structures, modules, auth logic, or databases.\n"
            f"- \"architecture_discuss\": Systems design critique, framework choice rationale, scaling limits, design trade-offs.\n"
            f"- \"general_technical\": Conceptual questions NOT specific to the current codebase (e.g. 'What is JWT', 'What is REST').\n"
            f"- \"codebase_explore\": Navigating, finding file locations, pathways, or relationships between symbols.\n"
            f"- \"learning_guidance\": Study plans, career tips, general study/preparation guidance.\n\n"
            f"OBJECTIVE CATEGORIES:\n"
            f"- \"concept_explain\": User wants to learn the general concept or definition of a technical topic.\n"
            f"- \"project_pitch\": User wants to know how to explain their project's codebase implementation in an interview setting.\n"
            f"- \"design_critique\": User wants to critique design choices, analyze scaling/locking limitations, database connection pooling, or trade-offs.\n"
            f"- \"vocab_coaching\": User wants to coach articulation, improve technical phrasing, learn vocabulary signaling, or find out what an interviewer expects to hear.\n\n"
            f"Respond strictly in JSON format matching this schema:\n"
            f"{{\n"
            f"  \"mode\": \"casual\" | \"project_explain\" | \"architecture_discuss\" | \"general_technical\" | \"codebase_explore\" | \"learning_guidance\",\n"
            f"  \"objective\": \"concept_explain\" | \"project_pitch\" | \"design_critique\" | \"vocab_coaching\"\n"
            f"}}"
        )
        try:
            raw_res = router.generate(prompt=prompt, system_prompt="You are a query classification helper.", json_format=True)
            clean_res = raw_res.strip()
            if clean_res.startswith("```json"):
                clean_res = clean_res[7:]
            if clean_res.endswith("```"):
                clean_res = clean_res[:-3]
            res = json.loads(clean_res.strip())
            mode = res.get("mode", "project_explain")
            objective = res.get("objective", "project_pitch")
            if mode in {"casual", "project_explain", "architecture_discuss", "general_technical", "codebase_explore", "learning_guidance"} and \
               objective in {"concept_explain", "project_pitch", "design_critique", "vocab_coaching"}:
                return {"mode": mode, "objective": objective}
        except Exception:
            pass
            
        # 3. Fallback
        return {"mode": "project_explain", "objective": "project_pitch"}

    def _build_visual_tree(self, files: List[str]) -> str:
        """Generates a clean, recursive visual directory tree of the workspace."""
        tree = {}
        for path in files:
            parts = path.replace("\\", "/").split("/")
            current = tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]

        def render_node(node, prefix="") -> List[str]:
            output_lines = []
            dirs = []
            files_list = []
            for name, child in sorted(node.items()):
                if not child:
                    files_list.append(name)
                else:
                    dirs.append((name, child))
            
            # Always render directories first to show folders clearly
            for idx, (d_name, d_child) in enumerate(dirs):
                is_last_dir = (idx == len(dirs) - 1 and len(files_list) == 0)
                connector = "└── " if is_last_dir else "├── "
                child_prefix = "    " if is_last_dir else "│   "
                output_lines.append(f"{prefix}{connector}{d_name}/")
                output_lines.extend(render_node(d_child, prefix + child_prefix))

            # Render files up to a limit (max 4 files) to prevent long trees
            file_limit = 4
            visible_files = files_list[:file_limit]
            remaining_files = len(files_list) - file_limit

            for idx, f_name in enumerate(visible_files):
                is_last_file = (idx == len(visible_files) - 1 and remaining_files <= 0)
                connector = "└── " if is_last_file else "├── "
                output_lines.append(f"{prefix}{connector}{f_name}")

            if remaining_files > 0:
                output_lines.append(f"{prefix}└── ... (and {remaining_files} more files)")

            return output_lines

        return "\n".join(render_node(tree))

    def _retrieve_relevant_code_context(self, project_id: str, project_path: str, query: str, mode: str) -> str:
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
            f"- [{s.type.upper()}] {s.name} (defined in {s.file.relative_path.replace('\\\\', '/').replace('\\', '/')}): {s.signature or ''}"
            if s.file else f"- [{s.type.upper()}] {s.name}: {s.signature or ''}"
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

        files_tree_str = ""
        if mode == "codebase_explore":
            project_files_paths = [f.relative_path for f in all_project_files]
            files_tree_str = self._build_visual_tree(project_files_paths)

        # Build index mapping base filenames to their relative path for targeted RAG-on-Demand
        existing_filenames = {}
        for f in all_project_files:
            base = f.relative_path.replace("\\", "/").split("/")[-1]
            existing_filenames[base.lower()] = f.relative_path
            # Also map base name without extension
            if "." in base:
                existing_filenames[base.split(".")[0].lower()] = f.relative_path

        # Find target files in user query words
        words_clean = [w.strip("?.,!\"'()[]{}").lower() for w in query.split()]
        
        # Build the dynamic files_by_parent mapping dictionary in RAM
        files_by_parent = {}
        for f in all_project_files:
            normalized = f.relative_path.replace("\\", "/").strip("/")
            parts = normalized.split("/")
            for i in range(len(parts)):
                parent = "/".join(parts[:i])
                child = parts[i]
                if parent not in files_by_parent:
                    files_by_parent[parent] = set()
                if i == len(parts) - 1:
                    files_by_parent[parent].add(f"📄 {child}")
                else:
                    files_by_parent[parent].add(f"📂 {child}/")

        files_by_parent_lower = {k.lower(): v for k, v in files_by_parent.items()}

        # Check if query keywords match any folder paths in the project
        queried_folders_files = {}
        for folder_path in files_by_parent.keys():
            if not folder_path:
                continue
            folder_name = folder_path.split("/")[-1].lower()
            if folder_name in words_clean:
                # Retrieve only the immediate children of this folder
                children = sorted(list(files_by_parent_lower.get(folder_path.lower(), set())))
                
                # Filter folders and files to apply the 3-file maximum limit
                folders = [c for c in children if c.startswith("📂")]
                files = [c for c in children if c.startswith("📄")]
                max_files_limit = 3
                if len(files) > max_files_limit:
                    files = files[:max_files_limit] + [f"... [+{len(files) - max_files_limit} more files]"]
                
                queried_folders_files[folder_path] = folders + files

        target_file_contents = []
        for w in words_clean:
            if w in existing_filenames:
                rel_path = existing_filenames[w]
                try:
                    content = read_workspace_file_content(project_path, rel_path)
                    limit_char = 4000
                    snippet = content[:limit_char] + ("\n... [truncated]" if len(content) > limit_char else "")
                    target_file_contents.append(f"--- File Code Content: {rel_path} ---\n{snippet}")
                except Exception as e:
                    logger.warning(f"Failed to read target file {rel_path}: {e}")
        
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

        # 1. Always append Project Root structure cleanly separated
        root_items = sorted(list(files_by_parent.get("", set())))
        root_folders = [item for item in root_items if item.startswith("📂")]
        root_files = [item for item in root_items if item.startswith("📄")]

        # Apply 3-file maximum limit to root files
        max_root_files_limit = 3
        if len(root_files) > max_root_files_limit:
            root_files = root_files[:max_root_files_limit] + [f"... [+{len(root_files) - max_root_files_limit} more files]"]

        root_context = []
        if root_folders:
            root_context.append("### Project Root Folders (Directories directly at the workspace root):\n" + "\n".join(root_folders))
        if root_files:
            root_context.append("### Project Root Files (Configuration/Data files directly at the workspace root):\n" + "\n".join(root_files))
        
        if root_context:
            context_parts.append("\n\n".join(root_context))

        # 2. Append specific queried folders' contents (if any folder matched the user query)
        if queried_folders_files:
            folder_info_parts = []
            for folder_path, children in queried_folders_files.items():
                children_list_str = "\n".join(children)
                folder_info_parts.append(
                    f"### Files & subdirectories directly inside the queried folder '{folder_path}/':\n"
                    f"{children_list_str}\n\n"
                    f"[RAG BOUNDARY NOTE: The contents of any nested subdirectories listed above (folders marked with 📂) are HIDDEN from your current view. Do NOT assume, invent, or guess any file names inside those folders. Only explain their conceptual roles based on the folder name. If the user wants to explore their files, advise them to ask about that specific folder directly.]"
                )
            context_parts.append("\n\n".join(folder_info_parts))
            
        if mode == "codebase_explore":
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
            
        if target_file_contents:
            context_parts.append("### Targeted File Contents (High Priority for explanation):\n" + "\n\n".join(target_file_contents))

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

        # Extract all folder and subfolder names dynamically from SQLite project files
        all_project_files = self.file_repo.list_by_project(project_id)
        project_folders = []
        for f in all_project_files:
            parts = f.relative_path.replace("\\", "/").split("/")
            for p in parts[:-1]:
                project_folders.append(p)
        project_folders = list(set(project_folders))

        # 1. Check query intent mode and learning objective
        intent_data = self._classify_intent(query, project_folders=project_folders)
        mode = intent_data["mode"]
        objective = intent_data["objective"]
        is_casual = (mode == "casual")

        # 2. Retrieval Layer (Bypassed if casual)
        if is_casual:
            symbols_context = ""
        else:
            symbols_context = self._retrieve_relevant_code_context(project_id, project.path, query, mode)

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

        if mode == "codebase_explore":
            files_tree_str = self._build_visual_tree([f.relative_path for f in all_project_files])
            tree_prefix = (
                f"### 📂 Project Directory Structure:\n"
                f"```plaintext\n"
                f"{files_tree_str}\n"
                f"```\n\n"
                f"──────────══════════──────────\n\n"
            )
            response = tree_prefix + response

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

        # Extract all folder and subfolder names dynamically from SQLite project files
        all_project_files = self.file_repo.list_by_project(project_id)
        project_folders = []
        for f in all_project_files:
            parts = f.relative_path.replace("\\", "/").split("/")
            for p in parts[:-1]:
                project_folders.append(p)
        project_folders = list(set(project_folders))

        # 1. Check query intent mode and learning objective
        intent_data = self._classify_intent(query, project_folders=project_folders)
        mode = intent_data["mode"]
        objective = intent_data["objective"]
        is_casual = (mode == "casual")

        # 2. Retrieval Layer (Bypassed if casual)
        if is_casual:
            symbols_context = ""
        else:
            symbols_context = self._retrieve_relevant_code_context(project_id, project.path, query, mode)

        # Determine framework and database strings, filtering out "Unknown" and "None" strings
        fw_str = project.framework if (project.framework and project.framework not in {"Unknown", "None"}) else "General Workspace (No specific framework detected)"
        db_str = project.database_type if (project.database_type and project.database_type != "None") else "None (No database detected)"

        # 3. Project Intelligence Agent Layer
        full_response_chunks = []

        if mode == "codebase_explore":
            files_tree_str = self._build_visual_tree([f.relative_path for f in all_project_files])
            tree_prefix = (
                f"### 📂 Project Directory Structure:\n"
                f"```plaintext\n"
                f"{files_tree_str}\n"
                f"```\n\n"
                f"──────────══════════──────────\n\n"
            )
            full_response_chunks.append(tree_prefix)
            yield tree_prefix
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
