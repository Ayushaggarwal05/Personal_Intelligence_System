from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List, Optional

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

    def classify_intent(self, query: str, project_folders: Optional[List[str]] = None) -> Dict[str, str]:
        """Classifies the user query intent (mode) and the learning objective in a single call."""
        query_lower = query.lower().strip("?.,!\"' ")
        
        # 1. Fast heuristic checks for common greetings
        greetings = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "sup", "hi asta", "yo", "wave"}
        if query_lower in greetings or any(query_lower.startswith(g) for g in ["who are you", "how are you", "introduce yourself"]):
            return {"mode": "casual", "objective": "concept_explain"}

        # 1b. High-performance deterministic keyword pass (Approach 1: Heuristics-First)
        # Check codebase exploration queries
        explore_kws = {"folder", "directory", "directories", "files in", "structure of", "whats in", "what's in", "show me files", "where is", "how to find", "find file", "find class", "find route", "locate"}
        specific_dirs = {"backend", "frontend", "app", "src", "docs", "prompts", "tests", "components", "pages", "services"}
        if project_folders:
            specific_dirs = specific_dirs | {f.lower() for f in project_folders}
            
        if any(kw in query_lower for kw in explore_kws):
            # If they ask about a specific directory specifically, treat it as project explanation
            if any(d in query_lower for d in specific_dirs) and "structure" not in query_lower and "tree" not in query_lower:
                return {"mode": "project_explain", "objective": "project_pitch"}
            return {"mode": "codebase_explore", "objective": "project_pitch"}

        # Check architecture discussion queries
        arch_kws = {"why react", "why django", "why sqlite", "why fastapi", "trade-off", "tradeoff", "scalability", "alternatives", "design critique", "scale"}
        if any(kw in query_lower for kw in arch_kws):
            return {"mode": "architecture_discuss", "objective": "design_critique"}

        # Check conceptual general technical queries
        tech_kws = {"what is jwt", "what is oauth", "what is rest", "what is clean architecture", "concept of", "definition of", "explain docker"}
        if any(kw in query_lower for kw in tech_kws):
            return {"mode": "general_technical", "objective": "concept_explain"}

        # Check learning guidance queries
        guidance_kws = {"study plan", "learning path", "how to prepare", "prepare for", "career advice", "guide me", "mock interview"}
        if any(kw in query_lower for kw in guidance_kws):
            return {"mode": "learning_guidance", "objective": "concept_explain"}

        # Check explicit project explanation queries
        explain_kws = {"explain how", "route logic", "database schema", "model design", "login flow", "auth logic"}
        if any(kw in query_lower for kw in explain_kws):
            return {"mode": "project_explain", "objective": "project_pitch"}
            
        # 2. LLM-based classification for high-accuracy
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
            res = self.call_llm_structured(prompt=prompt)
            mode = res.get("mode", "project_explain")
            objective = res.get("objective", "project_pitch")
            if mode in {"casual", "project_explain", "architecture_discuss", "general_technical", "codebase_explore", "learning_guidance"} and \
               objective in {"concept_explain", "project_pitch", "design_critique", "vocab_coaching"}:
                return {"mode": mode, "objective": objective}
        except Exception:
            pass
            
        # 3. Robust heuristic fallback if LLM classification fails
        # Detect mode
        mode = "project_explain"
        if any(kw in query_lower for kw in {"why django", "why react", "why sqlite", "scale", "impro", "alternative", "trade-off", "tradeoff"}):
            mode = "architecture_discuss"
        elif any(kw in query_lower for kw in {"what is jwt", "what is rest", "explain docker", "explain jwt", "concept"}):
            mode = "general_technical"
        elif any(kw in query_lower for kw in {"how is", "where is", "file", "class", "symbol", "find", "explore"}):
            mode = "codebase_explore"
        elif any(kw in query_lower for kw in {"study", "plan", "guide", "learn", "how to answer", "prepare"}):
            mode = "learning_guidance"
        elif any(kw in query_lower for kw in {"explain", "how does", "route", "database", "auth", "login", "schema"}):
            mode = "project_explain"
        else:
            mode = "casual"

        # Detect objective
        objective = "project_pitch"
        if any(kw in query_lower for kw in {"explain jwt", "explain rest", "what is", "concept of", "definition of"}):
            objective = "concept_explain"
        elif any(kw in query_lower for kw in {"why did", "why do", "trade-off", "tradeoff", "critique", "scaling", "limitation", "bottleneck", "alternatives"}):
            objective = "design_critique"
        elif any(kw in query_lower for kw in {"interviewer expect", "say here", "vocabulary", "signal", "coaching", "articulation", "word", "phrasing"}):
            objective = "vocab_coaching"

        return {"mode": mode, "objective": objective}

    def classify_mode(self, query: str) -> str:
        """Classifies the user query intent into one of the ASTA conversational styles."""
        return self.classify_intent(query)["mode"]

    def is_technical_query(self, query: str) -> bool:
        """Determines if the query is a technical codebase query or general conversational banter."""
        mode = self.classify_mode(query)
        return mode != "casual"
        
# Add a global import for logger since BaseAgent might depend on it implicitly
from app.core.logging import logger
