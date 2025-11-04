"""
Endpoints para upload de arquivos.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import uuid
from pathlib import Path
import logging
from app.core.dependencies import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uploads", tags=["Uploads"])

# Diretório de uploads
UPLOAD_DIR = Path("uploads/activities")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Tipos de imagem permitidos
ALLOWED_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp"
}

# Tamanho máximo: 5MB
MAX_SIZE = 5 * 1024 * 1024


@router.post("/images")
async def upload_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Upload de múltiplas imagens.
    
    Validações:
    - Apenas imagens (jpeg, png, gif, webp)
    - Máximo 5MB por imagem
    - Máximo 10 imagens por request
    
    Returns:
        dict: Lista de paths das imagens salvas
    """
    # Validar número de arquivos
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Máximo de 10 imagens por upload"
        )
    
    uploaded_paths = []
    
    for file in files:
        # Validar tipo
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo não permitido: {file.content_type}. Permitidos: jpeg, png, gif, webp"
            )
        
        # Ler conteúdo
        content = await file.read()
        
        # Validar tamanho
        if len(content) > MAX_SIZE:
            size_mb = len(content) / 1024 / 1024
            raise HTTPException(
                status_code=400,
                detail=f"Imagem muito grande ({size_mb:.1f}MB). Máximo: 5MB"
            )
        
        # Gerar nome único
        ext = file.filename.split(".")[-1] if "." in file.filename else "png"
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = UPLOAD_DIR / filename
        
        # Salvar arquivo
        try:
            with open(filepath, "wb") as f:
                f.write(content)
            
            # Retornar path relativo
            relative_path = str(filepath)
            uploaded_paths.append(relative_path)
            
            logger.info(f"✅ Imagem salva: {relative_path} ({len(content)} bytes)")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar imagem: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao salvar imagem: {str(e)}"
            )
    
    return {
        "paths": uploaded_paths,
        "count": len(uploaded_paths),
        "message": f"{len(uploaded_paths)} imagem(ns) enviada(s) com sucesso"
    }


@router.delete("/images/{filename}")
async def delete_image(
    filename: str,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Deleta uma imagem do servidor.
    
    Args:
        filename: Nome do arquivo (UUID.ext)
    """
    filepath = UPLOAD_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail="Imagem não encontrada"
        )
    
    try:
        os.remove(filepath)
        logger.info(f"✅ Imagem deletada: {filepath}")
        return {"message": "Imagem deletada com sucesso"}
    except Exception as e:
        logger.error(f"❌ Erro ao deletar imagem: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar imagem: {str(e)}"
        )
