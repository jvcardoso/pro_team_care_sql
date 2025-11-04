"""
BaseRepository - Repositório genérico com CRUD completo.
Reutilizável para qualquer model SQLAlchemy.
"""
from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import DeclarativeMeta
from datetime import datetime

# TypeVar para tipagem genérica
ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Repositório base com operações CRUD genéricas.

    Suporta soft delete automático.

    Uso:
        user_repo = BaseRepository(User, db)
        users = await user_repo.get_all()
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        Lista todos os registros.

        Args:
            skip: Quantidade de registros a pular (pagination)
            limit: Limite de registros a retornar
            include_deleted: Incluir registros soft deleted
        """
        query = select(self.model)

        # Filtrar soft delete
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.where(self.model.deleted_at.is_(None))

        # SQL Server requer ORDER BY para OFFSET/LIMIT
        # Usar ID como ordenação padrão
        query = query.order_by(self.model.id)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(
        self,
        id: int,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        Busca um registro por ID.

        Args:
            id: ID do registro
            include_deleted: Incluir registros soft deleted
        """
        query = select(self.model).where(self.model.id == id)

        # Filtrar soft delete
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Cria um novo registro.

        Args:
            data: Dicionário com dados do registro
        """
        db_obj = self.model(**data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        id: int,
        data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Atualiza um registro existente.

        Args:
            id: ID do registro
            data: Dicionário com dados a atualizar
        """
        # Adicionar updated_at se existir
        if hasattr(self.model, 'updated_at'):
            data['updated_at'] = datetime.utcnow()

        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
        )

        await self.db.execute(stmt)
        await self.db.commit()

        return await self.get_by_id(id)

    async def delete(self, id: int, soft: bool = True) -> bool:
        """
        Deleta um registro (soft delete por padrão).

        Args:
            id: ID do registro
            soft: Se True, faz soft delete; se False, deleta permanentemente
        """
        if soft and hasattr(self.model, 'deleted_at'):
            # Soft delete
            await self.update(id, {'deleted_at': datetime.utcnow()})
            return True
        else:
            # Hard delete
            stmt = delete(self.model).where(self.model.id == id)
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.rowcount > 0

    async def count(self, include_deleted: bool = False) -> int:
        """
        Conta total de registros.

        Args:
            include_deleted: Incluir registros soft deleted
        """
        query = select(func.count(self.model.id))

        # Filtrar soft delete
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(query)
        return result.scalar()

    async def exists(self, id: int) -> bool:
        """
        Verifica se registro existe.

        Args:
            id: ID do registro
        """
        obj = await self.get_by_id(id)
        return obj is not None
