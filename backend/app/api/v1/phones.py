"""
Endpoints CRUD de Phones.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.repositories.base import BaseRepository
from app.schemas.phone import PhoneCreate, PhoneUpdate, PhoneResponse, PhoneListResponse
from app.models.phone import Phone

router = APIRouter(prefix="/phones", tags=["Telefones"])


@router.get("", response_model=PhoneListResponse)
async def list_phones(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os telefones com paginação.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Phone, db)

    phones = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()

    return PhoneListResponse(total=total, phones=phones)


@router.get("/{phone_id}", response_model=PhoneResponse)
async def get_phone(
    phone_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca telefone por ID.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Phone, db)
    phone = await repo.get_by_id(phone_id)

    if not phone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telefone não encontrado"
        )

    return phone


@router.post("", response_model=PhoneResponse, status_code=status.HTTP_201_CREATED)
async def create_phone(
    phone_data: PhoneCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria novo telefone.

    Requer autenticação JWT.
    """
    from datetime import datetime

    repo = BaseRepository(Phone, db)

    data = phone_data.model_dump()
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()

    phone = await repo.create(data)
    return phone


@router.put("/{phone_id}", response_model=PhoneResponse)
async def update_phone(
    phone_id: int,
    phone_data: PhoneUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza telefone existente.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Phone, db)

    # Preparar dados (remover valores None)
    data = phone_data.model_dump(exclude_unset=True)

    phone = await repo.update(phone_id, data)

    if not phone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telefone não encontrado"
        )

    return phone


@router.delete("/{phone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_phone(
    phone_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta telefone (soft delete).

    Requer autenticação JWT.
    """
    repo = BaseRepository(Phone, db)

    success = await repo.delete(phone_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telefone não encontrado"
        )
