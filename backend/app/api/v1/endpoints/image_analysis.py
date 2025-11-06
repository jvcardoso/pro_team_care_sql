"""
Endpoints para análise de imagens com IA
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
import logging

from app.services.image_description_service import image_description_service
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


class ImageDescriptionRequest(BaseModel):
    """Request para descrição de imagem base64"""
    image_base64: str
    mime_type: str = "image/jpeg"
    context: Optional[str] = None


class ImageDescriptionResponse(BaseModel):
    """Response com descrição gerada"""
    description: str
    success: bool
    message: Optional[str] = None


@router.post("/analyze-upload", response_model=ImageDescriptionResponse)
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    context: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analisa imagem enviada via upload e retorna descrição
    
    - **file**: Arquivo de imagem (JPG, PNG, GIF, WebP)
    - **context**: Contexto opcional (ex: "card de desenvolvimento")
    """
    try:
        # Validar tipo de arquivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Arquivo deve ser uma imagem"
            )

        # Ler conteúdo
        content = await file.read()

        # Salvar temporariamente
        import tempfile
        import os

        # Usar extensão baseada no content_type
        ext = '.jpg'  # default
        if file.content_type == 'image/png':
            ext = '.png'
        elif file.content_type == 'image/gif':
            ext = '.gif'
        elif file.content_type == 'image/webp':
            ext = '.webp'

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Gerar descrição
            description = await image_description_service.generate_description(
                tmp_path,
                context=context
            )
            
            if not description:
                return ImageDescriptionResponse(
                    description="",
                    success=False,
                    message="Não foi possível gerar descrição automática. Serviço pode estar desabilitado."
                )
            
            return ImageDescriptionResponse(
                description=description,
                success=True,
                message="Descrição gerada com sucesso"
            )
            
        finally:
            # Limpar arquivo temporário
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Erro ao analisar imagem: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar imagem: {str(e)}"
        )


@router.post("/analyze-base64", response_model=ImageDescriptionResponse)
async def analyze_base64_image(
    request: ImageDescriptionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Analisa imagem em base64 e retorna descrição
    
    - **image_base64**: Imagem codificada em base64
    - **mime_type**: Tipo MIME (image/jpeg, image/png, etc)
    - **context**: Contexto opcional
    """
    try:
        description = await image_description_service.generate_description_from_base64(
            request.image_base64,
            mime_type=request.mime_type,
            context=request.context
        )
        
        if not description:
            return ImageDescriptionResponse(
                description="",
                success=False,
                message="Não foi possível gerar descrição automática"
            )
        
        return ImageDescriptionResponse(
            description=description,
            success=True,
            message="Descrição gerada com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao analisar imagem base64: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar imagem: {str(e)}"
        )


@router.get("/status")
async def get_service_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Verifica se o serviço de análise de imagens está ativo
    """
    from app.core.config import settings

    return {
        "enabled": image_description_service.enabled,
        "model": settings.GEMINI_MODEL if image_description_service.enabled else None,
        "message": "Serviço ativo" if image_description_service.enabled else "Configure GEMINI_API_KEY no .env"
    }
