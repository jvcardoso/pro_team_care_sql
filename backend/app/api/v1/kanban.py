"""
Endpoints FastAPI para o sistema Kanban Board.

Rotas:
- GET /kanban/board - Board completo
- GET /kanban/cards - Lista cards
- POST /kanban/cards - Cria card com IA
- GET /kanban/cards/{id} - Detalhes do card
- PUT /kanban/cards/{id} - Atualiza card
- DELETE /kanban/cards/{id} - Deleta card
- POST /kanban/cards/{id}/move - Move card (drag & drop)
- POST /kanban/cards/{id}/validate - Salva dados validados
- POST /kanban/cards/{id}/movements - Adiciona movimento
- GET /kanban/columns - Lista colunas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.kanban_service import KanbanService
from app.schemas.kanban import (
    CardCreate,
    CardCreateWithAI,
    CardResponse,
    CardWithDetails,
    CardWithAISuggestions,
    CardUpdate,
    CardMoveRequest,
    ValidatedCardData,
    CardMovementCreate,
    CardMovementResponse,
    CardColumnResponse
)
from app.models.user import User

router = APIRouter(prefix="/kanban", tags=["Kanban Board"])


# ============================================================================
# Board e Colunas
# ============================================================================

@router.get("/board")
async def get_board(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna board completo com todas as colunas e cards.
    """
    service = KanbanService(db)
    board = await service.get_board(current_user.company_id)  # type: ignore
    return board


@router.get("/columns", response_model=List[CardColumnResponse])
async def list_columns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista colunas do board.
    """
    service = KanbanService(db)
    columns = await service.column_repo.get_all(current_user.company_id)  # type: ignore
    return columns


# ============================================================================
# Cards - CRUD
# ============================================================================

@router.post("/cards", response_model=CardWithAISuggestions, status_code=status.HTTP_201_CREATED)
async def create_card(
    data: CardCreateWithAI,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria card e analisa com IA.
    
    Retorna card criado + sugestões da IA.
    """
    service = KanbanService(db)

    result = await service.create_card_with_ai(
        company_id=current_user.company_id,  # type: ignore
        user_id=current_user.id,  # type: ignore
        title=data.Title,
        original_text=data.OriginalText,
        column_id=data.ColumnID,
        priority=data.Priority,
        due_date=data.DueDate
    )

    return {
        **result["card"].__dict__,
        "ai_suggestions": result["ai_suggestions"]
    }


@router.get("/cards", response_model=List[CardResponse])
async def list_cards(
    column_id: Optional[int] = Query(None, description="Filtrar por coluna"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista cards da empresa.
    """
    service = KanbanService(db)
    cards = await service.card_repo.get_all(
        company_id=current_user.company_id,  # type: ignore
        column_id=column_id,
        skip=skip,
        limit=limit
    )
    return cards


@router.get("/cards/{card_id}", response_model=CardWithDetails)
async def get_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Busca card com todos os detalhes (assignees, tags, movements, etc.)
    """
    service = KanbanService(db)
    card_data = await service.get_card_with_details(
        card_id=card_id,
        company_id=current_user.company_id  # type: ignore
    )

    if not card_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card não encontrado"
        )

    return {
        **card_data["card"].__dict__,
        "assignees": card_data["assignees"],
        "tags": card_data["tags"],
        "movements": card_data["movements"],
        "total_time_spent": card_data["total_time_spent"]
    }


@router.put("/cards/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: int,
    data: CardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza card.
    """
    service = KanbanService(db)

    # Converter para dict removendo None
    update_data = data.model_dump(exclude_unset=True)

    card = await service.card_repo.update(
        card_id=card_id,
        company_id=current_user.company_id,  # type: ignore
        **update_data
    )

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card não encontrado"
        )

    return card


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deleta card (soft delete).
    """
    service = KanbanService(db)

    success = await service.card_repo.delete(
        card_id=card_id,
        company_id=current_user.company_id  # type: ignore
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card não encontrado"
        )

    return None


# ============================================================================
# Operações Especiais
# ============================================================================

@router.post("/cards/{card_id}/move", response_model=CardResponse)
async def move_card(
    card_id: int,
    data: CardMoveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Move card para outra coluna (drag & drop).
    Cria movimento de auditoria automaticamente.
    """
    service = KanbanService(db)

    try:
        card = await service.move_card(
            card_id=card_id,
            company_id=current_user.company_id,  # type: ignore
            user_id=current_user.id,  # type: ignore
            new_column_id=data.NewColumnID,
            new_position=data.NewDisplayOrder
        )
        return card

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/cards/{card_id}/validate")
async def save_validated_data(
    card_id: int,
    validated_data: ValidatedCardData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Salva dados validados pelo usuário após análise da IA.
    
    Cria assignees, tags e movements.
    """
    service = KanbanService(db)

    success = await service.save_validated_data(
        card_id=card_id,
        company_id=current_user.company_id,  # type: ignore
        user_id=current_user.id,  # type: ignore
        validated_data=validated_data.model_dump()
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar dados validados"
        )

    return {"message": "Dados validados salvos com sucesso"}


@router.post("/cards/{card_id}/movements", response_model=CardMovementResponse, status_code=status.HTTP_201_CREATED)
async def add_movement(
    card_id: int,
    data: CardMovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Adiciona movimento/lançamento ao card.
    """
    service = KanbanService(db)

    try:
        movement = await service.add_movement(
            card_id=card_id,
            company_id=current_user.company_id,  # type: ignore
            user_id=current_user.id,  # type: ignore
            subject=data.Subject,
            description=data.Description,
            time_spent=data.TimeSpent
        )
        return movement

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/cards/{card_id}/complete", response_model=CardResponse)
async def complete_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Marca card como concluído.
    Move para coluna "Concluído" e registra data de conclusão.
    """
    service = KanbanService(db)

    try:
        card = await service.complete_card(
            card_id=card_id,
            company_id=current_user.company_id,  # type: ignore
            user_id=current_user.id  # type: ignore
        )
        return card

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================================================
# Tags
# ============================================================================

@router.post("/cards/{card_id}/tags", status_code=status.HTTP_201_CREATED)
async def add_tag_to_card(
    card_id: int,
    tag_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Adiciona tag ao card.
    """
    from app.repositories.kanban_repository import CardTagRepository
    from datetime import datetime
    
    tag_name = tag_data.get("TagName")
    if not tag_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TagName é obrigatório"
        )
    
    tag_repo = CardTagRepository(db)
    tag = await tag_repo.create(
        card_id=card_id,
        tag_name=tag_name
    )
    
    return {"message": "Tag adicionada com sucesso", "tag_id": tag.CardTagID}


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove tag.
    """
    from app.repositories.kanban_repository import CardTagRepository
    
    tag_repo = CardTagRepository(db)
    success = await tag_repo.delete(tag_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag não encontrada"
        )
    
    return None
