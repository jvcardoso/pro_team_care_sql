"""
Repository para ActivityImages.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.activity_image import ActivityImage


class ActivityImageRepository:
    """Repository para gerenciar imagens de atividades"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        activity_id: int,
        image_path: str,
        image_order: int = 0
    ) -> ActivityImage:
        """Cria um novo registro de imagem"""
        image = ActivityImage(
            ActivityID=activity_id,
            ImagePath=image_path,
            ImageOrder=image_order
        )
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def create_many(
        self,
        activity_id: int,
        image_paths: List[str]
    ) -> List[ActivityImage]:
        """Cria múltiplos registros de imagens"""
        images = []
        for order, path in enumerate(image_paths):
            image = ActivityImage(
                ActivityID=activity_id,
                ImagePath=path,
                ImageOrder=order
            )
            self.db.add(image)
            images.append(image)
        
        await self.db.commit()
        
        # Refresh todos os objetos
        for image in images:
            await self.db.refresh(image)
        
        return images

    async def get_by_activity(
        self,
        activity_id: int
    ) -> List[ActivityImage]:
        """Busca todas as imagens de uma atividade"""
        query = select(ActivityImage).where(
            ActivityImage.ActivityID == activity_id,
            ActivityImage.IsDeleted.is_(False)
        ).order_by(ActivityImage.ImageOrder)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete(
        self,
        image_id: int
    ) -> bool:
        """Soft delete de uma imagem"""
        query = select(ActivityImage).where(
            ActivityImage.ImageID == image_id
        )
        result = await self.db.execute(query)
        image = result.scalar_one_or_none()
        
        if image:
            image.IsDeleted = True
            await self.db.commit()
            return True
        return False

    async def delete_by_activity(
        self,
        activity_id: int
    ) -> int:
        """Soft delete de todas as imagens de uma atividade"""
        images = await self.get_by_activity(activity_id)
        count = 0
        
        for image in images:
            image.IsDeleted = True
            count += 1
        
        if count > 0:
            await self.db.commit()
        
        return count
