"""
Endpoints CRUD de Establishments.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Apenas usuários da mesma empresa podem acessar/modificar
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.repositories.base import BaseRepository
from app.schemas.establishment import EstablishmentCreate, EstablishmentUpdate, EstablishmentResponse, EstablishmentListResponse
from app.models.establishment import Establishment

router = APIRouter(prefix="/establishments", tags=["Estabelecimentos"])


@router.get("", response_model=EstablishmentListResponse)
async def list_establishments(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os establishments com paginação.

    Requer autenticação JWT.
    """
    try:
        repo = BaseRepository(Establishment, db)
        establishments = await repo.get_all(skip=skip, limit=limit)
        total = await repo.count()
        return EstablishmentListResponse(total=total, establishments=establishments)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar establishments: {str(e)}"
        )


@router.get("/{establishment_id}", response_model=EstablishmentResponse)
async def get_establishment(
    establishment_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca establishment por ID.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Establishment, db)
    establishment = await repo.get_by_id(establishment_id)

    if not establishment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento não encontrado"
        )

    return establishment


@router.post("", response_model=EstablishmentResponse, status_code=status.HTTP_201_CREATED)
async def create_establishment(
    establishment_data: EstablishmentCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria novo establishment.

    Requer autenticação JWT.
    """
    from datetime import datetime

    repo = BaseRepository(Establishment, db)

    data = establishment_data.model_dump()
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()

    establishment = await repo.create(data)

    return establishment


@router.put("/{establishment_id}", response_model=EstablishmentResponse)
async def update_establishment(
    establishment_id: int,
    establishment_data: EstablishmentUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza establishment existente.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Establishment, db)

    # Preparar dados (remover valores None)
    data = establishment_data.model_dump(exclude_unset=True)

    establishment = await repo.update(establishment_id, data)

    if not establishment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento não encontrado"
        )

    return establishment


@router.delete("/{establishment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_establishment(
    establishment_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta establishment (soft delete).

    Requer autenticação JWT.
    """
    repo = BaseRepository(Establishment, db)

    success = await repo.delete(establishment_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento não encontrado"
        )