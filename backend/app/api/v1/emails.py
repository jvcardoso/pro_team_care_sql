"""
Endpoints CRUD de Emails.

Schema: [core]

⚠️  TODAS AS ROTAS REQUEREM AUTENTICAÇÃO JWT
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.repositories.base import BaseRepository
from app.schemas.email import EmailCreate, EmailUpdate, EmailResponse, EmailListResponse
from app.models.email import Email

router = APIRouter(prefix="/emails", tags=["Emails"])


@router.get("", response_model=EmailListResponse)
async def list_emails(
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os emails com paginação.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Email, db)

    emails = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()

    return EmailListResponse(total=total, emails=emails)


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca email por ID.

    Requer autenticação JWT.
    """
    repo = BaseRepository(Email, db)
    email = await repo.get_by_id(email_id)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email não encontrado"
        )

    return email


@router.post("", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def create_email(
    email_data: EmailCreate,
    db: AsyncSession = Depends(get_db)
):
    """Cria novo email"""
    from datetime import datetime

    repo = BaseRepository(Email, db)

    data = email_data.model_dump()
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()

    email = await repo.create(data)

    return email


@router.put("/{email_id}", response_model=EmailResponse)
async def update_email(
    email_id: int,
    email_data: EmailUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Atualiza email existente"""
    repo = BaseRepository(Email, db)

    # Preparar dados (remover valores None)
    data = email_data.model_dump(exclude_unset=True)

    email = await repo.update(email_id, data)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email não encontrado"
        )

    return email


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    email_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deleta email (soft delete)"""
    repo = BaseRepository(Email, db)

    success = await repo.delete(email_id, soft=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email não encontrado"
        )
