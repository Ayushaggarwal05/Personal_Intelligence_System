from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from app.core.base_interfaces import BaseRepository

T = TypeVar("T")

class SQLiteRepository(BaseRepository, Generic[T]):
    """Generic SQLite Repository implementing standard CRUD database logic."""
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, entity_id: str) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def list_all(self) -> List[T]:
        return self.db.query(self.model).all()

    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: str) -> bool:
        entity = self.get_by_id(entity_id)
        if entity:
            self.db.delete(entity)
            self.db.commit()
            return True
        return False
