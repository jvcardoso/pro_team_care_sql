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
from pydantic import BaseModel

# Schemas
class ProcessImageRequest(BaseModel):
    """Schema para processar imagem com IA"""
    image_id: int
    user_description: str = ""

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
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome do arquivo não fornecido"
        )
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
    
    # Criar registro no banco (apenas CardImage, sem movimento automático)
    card_image = CardImage(
        CardID=card_id,
        ImagePath=file_path,
        ImageType=image_type,
        Description=description,
        UploadedBy=current_user.id,  # type: ignore
        UploadedAt=datetime.utcnow()
    )

    db.add(card_image)
    await db.commit()
    await db.refresh(card_image)
    
    return {
        "message": "Imagem enviada com sucesso",
        "image_id": card_image.CardImageID,
        "path": file_path,
        "url": f"/uploads/kanban/{unique_filename}"
    }


@router.post("/cards/{card_id}/process-image", status_code=status.HTTP_201_CREATED)
async def process_card_image_with_ai(
    card_id: int,
    payload: ProcessImageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Processa imagem existente com IA e cria movimento.
    Recebe image_id (de CardImage) + descrição do usuário no body.
    """
    image_id = payload.image_id
    user_description = payload.user_description
    # Verificar se card existe
    card_repo = CardRepository(db)
    card = await card_repo.get_by_id(card_id, current_user.company_id)  # type: ignore

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card não encontrado"
        )

    # Buscar imagem existente
    from sqlalchemy import select
    from app.models.kanban import CardImage

    query = select(CardImage).where(
        CardImage.CardImageID == image_id,
        CardImage.CardID == card_id
    )
    result = await db.execute(query)
    card_image = result.scalar_one_or_none()

    if not card_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagem não encontrada neste card"
        )

    # Processar análise de IA da imagem + descrição do usuário
    ai_analysis = ""
    try:
        from app.services.gemini_service import GeminiService
        gemini_service = GeminiService()

        # Prompt para análise específica do anexo
        prompt = f"""
        Analise esta imagem anexada a um card do kanban.

        Descrição fornecida pelo usuário: "{user_description}"

        Forneça uma análise concisa sobre:
        1. O que a imagem mostra (elementos visuais, diagramas, screenshots, etc.)
        2. Como ela se relaciona com a descrição do usuário
        3. Qualquer insight ou observação relevante para gestão de projetos
        4. Sugestões de como usar esta imagem no contexto do card

        Mantenha a análise objetiva e útil para o contexto de gestão de projetos.
        """

        # Usar análise real de imagem com Gemini Vision
        print(f"🔍 Iniciando análise de imagem: {card_image.ImagePath}")
        response = await gemini_service._analyze_with_image(prompt, str(card_image.ImagePath))
        if response and hasattr(response, 'text'):
            ai_analysis = response.text
            print(f"✅ Análise de imagem concluída: {len(ai_analysis)} caracteres")
        else:
            ai_analysis = "Análise não disponível"
            print("❌ Resposta da IA não contém texto")
    except Exception as e:
        print(f"Erro na análise de IA: {e}")
        ai_analysis = "Análise não disponível"

    # Criar movimento para o processamento da imagem
    from app.repositories.kanban_repository import CardMovementRepository

    movement_repo = CardMovementRepository(db)
    movement = await movement_repo.create(
        card_id=card_id,
        user_id=current_user.id,  # type: ignore
        subject=user_description or "Imagem processada com IA",
        description="Imagem processada com análise de IA",
        movement_type="ImageProcessed"
    )

    # Truncar análise da IA se for muito longa (limite seguro para evitar erros de truncamento)
    max_ai_analysis_length = 4000
    if ai_analysis and len(ai_analysis) > max_ai_analysis_length:
        ai_analysis = ai_analysis[:max_ai_analysis_length] + "..."
        logger.warning(f"Análise da IA truncada para {max_ai_analysis_length} caracteres")

    # Criar MovementImage vinculando a imagem ao movimento
    movement_image = MovementImage(
        MovementID=movement.MovementID,
        ImagePath=card_image.ImagePath,
        ImageType=card_image.ImageType,
        Description=user_description,  # Descrição do usuário
        AIAnalysis=ai_analysis,        # Análise da IA
        UploadedAt=datetime.utcnow()
    )
    db.add(movement_image)

    await db.commit()
    await db.refresh(movement_image)

    return {
        "message": "Imagem processada com IA e movimento criado",
        "movement_id": movement.MovementID,
        "movement_image_id": movement_image.MovementImageID,
        "ai_analysis": ai_analysis
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
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome do arquivo não fornecido"
        )
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
        image_path = str(image.ImagePath)
        if os.path.exists(image_path):
            os.remove(image_path)
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
        image_path = str(image.ImagePath)
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
    
    # Deletar registro
    await db.delete(image)
    await db.commit()
    
    return None
