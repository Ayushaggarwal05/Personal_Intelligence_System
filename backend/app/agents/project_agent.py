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
        chat_history: str = ""
    ) -> str:
        """Generates dynamic, conversational, and query-focused answers incorporating codebase symbols and dialog history."""
        variables = {
            "project_context": (
                f"Active Workspace Project: {project_name}\n"
                f"Framework: {framework} | Database: {database_type}\n"
                f"Indexed Codebase Structures:\n{symbols_context}\n"
                f"Recent Conversation History:\n{chat_history or 'No previous messages.'}\n"
            )
        }
        
        prompt = (
            f"User Prompt: '{user_query}'\n\n"
            "Instructions:\n"
            "1. Respond directly, naturally, and conversationally to the user's prompt.\n"
            "2. If the user is saying hello or asking a general question, greet them cordially and concisely offer help with their project.\n"
            "3. If the user asks a specific technical question, answer it directly using the project's codebase symbols and tech stack context, focusing on senior engineering interview standards.\n"
            "4. If the user asks for a complete architecture breakdown or full project summary, provide a structured 5-part overview (Architecture, Database Schema, API Routing, Technical Trade-offs, and Interview Questions).\n"
            "Maintain a helpful, articulate, and technical tone."
        )
        
        return self.call_llm(prompt=prompt, system_variables=variables)

    def answer_user_query_stream(
        self,
        project_name: str,
        framework: str,
        database_type: str,
        symbols_context: str,
        user_query: str,
        chat_history: str = ""
    ):
        """Yields token-by-token stream for conversational query responses."""
        variables = {
            "project_context": (
                f"Active Workspace Project: {project_name}\n"
                f"Framework: {framework} | Database: {database_type}\n"
                f"Indexed Codebase Structures:\n{symbols_context}\n"
                f"Recent Conversation History:\n{chat_history or 'No previous messages.'}\n"
            )
        }
        
        prompt = (
            f"User Prompt: '{user_query}'\n\n"
            "Instructions:\n"
            "1. Respond directly, naturally, and conversationally to the user's prompt.\n"
            "2. If the user is saying hello or asking a general question, greet them cordially and concisely offer help with their project.\n"
            "3. If the user asks a specific technical question, answer it directly using the project's codebase symbols and tech stack context, focusing on senior engineering interview standards.\n"
            "4. If the user asks for a complete architecture breakdown or full project summary, provide a structured 5-part overview (Architecture, Database Schema, API Routing, Technical Trade-offs, and Interview Questions).\n"
            "Maintain a helpful, articulate, and technical tone."
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
