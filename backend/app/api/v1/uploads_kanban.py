"""
Endpoints para upload de imagens do Kanban
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.repositories.kanban_repository import CardRepository
from app.models.kanban import CardImage, MovementImage
from app.core.config import settings

router = APIRouter(prefix="/kanban", tags=["Kanban Uploads"])

# Diretório para salvar uploads
UPLOAD_DIR = "uploads/kanban"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/cards/{card_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_card_image(
    card_id: int,
    file: UploadFile = File(...),
    image_type: str = "reference",
    description: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload de imagem para o card.
    
    Tipos: problem, solution, reference, diagram
    """
    # Verificar se card existe
    card_repo = CardRepository(db)
    card = await card_repo.get_by_id(card_id, current_user.company_id)  # type: ignore
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card não encontrado"
        )
    
    # Validar tipo de arquivo
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Use: {', '.join(allowed_extensions)}"
        )
    
    # Gerar nome único
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Salvar arquivo
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )
    
    # Criar registro no banco
    card_image = CardImage(
        CardID=card_id,
        ImagePath=file_path,
        ImageType=image_type,
        Description=description,
        UploadedBy=current_user.id,  # type: ignore
        UploadedAt=datetime.utcnow()
    )
    
    db.add(card_image)
    await db.flush()  # Flush para obter o ID
    
    # Criar movimento automático para o upload de imagem
    from app.repositories.kanban_repository import CardMovementRepository
    
    movement_repo = CardMovementRepository(db)
    await movement_repo.create(
        card_id=card_id,
        user_id=current_user.id,  # type: ignore
        subject=f"📎 Imagem anexada",
        description=description or "Imagem anexada ao card",
        movement_type="ImageUpload"
    )
    
    # Associar imagem ao movimento recém-criado
    from sqlalchemy import select, desc
    from app.models.kanban import CardMovement, MovementImage
    
    # Buscar o último movimento criado
    query = select(CardMovement).where(
        CardMovement.CardID == card_id,
        CardMovement.MovementType == "ImageUpload"
    ).order_by(desc(CardMovement.MovementID)).limit(1)
    
    result = await db.execute(query)
    last_movement = result.scalar_one_or_none()
    
    if last_movement:
        # Criar MovementImage vinculando a imagem ao movimento
        movement_image = MovementImage(
            MovementID=last_movement.MovementID,
            ImagePath=file_path,
            ImageType=image_type,
            Description=description,
            UploadedAt=datetime.utcnow()
        )
        db.add(movement_image)
    
    await db.commit()
    await db.refresh(card_image)
    
    return {
        "message": "Imagem enviada com sucesso",
        "image_id": card_image.CardImageID,
        "path": file_path,
        "url": f"/uploads/kanban/{unique_filename}"
    }


@router.post("/movements/{movement_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_movement_image(
    movement_id: int,
    file: UploadFile = File(...),
    image_type: str = "evidence",
    description: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload de imagem para o movimento.
    
    Tipos: evidence, before, after, screenshot
    """
    # Validar tipo de arquivo
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Use: {', '.join(allowed_extensions)}"
        )
    
    # Gerar nome único
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Salvar arquivo
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )
    
    # Criar registro no banco
    movement_image = MovementImage(
        MovementID=movement_id,
        ImagePath=file_path,
        ImageType=image_type,
        Description=description,
        UploadedAt=datetime.utcnow()
    )
    
    db.add(movement_image)
    await db.commit()
    await db.refresh(movement_image)
    
    return {
        "message": "Imagem enviada com sucesso",
        "image_id": movement_image.MovementImageID,
        "path": file_path,
        "url": f"/uploads/kanban/{unique_filename}"
    }


@router.delete("/card-images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove imagem do card.
    """
    from sqlalchemy import select
    
    query = select(CardImage).where(CardImage.CardImageID == image_id)
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagem não encontrada"
        )
    
    # Deletar arquivo físico
    try:
        if os.path.exists(image.ImagePath):
            os.remove(image.ImagePath)
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
    
    # Deletar registro
    await db.delete(image)
    await db.commit()
    
    return None


@router.delete("/movement-images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movement_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove imagem do movimento.
    """
    from sqlalchemy import select
    
    query = select(MovementImage).where(MovementImage.MovementImageID == image_id)
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagem não encontrada"
        )
    
    # Deletar arquivo físico
    try:
        if os.path.exists(image.ImagePath):
            os.remove(image.ImagePath)
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
    
    # Deletar registro
    await db.delete(image)
    await db.commit()
    
    return None
