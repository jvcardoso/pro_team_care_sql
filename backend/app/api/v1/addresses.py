"""
Endpoints CRUD de Addresses.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.repositories.base import BaseRepository
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse, AddressListResponse
from app.models.address import Address

router = APIRouter(prefix="/addresses", tags=["Endereços"])


@router.get("", response_model=AddressListResponse)
async def list_addresses(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os endereços com paginação.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Address, db)

    addresses = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()

    return AddressListResponse(total=total, addresses=addresses)


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca endereço por ID.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Address, db)
    address = await repo.get_by_id(address_id)

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço não encontrado"
        )

    return address


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreate,
    db: AsyncSession = Depends(get_db)
):
    """Cria novo endereço"""
    from datetime import datetime

    repo = BaseRepository(Address, db)

    data = address_data.model_dump()
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()

    address = await repo.create(data)

    return address


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Atualiza endereço existente"""
    repo = BaseRepository(Address, db)

    # Preparar dados (remover valores None)
    data = address_data.model_dump(exclude_unset=True)

    address = await repo.update(address_id, data)

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço não encontrado"
        )

    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deleta endereço (soft delete)"""
    repo = BaseRepository(Address, db)

    success = await repo.delete(address_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço não encontrado"
        )
