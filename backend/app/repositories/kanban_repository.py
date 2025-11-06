"""
Repositories para o sistema Kanban Board.

Operações de banco de dados para:
- CardColumns
- Cards
- CardMovements
- CardAssignees
- CardTags
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime

from app.models.kanban import (
    CardColumn, Card, CardMovement, CardAssignee, CardTag, CardImage, MovementImage
)


class CardColumnRepository:
    """Repository para operações de CardColumns"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, company_id: int) -> List[CardColumn]:
        """Lista todas as colunas ativas de uma empresa"""
        query = select(CardColumn).where(
            CardColumn.CompanyID == company_id,
            CardColumn.IsActive == True
        ).order_by(CardColumn.DisplayOrder)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, column_id: int) -> Optional[CardColumn]:
        """Busca coluna por ID"""
        query = select(CardColumn).where(CardColumn.ColumnID == column_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self,
        company_id: int,
        column_name: str,
        display_order: int = 0,
        color: Optional[str] = None
    ) -> CardColumn:
        """Cria nova coluna"""
        column = CardColumn(
            CompanyID=company_id,
            ColumnName=column_name,
            DisplayOrder=display_order,
            Color=color,
            CreatedAt=datetime.utcnow()
        )
        self.db.add(column)
        await self.db.commit()
        await self.db.refresh(column)
        return column


