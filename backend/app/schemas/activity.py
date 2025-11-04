"""
Schemas Pydantic para Activities.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    """Campos base de activity"""
    Title: str = Field(..., max_length=255, description="Título/Assunto da atividade")
    Status: str = Field(..., max_length=50, description="Status da atividade")
    DueDate: Optional[datetime] = Field(None, description="Data/hora de prazo")


class ActivityCreate(ActivityBase):
    """Schema para criação de activity"""
    RawText: Optional[str] = Field(None, description="Texto colado")
    RawImagePath: Optional[str] = Field(None, max_length=512, description="Imagem")


class ActivityUpdate(BaseModel):
    """Schema para atualização de activity"""
    Title: Optional[str] = Field(None, max_length=255)
    Status: Optional[str] = Field(None, max_length=50)
    DueDate: Optional[datetime] = None
    RawText: Optional[str] = Field(None, description="Conteúdo para reprocessar com IA")


class ActivityResponse(ActivityBase):
    """Schema de resposta de activity"""
    ActivityID: int
    UserID: int
    CompanyID: int
    CreationDate: datetime
    IsDeleted: bool
    DeletedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ActivityWithAISuggestions(ActivityResponse):
    """Schema de resposta com sugestões da IA"""
    ai_suggestions: Optional[Dict[str, Any]] = Field(
        None,
        description="Sugestões extraídas pela IA (pessoas, tags, pendências)"
    )


class ActivityWithDetails(ActivityResponse):
    """Schema de resposta com detalhes completos"""
    contents: List[Dict[str, Any]] = Field(default_factory=list)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    pendencies: List[Dict[str, Any]] = Field(default_factory=list)
