import re
from typing import Dict, Any, List

class PlannerAgent:
    def __init__(self):
        pass

    def determine_plan(self, user_query: str) -> Dict[str, Any]:
        """Analyzes user query and decides which agents and workflows need to execute."""
        query = user_query.lower().strip()
        
        # 1. Interview Workflow Intent
        if any(keyword in query for keyword in ["interview", "mock", "coach", "prepare", "question"]):
            return {
                "intent": "interview",
                "steps": [
                    {"agent": "workspace_agent", "action": "scan_workspace"},
                    {"agent": "interview_agent", "action": "generate_question"}
                ],
                "description": "Start or continue a mock interview session."
            }
            
        # 2. Diagram / Visualization Intent
        if any(keyword in query for keyword in ["diagram", "chart", "mermaid", "visualize", "schema", "flowchart"]):
            return {
                "intent": "diagram",
                "steps": [
                    {"agent": "workspace_agent", "action": "scan_workspace"},
                    {"agent": "diagram_agent", "action": "generate_diagram"}
                ],
                "description": "Generate architectural or database diagrams."
            }

        # 3. Code search / retrieval Intent
        if any(keyword in query for keyword in ["find", "search", "where is", "locate", "lookup", "grep"]):
            return {
                "intent": "search",
                "steps": [
                    {"agent": "retrieval_agent", "action": "hybrid_search"}
                ],
                "description": "Perform keyword and vector search over codebase files."
            }

        # 4. Fallback: Generic Chat / Code explanation
        return {
            "intent": "chat",
            "steps": [
                {"agent": "retrieval_agent", "action": "retrieve_context"},
                {"agent": "chat_agent", "action": "explain"}
            ],
            "description": "Standard code retrieval and explanation chat."
        }

planner = PlannerAgent()
