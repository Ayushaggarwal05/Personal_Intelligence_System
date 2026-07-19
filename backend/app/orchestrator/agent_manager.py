from sqlalchemy.orm import Session
from app.agents.planner_agent import PlannerAgent
from app.agents.project_agent import ProjectAgent
from app.agents.interview_agent import InterviewAgent
from app.agents.review_agent import ReviewAgent
from app.agents.reflection_agent import ReflectionAgent
from app.agents.memory_agent import MemoryAgent
from typing import Dict, Any

class AgentManager:
    """Central manager instantiating and caching active agent classes."""
    def __init__(self, db: Session):
        self.db = db
        self._agents: Dict[str, Any] = {
            "PlannerAgent": PlannerAgent(),
            "ProjectAgent": ProjectAgent(),
            "InterviewAgent": InterviewAgent(),
            "ReviewAgent": ReviewAgent(),
            "ReflectionAgent": ReflectionAgent(),
            "MemoryAgent": MemoryAgent(db)
        }

    def get_agent(self, name: str) -> Any:
        """Retrieves target agent class by name key."""
        return self._agents.get(name)
