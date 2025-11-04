"""
Repository para Pendencies.
"""
from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from app.models.pendency import Pendency


class PendencyRepository:
    """Repository para operações de Pendencies"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        activity_id: int,
        description: str,
        owner: Optional[str] = None,
        status: str = "Pendente",
        impediment: Optional[str] = None
    ) -> Pendency:
        """Cria nova pendência"""
        pendency = Pendency(
            ActivityID=activity_id,
            Description=description,
            Owner=owner,
            Status=status,
            Impediment=impediment
        )
        self.db.add(pendency)
        await self.db.commit()
        await self.db.refresh(pendency)
        return pendency

    async def get_by_id(self, pendency_id: int) -> Optional[Pendency]:
        """Busca pendência por ID"""
        query = select(Pendency).where(Pendency.PendencyID == pendency_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        company_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Pendency]:
        """Lista pendências (com join em Activity para filtrar por company)"""
        from app.models.activity import Activity

        query = select(Pendency).join(
            Activity, Pendency.ActivityID == Activity.ActivityID
        ).where(
            Activity.CompanyID == company_id,
            Activity.IsDeleted == False
        )

        if status:
            query = query.where(Pendency.Status == status)

        query = query.order_by(Pendency.PendencyID.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        pendency_id: int,
        **kwargs
    ) -> Optional[Pendency]:
        """Atualiza pendência"""
        pendency = await self.get_by_id(pendency_id)
        if not pendency:
            return None

        for key, value in kwargs.items():
            if hasattr(pendency, key) and value is not None:
                setattr(pendency, key, value)

        await self.db.commit()
        await self.db.refresh(pendency)
        return pendency

    async def update_status(
        self,
        pendency_id: int,
        status: str
    ) -> Optional[Pendency]:
        """Atualiza status da pendência"""
        update_query = (
            update(Pendency)
            .where(Pendency.PendencyID == pendency_id)
            .values(Status=status)
        )
        await self.db.execute(update_query)
        await self.db.commit()

        # Depois busca o registro atualizado
        return await self.get_by_id(pendency_id)
