from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class DiagramAgent(BaseAgent):
    """Diagram Agent that reasons over user diagram requests and compiles custom Mermaid.js markups."""
    def __init__(self):
        super().__init__(name="DiagramAgent", category="diagrams", prompt_file="generate_diagram.txt")

    def generate_diagram_markup(self, user_request: str, project_context: str) -> str:
        """Call LLM and requests customized Mermaid.js code strings based on architecture details."""
        variables = {
            "project_context": project_context
        }
        
        prompt = (
            "User Diagram Request: '{user_request}'\n\n"
            "Project Architectural Context:\n"
            "{project_context}\n\n"
            "Generate a Mermaid.js diagram representing this request.\n"
            "Respond ONLY with valid Mermaid syntax starting with e.g. 'graph TD', 'sequenceDiagram', or 'classDiagram'.\n"
            "Do NOT wrap output in markdown code blocks."
        )
        
        formatted_prompt = prompt.replace("{user_request}", user_request)
        
        try:
            markup = self.call_llm(
                prompt=formatted_prompt,
                system_variables=variables
            )
            # Remove any trailing code block formatting if returned
            clean_markup = markup.strip()
            if clean_markup.startswith("```"):
                lines = clean_markup.splitlines()
                if lines[0].startswith("```mermaid") or lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].endswith("```"):
                    lines = lines[:-1]
                clean_markup = "\n".join(lines).strip()
            return clean_markup
        except Exception:
            # Fallback ER placeholder
            return "graph TD; Client-->APIRouter;"
