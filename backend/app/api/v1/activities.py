"""
Endpoints CRUD de Activities.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Usuários só podem acessar atividades da própria empresa
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.activity_service import ActivityService
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityWithAISuggestions
)
from app.models.user import User

router = APIRouter(prefix="/activities", tags=["Atividades"])


@router.post("", response_model=ActivityWithAISuggestions, status_code=201)
async def create_activity(
    activity: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria nova atividade e retorna com sugestões da IA.

    A IA analisa o conteúdo (texto/imagem) e sugere:
    - Pessoas envolvidas
    - Sistemas mencionados
    - Datas e prazos
    - Tags para categorização
    - Pendências identificadas
    """
    service = ActivityService(db)

    result = await service.create_with_ai_analysis(
        user_id=current_user.id,  # type: ignore
        company_id=current_user.company_id,  # type: ignore
        title=activity.Title,
        status=activity.Status,
        due_date=activity.DueDate,
        raw_text=activity.RawText,
        raw_image_path=activity.RawImagePath
    )

    return result


@router.post("/{activity_id}/validate", status_code=status.HTTP_200_OK)
async def save_validated_data(
    activity_id: int,
    validated_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Salva dados validados pelo usuário.

    Após a IA sugerir dados, o usuário valida/corrige e envia:
    - pessoas: lista de nomes
    - sistemas: lista de sistemas
    - tags: lista de tags
    - pendencias: lista de objetos {descricao, responsavel, impedimento}
    """
    service = ActivityService(db)

    success = await service.save_validated_data(
        activity_id=activity_id,
        company_id=current_user.company_id,  # type: ignore
        validated_data=validated_data
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada"
        )

    return {"message": "Dados validados salvos com sucesso"}


@router.get("", response_model=List[ActivityResponse])
async def list_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista atividades da empresa do usuário logado.
    """
    service = ActivityService(db)
    activities = await service.get_all(
        company_id=current_user.company_id,  # type: ignore
        skip=skip,
        limit=limit
    )
    return activities


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Busca atividade por ID.
    """
    service = ActivityService(db)
    activity = await service.get_by_id(
        activity_id=activity_id,
        company_id=current_user.company_id  # type: ignore
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada"
        )

    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza atividade.
    """
    service = ActivityService(db)

    # Converter para dict removendo None
    update_data = data.model_dump(exclude_unset=True)

    activity = await service.update(
        activity_id=activity_id,
        company_id=current_user.company_id,  # type: ignore
        **update_data
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada"
        )

    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Exclui atividade (soft delete).
    """
    service = ActivityService(db)

    success = await service.delete(
        activity_id=activity_id,
        company_id=current_user.company_id  # type: ignore
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada"
        )

    return None
