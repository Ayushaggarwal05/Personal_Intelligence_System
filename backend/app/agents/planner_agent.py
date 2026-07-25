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

    def classify_mode(self, query: str) -> str:
        """Classifies the user query intent into one of the 5 ASTA interaction modes."""
        query_lower = query.lower().strip("?.,!\"' ")
        
        # 1. Fast heuristic checks for common greetings
        greetings = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "sup", "hi asta", "yo"}
        if query_lower in greetings:
            return "casual"
            
        # Fast heuristic checks for mock interview requests
        interview_keywords = {"interview me", "take my interview", "ask me questions", "mock interview", "start interview"}
        if any(kw in query_lower for kw in interview_keywords):
            return "mock_interview_start"
            
        # 2. LLM-based classification for high-accuracy
        prompt = (
            f"Analyze the following user query: '{query}'.\n"
            f"Classify the user intent into exactly one of these categories:\n"
            f"1. \"casual\" - Greetings, social talk, 'how are you', 'who are you', 'introduce yourself', or general small talk.\n"
            f"2. \"mock_interview_start\" - Requests to start or take a mock interview session (e.g. 'interview me', 'ask me questions').\n"
            f"3. \"architecture_discuss\" - High-level systems design discussion, framework choices ('Why Django?', 'Why SQLite?'), scaling, design trade-offs, or improvement suggestions.\n"
            f"4. \"project_explain\" - Explaining specific files, folder structures, modules, authentication flow, database schemas, or code implementation details of the project.\n"
            f"5. \"general_technical\" - Conceptual questions NOT specific to the current project codebase (e.g. 'What is JWT', 'What is REST', 'Explain Docker').\n\n"
            f"Respond strictly in JSON format matching this schema:\n"
            f"{{\n"
            f"  \"mode\": \"casual\" | \"mock_interview_start\" | \"architecture_discuss\" | \"project_explain\" | \"general_technical\"\n"
            f"}}"
        )
        try:
            res = self.call_llm_structured(prompt=prompt)
            mode = res.get("mode", "project_explain")
            if mode in {"casual", "mock_interview_start", "architecture_discuss", "project_explain", "general_technical"}:
                return mode
        except Exception:
            pass
            
        # 3. Robust heuristic fallback if LLM classification fails
        if any(kw in query_lower for kw in {"why django", "why react", "why sqlite", "scale", "impro", "alternative"}):
            return "architecture_discuss"
        elif any(kw in query_lower for kw in {"what is jwt", "what is rest", "explain docker", "explain jwt"}):
            return "general_technical"
        elif any(kw in query_lower for kw in {"explain", "how does", "route", "database", "auth", "login"}):
            return "project_explain"
            
        return "casual"

    def is_technical_query(self, query: str) -> bool:
        """Determines if the query is a technical codebase query or general conversational banter."""
        mode = self.classify_mode(query)
        return mode not in {"casual", "mock_interview_start"}
        
# Add a global import for logger since BaseAgent might depend on it implicitly
from app.core.logging import logger
