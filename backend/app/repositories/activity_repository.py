"""
Repository para Activities.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from app.models.activity import Activity
from app.models.activity_content import ActivityContent


class ActivityRepository:
    """Repository para operações de Activities"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        company_id: int,
        title: str,
        status: str,
        due_date: Optional[datetime] = None,
        raw_text: Optional[str] = None,
        raw_image_path: Optional[str] = None
    ) -> Activity:
        """Cria nova atividade com conteúdo"""
        # Criar atividade
        activity = Activity(
            UserID=user_id,
            CompanyID=company_id,
            Title=title,
            Status=status,
            CreationDate=datetime.utcnow(),
            DueDate=due_date,
            IsDeleted=False
        )
        self.db.add(activity)
        await self.db.flush()  # Get ActivityID

        # Criar conteúdo
        content = ActivityContent(
            ActivityID=activity.ActivityID,
            RawText=raw_text,
            RawImagePath=raw_image_path
        )
        self.db.add(content)

        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def get_by_id(
        self,
        activity_id: int,
        company_id: int
    ) -> Optional[Activity]:
        """Busca atividade por ID (com filtro de company)"""
        query = select(Activity).where(
            Activity.ActivityID == activity_id,
            Activity.CompanyID == company_id,
            Activity.IsDeleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Activity]:
        """Lista atividades da empresa (sem carregar relacionamentos)"""
        query = (
            select(Activity)
            .where(
                Activity.CompanyID == company_id,
                Activity.IsDeleted == False
            )
            .order_by(Activity.CreationDate.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        activity_id: int,
        company_id: int,
        **kwargs
    ) -> Optional[Activity]:
        """Atualiza atividade"""
        activity = await self.get_by_id(activity_id, company_id)
        if not activity:
            return None

        for key, value in kwargs.items():
            if hasattr(activity, key) and value is not None:
                setattr(activity, key, value)

        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def save_ai_extraction(
        self,
        activity_id: int,
        ai_json: str
    ) -> bool:
        """Salva JSON da análise da IA no conteúdo"""
        update_query = (
            update(ActivityContent)
            .where(ActivityContent.ActivityID == activity_id)
            .values(AIExtractionJSON=ai_json)
        )
        result = await self.db.execute(update_query)
        await self.db.commit()
        return result.rowcount > 0

    async def save_user_corrections(
        self,
        activity_id: int,
        user_json: str
    ) -> bool:
        """Salva JSON validado pelo usuário"""
        update_query = (
            update(ActivityContent)
            .where(ActivityContent.ActivityID == activity_id)
            .values(UserCorrectedJSON=user_json)
        )
        result = await self.db.execute(update_query)
        await self.db.commit()
        return result.rowcount > 0

    async def delete(
        self,
        activity_id: int,
        company_id: int
    ) -> bool:
        """Soft delete de atividade"""
        # Verificar se atividade existe
        activity = await self.get_by_id(activity_id, company_id)
        if not activity:
            return False

        # Soft delete usando update query
        update_query = (
            update(Activity)
            .where(Activity.ActivityID == activity_id)
            .values(IsDeleted=True, DeletedAt=datetime.utcnow())
        )
        result = await self.db.execute(update_query)
        await self.db.commit()
        return result.rowcount > 0
