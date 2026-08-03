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
        mode: str = "project_explain",
        objective: str = "project_pitch"
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
                f"# INSTRUCTIONS:\n"
                f"- You are ASTA 👋, a friendly, calm, and natural Senior Staff Software Engineer mentoring a junior developer.\n"
                f"- The user is greeting you, waving, or initiating a casual conversation.\n"
                f"- Respond dynamically, naturally, and warmly to the user's greeting or wave. Do NOT repeat or copy the example response verbatim.\n"
                f"- If they are greeting you, introduce yourself as ASTA, their Engineering Intelligence Mentor, and explain what you do (help understand architecture, coaching, explaining decisions, etc.) naturally and conversationally.\n"
                f"- Do NOT immediately start explaining the codebase files.\n"
                f"- Do NOT produce interview sections.\n"
                f"- Do NOT generate follow-up questions.\n"
                f"- Do NOT mention indexing unless relevant.\n"
                f"- Keep the response professional, friendly, calm, and natural.\n"
                f"- Tone example: A warm, inviting, custom welcome showing ASTA's persona without copy-pasting standard canned scripts."
            )
        else:
            # Setup prompt instructions tailored by specific mode and objective
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
                f"# INSTRUCTIONS:\n"
                f"- You are ASTA, a friendly, calm, and natural Senior Staff Software Engineer mentoring a junior developer.\n"
                f"- Grounding: Only reference existing files, directories, notes, and modules present in the codebase context (e.g., from the Project Directory Structure or README). Do NOT invent database schemas, frameworks (like Django, FastAPI, React), code views, or architectures that are not explicitly present. If the project contains only text, markdown, or documentation files (like PR notes, combined data), explain those specific documents and their contents dynamically, explicitly stating that this is a notes/documentation folder rather than a running application codebase. If the context is insufficient, explicitly say so.\n"
                f"- Concise & To-The-Point: Keep your response precise, focused, and direct. Avoid excessively long-winded textbook explanations or general fillers. Summarize key aspects cleanly.\n"
                f"- No Script Dialogues: Do NOT format your explanation as a dialogue transcript (e.g., do NOT generate 'Interviewer:' and 'You:' script lines). Instead, explain the concepts and architecture directly to the user.\n"
                f"- Explain it as if you are teaching the user how THEY should explain it or understand it. Start your explanation naturally (e.g., 'In this workspace...' or 'If I were asked about this...').\n"
                f"- Do NOT write a rigid textbook response or documentation. Prefer conversational teaching.\n"
                f"- Teach better engineering communication and vocabulary naturally where applicable.\n"
                f"- Keep the response clean, conversational, and directly focused on the user's actual files. Do NOT append any '## 💡 Tech Interview Rationale' section or follow-up questions.\n\n"
                f"- Focus your mentoring specifically on the user's LEARNING OBJECTIVE: '{objective}'\n"
                f"  - If objective is 'concept_explain': Focus heavily on teaching the core concepts and definitions of the technical topic simply and clearly, ensuring the junior engineer understands the basic logic.\n"
                f"  - If objective is 'project_pitch': Focus heavily on how the user should explain the codebase implementation details in an interview setting using the indexed symbols tree.\n"
                f"  - If objective is 'design_critique': Focus heavily on critiquing design choices, system scalability limits, database connection limits, and technical trade-offs (e.g., PostgreSQL vs SQLite).\n"
                f"  - If objective is 'vocab_coaching': Focus heavily on articulation coaching, highlighting strong technical vocabulary, and explaining what signaling details an interviewer expects to hear."
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
        mode: str = "project_explain",
        objective: str = "project_pitch"
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
                f"# INSTRUCTIONS:\n"
                f"- You are ASTA 👋, a friendly, calm, and natural Senior Staff Software Engineer mentoring a junior developer.\n"
                f"- The user is greeting you, waving, or initiating a casual conversation.\n"
                f"- Respond dynamically, naturally, and warmly to the user's greeting or wave. Do NOT repeat or copy the example response verbatim.\n"
                f"- If they are greeting you, introduce yourself as ASTA, their Engineering Intelligence Mentor, and explain what you do (help understand architecture, coaching, explaining decisions, etc.) naturally and conversationally.\n"
                f"- Do NOT immediately start explaining the codebase files.\n"
                f"- Do NOT produce interview sections.\n"
                f"- Do NOT generate follow-up questions.\n"
                f"- Do NOT mention indexing unless relevant.\n"
                f"- Keep the response professional, friendly, calm, and natural.\n"
                f"- Tone example: A warm, inviting, custom welcome showing ASTA's persona without copy-pasting standard canned scripts."
            )
        else:
            # Setup prompt instructions tailored by specific mode and objective
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
                f"# INSTRUCTIONS:\n"
                f"- You are ASTA, a friendly, calm, and natural Senior Staff Software Engineer mentoring a junior developer.\n"
                f"- Grounding: Only reference existing files, directories, notes, and modules present in the codebase context (e.g., from the Project Directory Structure or README). Do NOT invent database schemas, frameworks (like Django, FastAPI, React), code views, or architectures that are not explicitly present. If the project contains only text, markdown, or documentation files (like PR notes, combined data), explain those specific documents and their contents dynamically, explicitly stating that this is a notes/documentation folder rather than a running application codebase. If the context is insufficient, explicitly say so.\n"
                f"- Concise & To-The-Point: Keep your response precise, focused, and direct. Avoid excessively long-winded textbook explanations or general fillers. Summarize key aspects cleanly.\n"
                f"- No Script Dialogues: Do NOT format your explanation as a dialogue transcript (e.g., do NOT generate 'Interviewer:' and 'You:' script lines). Instead, explain the concepts and architecture directly to the user.\n"
                f"- Explain it as if you are teaching the user how THEY should explain it or understand it. Start your explanation naturally (e.g., 'In this workspace...' or 'If I were asked about this...').\n"
                f"- Do NOT write a rigid textbook response or documentation. Prefer conversational teaching.\n"
                f"- Teach better engineering communication and vocabulary naturally where applicable.\n"
                f"- Keep the response clean, conversational, and directly focused on the user's actual files. Do NOT append any '## 💡 Tech Interview Rationale' section or follow-up questions.\n\n"
                f"- Focus your mentoring specifically on the user's LEARNING OBJECTIVE: '{objective}'\n"
                f"  - If objective is 'concept_explain': Focus heavily on teaching the core concepts and definitions of the technical topic simply and clearly, ensuring the junior engineer understands the basic logic.\n"
                f"  - If objective is 'project_pitch': Focus heavily on how the user should explain the codebase implementation details in an interview setting using the indexed symbols tree.\n"
                f"  - If objective is 'design_critique': Focus heavily on critiquing design choices, system scalability limits, database connection limits, and technical trade-offs (e.g., PostgreSQL vs SQLite).\n"
                f"  - If objective is 'vocab_coaching': Focus heavily on articulation coaching, highlighting strong technical vocabulary, and explaining what signaling details an interviewer expects to hear."
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
