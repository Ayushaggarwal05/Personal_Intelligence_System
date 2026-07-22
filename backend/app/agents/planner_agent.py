from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class PlannerAgent(BaseAgent):
    """Planner Agent orchestrating multi-agent tool execution steps based on user query intent."""
    def __init__(self):
        super().__init__(name="PlannerAgent", category="planner", prompt_file="plan.txt")

    def heuristic_classify_intent(self, user_intent: str) -> str:
        """Heuristically classifies user intent based on keywords."""
        query_lower = user_intent.lower()
        if "compare" in query_lower:
            return "compare"
        elif "interview" in query_lower or "mock" in query_lower:
            return "interview_start"
        elif "score" in query_lower or "grade" in query_lower or "submit" in query_lower:
            return "interview_review"
        elif "explain" in query_lower or "architecture" in query_lower:
            return "explain"
        else:
            return "chat"

    def plan_execution(self, user_intent: str) -> Dict[str, Any]:
        """Parses user intent and returns a structured plan list of tool/agent steps."""
        variables = {
            "user_intent": user_intent
        }
        
        prompt = (
            "Analyze the following user query: '{user_intent}'.\n"
            "Respond strictly in JSON format matching this schema:\n"
            "{\n"
            "  \"intent\": \"explain\" | \"interview_start\" | \"interview_review\" | \"compare\" | \"chat\",\n"
            "  \"steps\": [\n"
            "    {\n"
            "      \"step\": 1,\n"
            "      \"agent\": \"RetrievalAgent\" | \"ProjectAgent\" | \"InterviewAgent\" | \"ReviewAgent\",\n"
            "      \"action\": \"hybrid_search\" | \"explain_project\" | \"generate_question\" | \"score_answer\",\n"
            "      \"args\": {}\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        
        # Safely insert query string without trigger template variable key errors
        formatted_prompt = prompt.replace("{user_intent}", user_intent)
        
        try:
            plan_data = self.call_llm_structured(
                prompt=formatted_prompt,
                system_variables=variables
            )
            
            # Simple fallback validation if parsing failed/yielded empty dict
            if not plan_data or "intent" not in plan_data:
                intent = self.heuristic_classify_intent(user_intent)
                plan_data = {
                    "intent": intent,
                    "steps": [
                        {"step": 1, "agent": "RetrievalAgent", "action": "hybrid_search", "args": {}},
                        {"step": 2, "agent": "ProjectAgent", "action": "explain_project", "args": {}}
                    ]
                }
                
            return plan_data
        except Exception:
            intent = self.heuristic_classify_intent(user_intent)
            return {
                "intent": intent,
                "steps": [
                    {"step": 1, "agent": "RetrievalAgent", "action": "hybrid_search", "args": {}},
                    {"step": 2, "agent": "ProjectAgent", "action": "explain_project", "args": {}}
                ]
            }

    def is_technical_query(self, query: str) -> bool:
        """Determines if the query is a technical codebase query or general conversational banter."""
        greetings = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "sup", "hi asta"}
        cleaned = query.lower().strip("?.,!\"' ")
        if cleaned in greetings:
            return False

        prompt = (
            f"Analyze the following user message: '{query}'.\n"
            f"Determine if the user is asking a technical query about a codebase (e.g. explaining a file, architecture, frameworks, database setup, or coding patterns) or just chatting casually/asking general questions (e.g. 'what are you doing', 'how are you', 'tell me a joke', 'who are you', general chat).\n\n"
            f"Respond strictly in JSON format matching this schema:\n"
            f"{{\n"
            f"  \"is_technical\": true or false\n"
            f"}}"
        )
        try:
            res = self.call_llm_structured(prompt=prompt)
            return res.get("is_technical", True)
        except Exception:
            intent = self.heuristic_classify_intent(query)
            return intent != "chat"
        
# Add a global import for logger since BaseAgent might depend on it implicitly
from app.core.logging import logger
