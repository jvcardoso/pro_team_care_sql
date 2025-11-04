"""
BaseService - Serviço genérico com lógica de negócio.
Camada entre API e Repository.
"""
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType")
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, RepositoryType]):
    """
    Serviço base com operações de negócio genéricas.

    Usa BaseRepository internamente.

    Uso:
        user_service = BaseService(UserRepository, db)
        users = await user_service.list_all()
    """

    def __init__(
        self,
        repository_class: Type[RepositoryType],
        model: Type[ModelType],
        db: AsyncSession
    ):
        self.repository = repository_class(model, db)
        self.db = db

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Lista todos os registros ativos"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Busca por ID"""
        return await self.repository.get_by_id(id)

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Cria novo registro.
        Sobrescreva para adicionar validações de negócio.
        """
        return await self.repository.create(data)

    async def update(
        self,
        id: int,
        data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Atualiza registro.
        Sobrescreva para adicionar validações de negócio.
        """
        # Verificar se existe
        exists = await self.repository.exists(id)
        if not exists:
            return None

        return await self.repository.update(id, data)

    async def delete(self, id: int) -> bool:
        """
        Deleta registro (soft delete).
        Sobrescreva para adicionar validações de negócio.
        """
        # Verificar se existe
        exists = await self.repository.exists(id)
        if not exists:
            return False

        return await self.repository.delete(id, soft=True)

    async def count(self) -> int:
        """Conta registros ativos"""
        return await self.repository.count()
