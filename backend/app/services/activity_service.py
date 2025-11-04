"""
Service para Activities - Orquestra lógica de negócio.
"""
import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.repositories.activity_repository import ActivityRepository
from app.repositories.pendency_repository import PendencyRepository
from app.services.gemini_service import gemini_service
from app.models.activity import Activity
from app.models.activity_entity import ActivityEntity

logger = logging.getLogger(__name__)


class ActivityService:
    """Service para operações de Activities"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.activity_repo = ActivityRepository(db)
        self.pendency_repo = PendencyRepository(db)

    async def create_with_ai_analysis(
        self,
        user_id: int,
        company_id: int,
        title: str,
        status: str,
        due_date: Optional[datetime] = None,
        raw_text: Optional[str] = None,
        raw_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cria atividade e retorna com sugestões da IA.

        Returns:
            Dict com dados da atividade + ai_suggestions
        """
        # 1. Criar atividade
        activity = await self.activity_repo.create(
            user_id=user_id,
            company_id=company_id,
            title=title,
            status=status,
            due_date=due_date,
            raw_text=raw_text,
            raw_image_path=raw_image_path
        )

        # 2. Analisar com IA
        ai_suggestions = await gemini_service.analyze_activity(
            title=title,
            status=status,
            raw_text=raw_text,
            raw_image_path=raw_image_path
        )

        # 3. Salvar JSON da IA
        await self.activity_repo.save_ai_extraction(
            activity.ActivityID,  # type: ignore
            json.dumps(ai_suggestions, ensure_ascii=False)
        )

        logger.info(f"Atividade {activity.ActivityID} criada com análise IA")

        # 4. Retornar atividade + sugestões
        return {
            "ActivityID": activity.ActivityID,
            "UserID": activity.UserID,
            "CompanyID": activity.CompanyID,
            "Title": activity.Title,
            "Status": activity.Status,
            "CreationDate": activity.CreationDate,
            "DueDate": activity.DueDate,
            "IsDeleted": activity.IsDeleted,
            "DeletedAt": activity.DeletedAt,
            "ai_suggestions": ai_suggestions
        }

    async def save_validated_data(
        self,
        activity_id: int,
        company_id: int,
        validated_data: Dict[str, Any]
    ) -> bool:
        """
        Salva dados validados pelo usuário (entidades + pendências).

        Args:
            activity_id: ID da atividade
            company_id: ID da empresa (validação)
            validated_data: Dict com pessoas, sistemas, pendencias
        """
        # Verificar se atividade existe e pertence à empresa
        activity = await self.activity_repo.get_by_id(activity_id, company_id)
        if not activity:
            return False

        # Salvar JSON validado
        await self.activity_repo.save_user_corrections(
            activity_id,
            json.dumps(validated_data, ensure_ascii=False)
        )

        # Salvar entidades (pessoas)
        for pessoa in validated_data.get("pessoas", []):
            entity = ActivityEntity(
                ActivityID=activity_id,
                EntityType="Pessoa",
                EntityValue=pessoa
            )
            self.db.add(entity)

        # Salvar entidades (sistemas)
        for sistema in validated_data.get("sistemas", []):
            entity = ActivityEntity(
                ActivityID=activity_id,
                EntityType="Sistema",
                EntityValue=sistema
            )
            self.db.add(entity)

        # Salvar pendências
        for pend in validated_data.get("pendencias", []):
            await self.pendency_repo.create(
                activity_id=activity_id,
                description=pend.get("descricao", ""),
                owner=pend.get("responsavel"),
                impediment=pend.get("impedimento")
            )

        await self.db.commit()
        logger.info(f"Dados validados salvos para atividade {activity_id}")
        return True

    async def get_by_id(
        self,
        activity_id: int,
        company_id: int
    ) -> Optional[Activity]:
        """Busca atividade por ID"""
        return await self.activity_repo.get_by_id(activity_id, company_id)

    async def get_all(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Activity]:
        """Lista atividades da empresa"""
        return await self.activity_repo.get_all(company_id, skip, limit)

    async def update(
        self,
        activity_id: int,
        company_id: int,
        **kwargs
    ) -> Optional[Activity]:
        """
        Atualiza atividade.
        Se RawText for fornecido, reprocessa com IA.
        """
        # Se tem RawText, processar com IA
        raw_text = kwargs.pop('RawText', None)
        
        if raw_text:
            # Buscar atividade para pegar título e status
            activity = await self.activity_repo.get_by_id(activity_id, company_id)
            if not activity:
                return None
            
            # Processar com IA
            ai_result = await gemini_service.analyze_activity(
                title=kwargs.get('Title', activity.Title),
                status=kwargs.get('Status', activity.Status),
                raw_text=raw_text
            )
            
            # Salvar novo conteúdo com análise da IA
            await self.activity_repo.save_ai_analysis(
                activity_id,
                raw_text,
                json.dumps(ai_result, ensure_ascii=False)
            )
        
        # Atualizar campos básicos
        return await self.activity_repo.update(activity_id, company_id, **kwargs)

    async def delete(
        self,
        activity_id: int,
        company_id: int
    ) -> bool:
        """Soft delete de atividade"""
        return await self.activity_repo.delete(activity_id, company_id)