class CardRepository:
    """Repository para operações de Cards"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        company_id: int,
        user_id: int,
        column_id: int,
        title: str,
        description: Optional[str] = None,
        original_text: Optional[str] = None,
        priority: str = 'Média',
        due_date: Optional[datetime] = None
    ) -> Card:
        """Cria novo card"""
        # Criar card com DisplayOrder temporário
        card = Card(
            CompanyID=company_id,
            UserID=user_id,
            ColumnID=column_id,
            DisplayOrder=999999,  # Valor temporário alto
            Title=title,
            Description=description,
            OriginalText=original_text,
            Priority=priority,
            DueDate=due_date,
            CreatedAt=datetime.utcnow()
        )
        self.db.add(card)
        await self.db.flush()  # Obter CardID sem commit

        # Calcular DisplayOrder correto
        max_order_query = select(func.max(Card.DisplayOrder)).where(
            Card.ColumnID == column_id,
            Card.IsDeleted == False,
            Card.CardID != card.CardID  # Excluir o card que acabamos de criar
        )
        max_order_result = await self.db.execute(max_order_query)
        max_order = max_order_result.scalar() or 0

        # Atualizar DisplayOrder usando update
        await self.db.execute(
            update(Card).where(Card.CardID == card.CardID).values(DisplayOrder=max_order + 1)
        )

        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def get_by_id(self, card_id: int, company_id: int) -> Optional[Card]:
        """Busca card por ID"""
        query = select(Card).where(
            Card.CardID == card_id,
            Card.CompanyID == company_id,
            Card.IsDeleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_card_id: str, company_id: int) -> Optional[Card]:
        """Busca card por ExternalCardID"""
        query = select(Card).where(
            Card.ExternalCardID == external_card_id,
            Card.CompanyID == company_id,
            Card.IsDeleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        company_id: int,
        column_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Card]:
        """Lista cards da empresa"""
        query = select(Card).where(
            Card.CompanyID == company_id,
            Card.IsDeleted == False
        )

        if column_id:
            query = query.where(Card.ColumnID == column_id)

        query = query.order_by(Card.DisplayOrder.asc(), Card.CreatedAt.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        card_id: int,
        company_id: int,
        **kwargs
    ) -> Optional[Card]:
        """Atualiza card"""
        card = await self.get_by_id(card_id, company_id)
        if not card:
            return None

        for key, value in kwargs.items():
            if hasattr(card, key) and value is not None:
                setattr(card, key, value)

        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def move_to_column(
        self,
        card_id: int,
        company_id: int,
        new_column_id: int,
        user_id: int,
        new_position: int = None
    ) -> Optional[Card]:
        """
        Move card para outra coluna (drag & drop).
        Cria movimento de auditoria automaticamente.
        """
        card = await self.get_by_id(card_id, company_id)
        if not card:
            return None

        old_column_id = card.ColumnID

        # Buscar nomes das colunas
        from app.models.kanban import CardColumn
        
        old_column_query = select(CardColumn).where(CardColumn.ColumnID == old_column_id)
        old_column_result = await self.db.execute(old_column_query)
        old_column = old_column_result.scalar_one_or_none()
        
        new_column_query = select(CardColumn).where(CardColumn.ColumnID == new_column_id)
        new_column_result = await self.db.execute(new_column_query)
        new_column = new_column_result.scalar_one_or_none()
        
        old_column_name = old_column.ColumnName if old_column else f"Coluna {old_column_id}"
        new_column_name = new_column.ColumnName if new_column else f"Coluna {new_column_id}"

        # Atualizar coluna do card
        card.ColumnID = new_column_id

        # Atualizar ordem se fornecida
        if new_position is not None:
            # Reordenar outros cards na coluna de destino
            await self._reorder_cards_in_column(new_column_id, card_id, new_position)
            card.DisplayOrder = new_position
        else:
            # Se não forneceu posição, colocar no final
            max_order_query = select(func.max(Card.DisplayOrder)).where(
                Card.ColumnID == new_column_id,
                Card.IsDeleted == False
            )
            max_order_result = await self.db.execute(max_order_query)
            max_order = max_order_result.scalar() or 0
            card.DisplayOrder = max_order + 1

        # Criar movimento de auditoria
        movement_repo = CardMovementRepository(self.db)
        await movement_repo.create(
            card_id=card_id,
            user_id=user_id,
            subject=f"Card movido para {new_column_name}",
            description=f"Card movido de '{old_column_name}' para '{new_column_name}'",
            movement_type="ColumnChange",
            old_column_id=old_column_id,
            new_column_id=new_column_id
        )

        # Verificar se é uma coluna de conclusão e definir CompletedDate
        if new_column and ("conclu" in new_column_name.lower() or "final" in new_column_name.lower()):
            from datetime import datetime
            card.CompletedDate = datetime.utcnow()

        # Commit e refresh
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def delete(self, card_id: int, company_id: int) -> bool:
        """Soft delete de card"""
        card = await self.get_by_id(card_id, company_id)
        if not card:
            return False

        card.IsDeleted = True
        card.DeletedAt = datetime.utcnow()
        await self.db.commit()
        return True

    async def _reorder_cards_in_column(
        self,
        column_id: int,
        moving_card_id: int,
        new_position: int
    ) -> None:
        """
        Reordena cards em uma coluna quando um card é inserido em uma posição específica.
        """
        # Buscar todos os cards da coluna (exceto o que está sendo movido)
        query = select(Card).where(
            Card.ColumnID == column_id,
            Card.CardID != moving_card_id,
            Card.IsDeleted == False
        ).order_by(Card.DisplayOrder.asc())
        
        result = await self.db.execute(query)
        cards = list(result.scalars().all())
        
        # Reordenar
        order = 0
        for card in cards:
            if order == new_position:
                order += 1  # Pular a posição do card que está sendo inserido
            card.DisplayOrder = order
            order += 1
        
        await self.db.flush()

    async def get_total_time_spent(self, card_id: int) -> int:
        """Calcula tempo total gasto no card (em minutos)"""
        query = select(func.sum(CardMovement.TimeSpent)).where(
            CardMovement.CardID == card_id
        )
        result = await self.db.execute(query)
        total = result.scalar()
        return total or 0


class CardMovementRepository:
    """Repository para operações de CardMovements"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        card_id: int,
        user_id: int,
        subject: str,
        description: Optional[str] = None,
        time_spent: Optional[int] = None,
        movement_type: Optional[str] = None,
        old_column_id: Optional[int] = None,
        new_column_id: Optional[int] = None,
        old_sub_status: Optional[str] = None,
        new_sub_status: Optional[str] = None
    ) -> CardMovement:
        """Cria novo movimento"""
        movement = CardMovement(
            CardID=card_id,
            UserID=user_id,
            LogDate=datetime.utcnow(),
            Subject=subject,
            Description=description,
            TimeSpent=time_spent,
            MovementType=movement_type,
            OldColumnID=old_column_id,
            NewColumnID=new_column_id,
            OldSubStatus=old_sub_status,
            NewSubStatus=new_sub_status
        )
        self.db.add(movement)
        await self.db.commit()
        await self.db.refresh(movement)
        return movement

    async def get_by_card(
        self,
        card_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CardMovement]:
        """Lista movimentos de um card"""
        from sqlalchemy.orm import selectinload

        query = select(CardMovement).where(
            CardMovement.CardID == card_id
        ).options(selectinload(CardMovement.images)).order_by(CardMovement.LogDate.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        movement_id: int,
        subject: Optional[str] = None,
        description: Optional[str] = None,
        time_spent: Optional[int] = None
    ) -> Optional[CardMovement]:
        """Atualiza movimento"""
        from sqlalchemy.orm import selectinload

        query = select(CardMovement).where(CardMovement.MovementID == movement_id).options(selectinload(CardMovement.images))
        result = await self.db.execute(query)
        movement = result.scalar_one_or_none()

        if not movement:
            return None

        # Só atualiza se o valor não for None e não for string vazia para campos obrigatórios
        if subject is not None and subject.strip():
            movement.Subject = subject.strip()
        if description is not None:
            movement.Description = description.strip() if description.strip() else None
        if time_spent is not None:
            movement.TimeSpent = time_spent

        await self.db.commit()
        await self.db.refresh(movement)
        return movement

    async def delete(self, movement_id: int) -> bool:
        """Deleta movimento"""
        from sqlalchemy.orm import selectinload
        import os

        query = select(CardMovement).where(CardMovement.MovementID == movement_id).options(selectinload(CardMovement.images))
        result = await self.db.execute(query)
        movement = result.scalar_one_or_none()

        if not movement:
            return False

        # Deletar arquivos físicos das imagens associadas
        for image in movement.images:
            try:
                image_path = str(image.ImagePath)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Erro ao deletar arquivo da imagem {image.MovementImageID}: {e}")

        await self.db.delete(movement)
        await self.db.commit()
        return True


