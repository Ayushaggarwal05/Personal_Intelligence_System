import json
from app.agents.base_agent import BaseAgent
from app.database.models.project import Project
from app.database.models.file import File
from app.database.models.symbol import Symbol
from app.core.logging import logger
from app.core.exceptions import PEISException

class ReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ReviewAgent", category="interview", prompt_file="score_answer.txt")

    def score_answer(self, context: dict, question: str, user_answer: str) -> dict:
        """Scores a user's answer and evaluates keyword gaps against codebase schemas."""
        db = context["db"]
        project_path = context["project_path"]

        project = db.query(Project).filter(Project.path == project_path).first()
        if not project:
            raise PEISException(f"Project not found at path '{project_path}'", status_code=404)

        # 1. Fetch symbols context
        db_symbols = db.query(Symbol).join(File).filter(File.project_id == project.id).limit(15).all()
        symbols_summary = ""
        if db_symbols:
            symbols_summary = "\n".join([
                f"- [{s.type.upper()}] Name: {s.name} | Signature: {s.signature}" 
                for s in db_symbols
            ])

        # 2. Setup Variables
        variables = {
            "framework": project.framework or "Python/FastAPI",
            "database_type": project.database_type or "SQLite",
            "symbols": symbols_summary,
            "question": question,
            "user_answer": user_answer
        }

        logger.info(f"[ReviewAgent] Scoring answer for question: '{question[:40]}...'")
        
        try:
            # Call LLM router requesting JSON output
            raw_response = self.call_llm(
                prompt="Evaluate user's mock answer now.",
                system_variables=variables,
                json_format=True
            )
            logger.info(f"[ReviewAgent] Raw LLM Response: {raw_response}")
            
            # Clean string
            cleaned_res = raw_response.strip()
            if cleaned_res.startswith("```"):
                cleaned_res = cleaned_res.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                if cleaned_res.startswith("json"):
                    cleaned_res = cleaned_res[4:].strip()
                    
            score_data = json.loads(cleaned_res)
            return score_data
        except Exception as e:
            logger.error(f"[ReviewAgent] Failed to parse evaluation JSON: {e}. Booting fallback review.")
            
            # Simple heuristic keyword matcher to compile fallback scoring
            missing = []
            answer_lower = user_answer.lower() if user_answer else ""
            
            # Key checks
            concepts = {
                "connection pooling": ["pool", "connection pool", "engine"],
                "jwt rotation": ["jwt", "token", "payload"],
                "caching": ["cache", "redis", "memoize"],
                "middleware": ["middleware", "cors", "exception handler"],
                "rate limiting": ["rate limit", "throttle", "slowdown"],
                "async processing": ["async", "await", "coroutine", "celery", "task"]
            }
            for term, triggers in concepts.items():
                if not any(trigger in answer_lower for trigger in triggers):
                    missing.append(term)
            
            # Basic score based on word length and keyword matching
            word_count = len(user_answer.split()) if user_answer else 0
            base_score = 50
            if word_count > 20: base_score += 15
            if word_count > 50: base_score += 15
            base_score -= len(missing) * 5
            base_score = max(30, min(95, base_score))
            
            return {
                "score": base_score,
                "missing_keywords": missing[:3],
                "model_answer": f"A model answer for a senior engineer should explain the workflow of {project.framework or 'FastAPI'} routes and how database models link to sessions. Explain variables lifecycle clearly.",
                "suggestions": "Try writing a longer response describing design decisions and list exact technical patterns."
            }
object_review_agent = ReviewAgent()
