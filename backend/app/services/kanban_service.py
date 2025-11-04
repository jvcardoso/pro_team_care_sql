"""
Service para o sistema Kanban Board.

Lógica de negócio para:
- Criação de cards com análise da IA
- Movimentação de cards (drag & drop)
- Registro de movimentos/lançamentos
- Gerenciamento de assignees e tags
"""
import json
import logging
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kanban import Card, CardMovement
from app.repositories.kanban_repository import (
    CardRepository,
    CardMovementRepository,
    CardAssigneeRepository,
    CardTagRepository,
    CardColumnRepository
)
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class KanbanService:
    """Service para operações do Kanban Board"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.card_repo = CardRepository(db)
        self.movement_repo = CardMovementRepository(db)
        self.assignee_repo = CardAssigneeRepository(db)
        self.tag_repo = CardTagRepository(db)
        self.column_repo = CardColumnRepository(db)

    async def create_card_with_ai(
        self,
        company_id: int,
        user_id: int,
        title: str,
        original_text: str,
        column_id: int = 1,  # Default: Backlog
        priority: str = 'Média',
        due_date: Optional[datetime] = None
    ) -> Dict:
        """
        Cria card e analisa com IA.
        
        Returns:
            Dict com card e ai_suggestions
        """
        # Analisar com IA
        logger.info(f"Analisando card com IA: {title}")
        ai_result = await gemini_service.analyze_activity(
            title=title,
            status="Novo",
            raw_text=original_text
        )

        # Extrair dados da IA
        description = ai_result.get("description", "")
        ai_priority = ai_result.get("priority", priority)
        sub_status = ai_result.get("sub_status")
        
        # Parsear due_date se fornecido pela IA
        ai_due_date = ai_result.get("due_date")
        if ai_due_date and not due_date:
            try:
                due_date = datetime.strptime(ai_due_date, "%Y-%m-%d")
            except:
                pass

        # Criar card
        card = await self.card_repo.create(
            company_id=company_id,
            user_id=user_id,
            column_id=column_id,
            title=title,
            description=description,
            original_text=original_text,
            priority=ai_priority,
            due_date=due_date
        )

        # Atualizar SubStatus se houver
        if sub_status:
            await self.card_repo.update(
                card_id=card.CardID,
                company_id=company_id,
                SubStatus=sub_status
            )

        logger.info(f"Card {card.CardID} criado com sucesso")

        return {
            "card": card,
            "ai_suggestions": ai_result
        }

    async def save_validated_data(
        self,
        card_id: int,
        company_id: int,
        user_id: int,
        validated_data: Dict
    ) -> bool:
        """
        Salva dados validados pelo usuário após análise da IA.
        
        Cria:
        - Assignees
        - Tags
        - Movements (sub-tarefas)
        """
        try:
            # Atualizar description se fornecida
            description = validated_data.get("description")
            if description:
                await self.card_repo.update(
                    card_id=card_id,
                    company_id=company_id,
                    Description=description
                )

            # Atualizar priority se fornecida
            priority = validated_data.get("priority")
            if priority:
                await self.card_repo.update(
                    card_id=card_id,
                    company_id=company_id,
                    Priority=priority
                )

            # Atualizar sub_status se fornecido
            sub_status = validated_data.get("sub_status")
            if sub_status:
                await self.card_repo.update(
                    card_id=card_id,
                    company_id=company_id,
                    SubStatus=sub_status
                )

            # Salvar assignees
            for assignee_name in validated_data.get("assignees", []):
                await self.assignee_repo.create(
                    card_id=card_id,
                    person_name=assignee_name
                )

            # Salvar tags
            for tag_name in validated_data.get("tags", []):
                await self.tag_repo.create(
                    card_id=card_id,
                    tag_name=tag_name
                )

            # Salvar movements (sub-tarefas)
            for movement_data in validated_data.get("movements", []):
                await self.movement_repo.create(
                    card_id=card_id,
                    user_id=user_id,
                    subject=movement_data.get("subject", ""),
                    description=movement_data.get("description"),
                    time_spent=movement_data.get("estimated_time"),
                    movement_type="Update"
                )

            logger.info(f"Dados validados salvos para card {card_id}")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar dados validados: {e}")
            return False

    async def add_movement(
        self,
        card_id: int,
        company_id: int,
        user_id: int,
        subject: str,
        description: Optional[str] = None,
        time_spent: Optional[int] = None
    ) -> CardMovement:
        """
        Adiciona movimento/lançamento ao card.
        """
        # Verificar se card existe
        card = await self.card_repo.get_by_id(card_id, company_id)
        if not card:
            raise ValueError(f"Card {card_id} não encontrado")

        # Criar movimento
        movement = await self.movement_repo.create(
            card_id=card_id,
            user_id=user_id,
            subject=subject,
            description=description,
            time_spent=time_spent,
            movement_type="Update"
        )

        logger.info(f"Movimento {movement.MovementID} adicionado ao card {card_id}")
        return movement

    async def move_card(
        self,
        card_id: int,
        company_id: int,
        user_id: int,
        new_column_id: int,
        new_position: int = None
    ) -> Card:
        """
        Move card para outra coluna (drag & drop).
        Cria movimento de auditoria automaticamente.
        """
        card = await self.card_repo.move_to_column(
            card_id=card_id,
            company_id=company_id,
            new_column_id=new_column_id,
            user_id=user_id,
            new_position=new_position
        )

        if not card:
            raise ValueError(f"Card {card_id} não encontrado")

        logger.info(f"Card {card_id} movido para coluna {new_column_id}")
        return card

    async def get_card_with_details(
        self,
        card_id: int,
        company_id: int
    ) -> Optional[Dict]:
        """
        Busca card com todos os detalhes (assignees, tags, movements, etc.)
        """
        card = await self.card_repo.get_by_id(card_id, company_id)
        if not card:
            return None

        # Buscar relacionamentos
        assignees = await self.assignee_repo.get_by_card(card_id)
        tags = await self.tag_repo.get_by_card(card_id)
        movements = await self.movement_repo.get_by_card(card_id)
        total_time = await self.card_repo.get_total_time_spent(card_id)

        return {
            "card": card,
            "assignees": assignees,
            "tags": tags,
            "movements": movements,
            "total_time_spent": total_time
        }

    async def get_board(
        self,
        company_id: int
    ) -> Dict:
        """
        Retorna board completo com todas as colunas e cards.
        
        Returns:
            {
                "columns": [...],
                "cards_by_column": {
                    column_id: [cards...]
                }
            }
        """
        # Buscar colunas
        columns = await self.column_repo.get_all(company_id)

        # Buscar cards por coluna
        cards_by_column = {}
        for column in columns:
            cards = await self.card_repo.get_all(
                company_id=company_id,
                column_id=column.ColumnID
            )
            cards_by_column[column.ColumnID] = cards

        return {
            "columns": columns,
            "cards_by_column": cards_by_column
        }

    async def update_card_status(
        self,
        card_id: int,
        company_id: int,
        user_id: int,
        new_sub_status: str
    ) -> Card:
        """
        Atualiza SubStatus do card.
        Cria movimento de auditoria.
        """
        card = await self.card_repo.get_by_id(card_id, company_id)
        if not card:
            raise ValueError(f"Card {card_id} não encontrado")

        old_sub_status = card.SubStatus

        # Atualizar status
        card = await self.card_repo.update(
            card_id=card_id,
            company_id=company_id,
            SubStatus=new_sub_status
        )

        # Criar movimento de auditoria
        await self.movement_repo.create(
            card_id=card_id,
            user_id=user_id,
            subject=f"Status alterado: {old_sub_status} → {new_sub_status}",
            movement_type="StatusChange",
            old_sub_status=old_sub_status,
            new_sub_status=new_sub_status
        )

        logger.info(f"Status do card {card_id} atualizado para {new_sub_status}")
        return card

    async def complete_card(
        self,
        card_id: int,
        company_id: int,
        user_id: int
    ) -> Card:
        """
        Marca card como concluído.
        Move para coluna "Concluído" e registra data de conclusão.
        """
        # Buscar coluna "Concluído" (assumindo DisplayOrder = 5)
        columns = await self.column_repo.get_all(company_id)
        completed_column = next(
            (c for c in columns if "Conclu" in c.ColumnName),
            None
        )

        if not completed_column:
            raise ValueError("Coluna 'Concluído' não encontrada")

        # Mover para coluna concluído
        card = await self.move_card(
            card_id=card_id,
            company_id=company_id,
            user_id=user_id,
            new_column_id=completed_column.ColumnID
        )

        # Atualizar data de conclusão
        card = await self.card_repo.update(
            card_id=card_id,
            company_id=company_id,
            CompletedDate=datetime.utcnow()
        )

        logger.info(f"Card {card_id} marcado como concluído")
        return card
