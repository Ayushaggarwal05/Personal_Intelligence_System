from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class ProjectAgent(BaseAgent):
    """Project Intelligence Agent providing technical explanations and conversational responses optimized for passing engineering interviews."""
    def __init__(self):
        super().__init__(name="ProjectAgent", category="chat", prompt_file="system_prompt.txt")

    def answer_user_query(
        self,
        project_name: str,
        framework: str,
        database_type: str,
        symbols_context: str,
        user_query: str,
        chat_history: str = "",
        is_casual: bool = False,
        mode: str = "project_explain"
    ) -> str:
        """Generates dynamic, conversational, and query-focused answers incorporating codebase symbols and dialog history."""
        if is_casual and mode == "project_explain":
            mode = "casual"

        if mode == "casual":
            variables = {
                "project_context": (
                    f"Project Name: {project_name}\n"
                    f"Frameworks/Languages: {framework}\n"
                    f"Databases: {database_type}\n\n"
                    f"Recent Chat History:\n{chat_history or 'No previous messages.'}\n"
                )
            }
            prompt = (
                f"# CURRENT USER QUERY: '{user_query}'\n\n"
                "# INSTRUCTIONS:\n"
                "- You are ASTA, a friendly, calm, and natural Senior Staff Engineer mentoring a junior engineer.\n"
                "- The user is chatting with you casually (greetings, small talk, \"who are you\", \"how are you\", \"introduce yourself\").\n"
                "- Respond to the CURRENT USER QUERY directly and conversationally as a helpful, friendly mentor.\n"
                "- Introduce yourself as ASTA, the Engineering Intelligence Assistant.\n"
                "- Keep the response professional, friendly, calm, and natural.\n"
                "- Do NOT explain project architecture.\n"
                "- Do NOT produce interview questions.\n"
                "- Do NOT produce rationale sections.\n"
                "- Do NOT mention project indexing unless relevant.\n"
                "- Example tone: \"Hi! I'm ASTA, your Engineering Intelligence Assistant. I can help you understand your project architecture, prepare for interviews, explain design decisions and even conduct mock interviews. What would you like to work on today?\""
            )
        elif mode == "architecture_discuss":
            variables = {
                "project_context": (
                    f"Project Name: {project_name}\n"
                    f"Frameworks/Languages: {framework}\n"
                    f"Databases: {database_type}\n\n"
                    f"## Indexed Codebase Symbols:\n{symbols_context}\n\n"
                    f"## Recent Chat History:\n{chat_history or 'No previous messages.'}\n"
                )
            }
            prompt = (
                f"# CURRENT USER QUERY: '{user_query}'\n\n"
                "# INSTRUCTIONS:\n"
                "- You are ASTA, a professional, friendly, calm, and natural Senior Staff Engineer mentoring a junior engineer.\n"
                "- Answer like a Staff Engineer: discuss trade-offs, discuss scalability, discuss alternatives, and avoid generic textbook definitions.\n"
                "- Discuss system architecture patterns and decisions specific to the active project (described in PROJECT CONTEXT).\n"
                "- Frame the discussion as a collaborative engineering critique.\n"
                "- Keep the response clean and conversational. Do NOT append any '## 💡 Tech Interview Rationale' section or follow-up questions."
            )
        elif mode == "general_technical":
            variables = {
                "project_context": (
                    f"Project Name: {project_name}\n"
                    f"Frameworks/Languages: {framework}\n"
                    f"Databases: {database_type}\n\n"
                    f"Recent Chat History:\n{chat_history or 'No previous messages.'}\n"
                )
            }
            prompt = (
                f"# CURRENT USER QUERY: '{user_query}'\n\n"
                "# INSTRUCTIONS:\n"
                "- You are ASTA, a professional, friendly, calm, and natural Senior Staff Engineer mentoring a junior engineer.\n"
                "- Provide a professional explanation of the general technical concept in the CURRENT USER QUERY (e.g. JWT, REST, Docker).\n"
                "- If the concept is relevant to the active project (Frameworks: {framework}, Databases: {database_type}), connect the concept back to the current indexed project naturally. Otherwise, answer normally.\n"
                "- Avoid textbook definitions; explain it like a Senior Engineer.\n"
                "- Keep the response conversational. Do NOT append any '## 💡 Tech Interview Rationale' or follow-up questions."
            )
        else: # project_explain
            variables = {
                "project_context": (
                    f"Project Name: {project_name}\n"
                    f"Frameworks/Languages: {framework}\n"
                    f"Databases: {database_type}\n\n"
                    f"## Indexed Codebase Symbols:\n{symbols_context}\n\n"
                    f"## Recent Chat History:\n{chat_history or 'No previous messages.'}\n"
                )
            }
            prompt = (
                f"# CURRENT USER QUERY: '{user_query}'\n\n"
                "# INSTRUCTIONS:\n"
                "- You are ASTA, a professional, friendly, calm, and natural Senior Staff Engineer mentoring a junior engineer.\n"
                "- Answer ONLY the user's question using the PROJECT CONTEXT.\n"
                "- Frame your explanation in a senior-level technical interview style, teaching the user how to speak during interviews.\n"
                "- Grounding: Only use files, classes, routes, and symbols that exist in the indexed codebase context. Never invent filenames or assume implementations. If information is missing, clearly state that the indexed project does not contain enough information.\n"
                "- Explain WHY decisions were made.\n"
                "- Teach better engineering vocabulary naturally (e.g. instead of saying 'stores data', teach 'persists domain entities using the Django ORM'; instead of 'sends requests', teach 'exposes RESTful endpoints consumed by the React client'; instead of 'updates', teach 'leverages asynchronous API communication with optimistic UI updates').\n"
                "- Every explanation should contain these exactly structured parts, keeping it conversational rather than robotic:\n"
                "  1. Direct Explanation: Direct, senior-level response.\n"
                "  2. Interview-Ready Answer: Clear definition/pitch the user can use word-for-word in an interview.\n"
                "  3. Engineering Reasoning: Architectural logic behind this choice.\n"
                "  4. Architecture Trade-offs: Systems engineering trade-offs (e.g. SQLite vs PostgreSQL).\n"
                "  5. Interview Vocabulary: Teach and highlight specific vocabulary improvements used.\n"
                "- Do NOT append any follow-up questions or '## 💡 Tech Interview Rationale' section. Keep formatting clean."
            )
        
        return self.call_llm(prompt=prompt, system_variables=variables)

    def answer_user_query_stream(
        self,
        project_name: str,
        framework: str,
        database_type: str,
        symbols_context: str,
        user_query: str,
        chat_history: str = "",
        is_casual: bool = False,
        mode: str = "project_explain"
    ):
        """Yields token-by-token stream for conversational query responses."""
        if is_casual and mode == "project_explain":
            mode = "casual"

        if mode == "casual":
            variables = {
                "project_context": (
                    f"Project Name: {project_name}\n"
                    f"Frameworks/Languages: {framework}\n"
                    f"Databases: {database_type}\n\n"
                    f"Recent Chat History:\n{chat_history or 'No previous messages.'}\n"
                )
            }
            prompt = (
                f"# CURRENT USER QUERY: '{user_query}'\n\n"
                "# INSTRUCTIONS:\n"
                "- You are ASTA, a friendly, calm, and natural Senior Staff Engineer mentoring a junior engineer.\n"
                "- The user is chatting with you casually (greetings, small talk, \"who are you\", \"how are you\", \"introduce yourself\").\n"
                "- Respond to the CURRENT USER QUERY directly and conversationally as a helpful, friendly mentor.\n"
                "- Introduce yourself as ASTA, the Engineering Intelligence Assistant.\n"
                "- Keep the response professional, friendly, calm, and natural.\n"
                "- Do NOT explain project architecture.\n"
                "- Do NOT produce interview questions.\n"
                "- Do NOT produce rationale sections.\n"
                "- Do NOT mention project indexing unless relevant.\n"
                "- Example tone: \"Hi! I'm ASTA, your Engineering Intelligence Assistant. I can help you understand your project architecture, prepare for interviews, explain design decisions and even conduct mock interviews. What would you like to work on today?\""
            )
        elif mode == "architecture_discuss":
            variables = {
                "project_context": (
                    f"Project Name: {project_name}\n"
                    f"Frameworks/Languages: {framework}\n"
                    f"Databases: {database_type}\n\n"
                    f"## Indexed Codebase Symbols:\n{symbols_context}\n\n"
                    f"## Recent Chat History:\n{chat_history or 'No previous messages.'}\n"
                )
            }
            prompt = (
                f"# CURRENT USER QUERY: '{user_query}'\n\n"
                "# INSTRUCTIONS:\n"
                "- You are ASTA, a professional, friendly, calm, and natural Senior Staff Engineer mentoring a junior engineer.\n"
                "- Answer like a Staff Engineer: discuss trade-offs, discuss scalability, discuss alternatives, and avoid generic textbook definitions.\n"
                "- Discuss system architecture patterns and decisions specific to the active project (described in PROJECT CONTEXT).\n"
                "- Frame the discussion as a collaborative engineering critique.\n"
                "- Keep the response clean and conversational. Do NOT append any '## 💡 Tech Interview Rationale' section or follow-up questions."
            )
        elif mode == "general_technical":
            variables = {
                "project_context": (
                    f"Project Name: {project_name}\n"
                    f"Frameworks/Languages: {framework}\n"
                    f"Databases: {database_type}\n\n"
                    f"Recent Chat History:\n{chat_history or 'No previous messages.'}\n"
                )
            }
            prompt = (
                f"# CURRENT USER QUERY: '{user_query}'\n\n"
                "# INSTRUCTIONS:\n"
                "- You are ASTA, a professional, friendly, calm, and natural Senior Staff Engineer mentoring a junior engineer.\n"
                "- Provide a professional explanation of the general technical concept in the CURRENT USER QUERY (e.g. JWT, REST, Docker).\n"
                "- If the concept is relevant to the active project (Frameworks: {framework}, Databases: {database_type}), connect the concept back to the current indexed project naturally. Otherwise, answer normally.\n"
                "- Avoid textbook definitions; explain it like a Senior Engineer.\n"
                "- Keep the response conversational. Do NOT append any '## 💡 Tech Interview Rationale' or follow-up questions."
            )
        else: # project_explain
            variables = {
                "project_context": (
                    f"Project Name: {project_name}\n"
                    f"Frameworks/Languages: {framework}\n"
                    f"Databases: {database_type}\n\n"
                    f"## Indexed Codebase Symbols:\n{symbols_context}\n\n"
                    f"## Recent Chat History:\n{chat_history or 'No previous messages.'}\n"
                )
            }
            prompt = (
                f"# CURRENT USER QUERY: '{user_query}'\n\n"
                "# INSTRUCTIONS:\n"
                "- You are ASTA, a professional, friendly, calm, and natural Senior Staff Engineer mentoring a junior engineer.\n"
                "- Answer ONLY the user's question using the PROJECT CONTEXT.\n"
                "- Frame your explanation in a senior-level technical interview style, teaching the user how to speak during interviews.\n"
                "- Grounding: Only use files, classes, routes, and symbols that exist in the indexed codebase context. Never invent filenames or assume implementations. If information is missing, clearly state that the indexed project does not contain enough information.\n"
                "- Explain WHY decisions were made.\n"
                "- Teach better engineering vocabulary naturally (e.g. instead of saying 'stores data', teach 'persists domain entities using the Django ORM'; instead of 'sends requests', teach 'exposes RESTful endpoints consumed by the React client'; instead of 'updates', teach 'leverages asynchronous API communication with optimistic UI updates').\n"
                "- Every explanation should contain these exactly structured parts, keeping it conversational rather than robotic:\n"
                "  1. Direct Explanation: Direct, senior-level response.\n"
                "  2. Interview-Ready Answer: Clear definition/pitch the user can use word-for-word in an interview.\n"
                "  3. Engineering Reasoning: Architectural logic behind this choice.\n"
                "  4. Architecture Trade-offs: Systems engineering trade-offs (e.g. SQLite vs PostgreSQL).\n"
                "  5. Interview Vocabulary: Teach and highlight specific vocabulary improvements used.\n"
                "- Do NOT append any follow-up questions or '## 💡 Tech Interview Rationale' section. Keep formatting clean."
            )
        
        for token in self.call_llm_stream(prompt=prompt, system_variables=variables):
            yield token

    def explain_project(self, project_name: str, framework: str, database_type: str, symbols_context: str) -> str:
        """Backwards-compatible wrapper for full project explanation."""
        return self.answer_user_query(
            project_name=project_name,
            framework=framework,
            database_type=database_type,
            symbols_context=symbols_context,
            user_query="Provide a full high-level architecture overview and interview analysis for this project."
        )

    def compare_projects(self, project_a: Dict[str, Any], project_b: Dict[str, Any]) -> str:
        """Compares two codebase projects across architecture, tech stack, and design trade-offs."""
        variables = {
            "project_context": (
                f"Project A Name: {project_a['name']} | Framework: {project_a['framework']} | DB: {project_a['database']}\n"
                f"Project B Name: {project_b['name']} | Framework: {project_b['framework']} | DB: {project_b['database']}\n"
            )
        }
        
        prompt = (
            "Compare Project A and Project B from a systems engineering perspective:\n"
            "1. Architectural style differences\n"
            "2. Framework ecosystem advantages/disadvantages\n"
            "3. Engineering trade-offs and complexity differentials\n"
            "Provide an interview-ready summary comparing these two codebases."
        )
        
        return self.call_llm(prompt=prompt, system_variables=variables)
