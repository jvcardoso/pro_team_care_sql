"""
Endpoints CRUD de Pendencies.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Usuários só podem acessar pendências da própria empresa
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.repositories.pendency_repository import PendencyRepository
from app.schemas.pendency import (
    PendencyCreate,
    PendencyUpdate,
    PendencyResponse
)
from app.models.user import User

router = APIRouter(prefix="/pendencies", tags=["Pendências"])


@router.post("", response_model=PendencyResponse, status_code=status.HTTP_201_CREATED)
async def create_pendency(
    pendency: PendencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria nova pendência manualmente.
    """
    repo = PendencyRepository(db)

    result = await repo.create(
        activity_id=pendency.ActivityID,
        description=pendency.Description,
        owner=pendency.Owner,
        status=pendency.Status,
        impediment=pendency.Impediment
    )

    return result


@router.get("", response_model=List[PendencyResponse])
async def list_pendencies(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista pendências da empresa do usuário logado.

    Pode filtrar por status: Pendente, Cobrado, Resolvido
    """
    repo = PendencyRepository(db)

    pendencies = await repo.get_all(
        company_id=current_user.company_id,
        status=status,
        skip=skip,
        limit=limit
    )

    return pendencies


@router.get("/{pendency_id}", response_model=PendencyResponse)
async def get_pendency(
    pendency_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Busca pendência por ID.
    """
    repo = PendencyRepository(db)
    pendency = await repo.get_by_id(pendency_id)

    if not pendency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pendência não encontrada"
        )

    return pendency


@router.put("/{pendency_id}", response_model=PendencyResponse)
async def update_pendency(
    pendency_id: int,
    data: PendencyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza pendência.
    """
    repo = PendencyRepository(db)

    # Converter para dict removendo None
    update_data = data.model_dump(exclude_unset=True)

    pendency = await repo.update(
        pendency_id=pendency_id,
        **update_data
    )

    if not pendency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pendência não encontrada"
        )

    return pendency


@router.patch("/{pendency_id}/status", response_model=PendencyResponse)
async def update_pendency_status(
    pendency_id: int,
    status: str = Query(..., description="Novo status: Pendente, Cobrado, Resolvido"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza apenas o status da pendência.

    Se status = "Resolvido", marca ResolvedAt automaticamente.
    """
    repo = PendencyRepository(db)

    pendency = await repo.update_status(
        pendency_id=pendency_id,
        status=status
    )

    if not pendency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pendência não encontrada"
        )

    return pendency
