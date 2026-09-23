from typing import Type, TypeVar, List, Optional, Any, Dict
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.infrastructure.repositories.base import BaseRepository, T

ModelType = TypeVar("ModelType")

class SQLAlchemyRepository(BaseRepository[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        result = await self.session.execute(select(self.model).filter_by(id=id))
        return result.scalar_one_or_none()

    async def list(self, **filters) -> List[ModelType]:
        stmt = select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: ModelType) -> ModelType:
        self.session.add(data)
        await self.session.flush()
        return data

    async def update(self, id: uuid.UUID, data: Dict[str, Any]) -> ModelType:
        stmt = update(self.model).where(self.model.id == id).values(**data).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, id: uuid.UUID) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