class CardAssigneeRepository:
    """Repository para operações de CardAssignees"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        card_id: int,
        person_name: str,
        person_id: Optional[int] = None
    ) -> CardAssignee:
        """Adiciona pessoa ao card"""
        assignee = CardAssignee(
            CardID=card_id,
            PersonName=person_name,
            PersonID=person_id,
            AssignedAt=datetime.utcnow()
        )
        self.db.add(assignee)
        await self.db.commit()
        await self.db.refresh(assignee)
        return assignee

    async def get_by_card(self, card_id: int) -> List[CardAssignee]:
        """Lista assignees de um card"""
        query = select(CardAssignee).where(CardAssignee.CardID == card_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete(self, assignee_id: int) -> bool:
        """Remove assignee"""
        query = select(CardAssignee).where(CardAssignee.AssigneeID == assignee_id)
        result = await self.db.execute(query)
        assignee = result.scalar_one_or_none()

        if not assignee:
            return False

        await self.db.delete(assignee)
        await self.db.commit()
        return True


class CardTagRepository:
    """Repository para operações de CardTags"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        card_id: int,
        tag_name: str,
        tag_color: Optional[str] = None
    ) -> CardTag:
        """Adiciona tag ao card"""
        tag = CardTag(
            CardID=card_id,
            TagName=tag_name,
            TagColor=tag_color,
            CreatedAt=datetime.utcnow()
        )
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def get_by_card(self, card_id: int) -> List[CardTag]:
        """Lista tags de um card"""
        query = select(CardTag).where(CardTag.CardID == card_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete(self, tag_id: int) -> bool:
        """Remove tag"""
        query = select(CardTag).where(CardTag.CardTagID == tag_id)
        result = await self.db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            return False

        await self.db.delete(tag)
        await self.db.commit()
        return True
