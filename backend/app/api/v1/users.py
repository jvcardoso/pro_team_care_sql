"""
Endpoints CRUD de Usuários.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
⚠️  Apenas superusuários podem criar/editar usuários
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os usuários com paginação.

    Requer autenticação JWT.
    """
    repo = BaseRepository(User, db)

    users = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()

    return UserListResponse(total=total, users=users)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca usuário por ID.

    Requer autenticação JWT.
    """
    repo = BaseRepository(User, db)
    user = await repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria novo usuário.

    Requer autenticação JWT + privilégios de superusuário.
    """
    from datetime import datetime

    repo = BaseRepository(User, db)

    # Preparar dados
    data = user_data.model_dump(exclude={'password'})
    data['password'] = hash_password(user_data.password)
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()

    user = await repo.create(data)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza usuário existente.

    Requer autenticação JWT + privilégios de superusuário.
    """
    repo = BaseRepository(User, db)

    # Preparar dados (remover valores None)
    data = user_data.model_dump(exclude_unset=True, exclude={'password'})

    # Se senha foi informada, hashear
    if user_data.password:
        data['password'] = hash_password(user_data.password)

    user = await repo.update(user_id, data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta usuário (soft delete).

    Requer autenticação JWT + privilégios de superusuário.
    """
    repo = BaseRepository(User, db)

    success = await repo.delete(user_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
