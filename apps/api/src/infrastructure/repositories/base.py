from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict
import uuid

T = TypeVar("T")

class BaseRepository(Generic[T], ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        pass

    @abstractmethod
    async def list(self, **filters) -> List[T]:
        pass

    @abstractmethod
    async def create(self, data: T) -> T:
        pass

    @abstractmethod
    async def update(self, id: uuid.UUID, data: Dict[str, Any]) -> T:
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        pass
