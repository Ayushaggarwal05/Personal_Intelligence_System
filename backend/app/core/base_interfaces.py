from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

class BaseRepository(ABC):
    """Abstract Base Class defining standard operations for Database Repositories."""
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def list_all(self) -> List[Any]:
        pass

    @abstractmethod
    def create(self, entity: Any) -> Any:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        pass


class BaseService(ABC):
    """Abstract Base Class defining operations for Business Logic Services."""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass


class BaseTool(ABC):
    """Abstract Base Class defining operations for Filesystem & Code Analysis Tools."""
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        pass


class BaseAgentInterface(ABC):
    """Abstract Base Class defining operational structures for Swarm Agents."""
    
    @abstractmethod
    def call_llm(self, prompt: str, system_variables: Optional[Dict[str, Any]] = None, json_format: bool = False) -> str:
        pass
