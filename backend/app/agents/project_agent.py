from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class ProjectAgent(BaseAgent):
    """Project Intelligence Agent providing technical explanations optimized for passing engineering interviews."""
    def __init__(self):
        super().__init__(name="ProjectAgent", category="chat", prompt_file="system_prompt.txt")

    def explain_project(self, project_name: str, framework: str, database_type: str, symbols_context: str) -> str:
        """Generates structured interview-focused project explanations."""
        variables = {
            "project_context": (
                f"Project Name: {project_name}\n"
                f"Primary Framework: {framework}\n"
                f"Database Configuration: {database_type}\n"
                f"Indexed Symbols Details:\n{symbols_context}"
            )
        }
        
        prompt = (
            "Explain this project focusing on topics required for a senior engineering interview:\n"
            "1. High-Level Architecture Overview\n"
            "2. Database Schema and Relations\n"
            "3. Key REST API Endpoint routing lifecycles\n"
            "4. Technical Trade-offs made (e.g. SQLite vs. PostgreSQL, synchronous vs asynchronous)\n"
            "5. Hardest follow-up questions an interviewer might ask and how to answer them.\n"
            "Ensure the tone is professional, technical, and concrete."
        )
        
        return self.call_llm(prompt=prompt, system_variables=variables)

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
