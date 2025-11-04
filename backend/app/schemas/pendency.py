"""
Schemas Pydantic para Pendencies.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PendencyBase(BaseModel):
    """Campos base de pendency"""
    Description: str = Field(..., max_length=500, description="Descrição da pendência")
    Owner: Optional[str] = Field(None, max_length=255, description="Responsável")
    Status: str = Field(default="Pendente", max_length=50, description="Status")
    Impediment: Optional[str] = Field(None, description="Descrição do impedimento")


class PendencyCreate(PendencyBase):
    """Schema para criação de pendency"""
    ActivityID: int


class PendencyUpdate(BaseModel):
    """Schema para atualização de pendency"""
    Description: Optional[str] = Field(None, max_length=500)
    Owner: Optional[str] = Field(None, max_length=255)
    Status: Optional[str] = Field(None, max_length=50)
    Impediment: Optional[str] = None


class PendencyResponse(PendencyBase):
    """Schema de resposta de pendency"""
    PendencyID: int
    ActivityID: int
    IsDeleted: bool = False
    DeletedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PendencyWithActivity(PendencyResponse):
    """Schema de resposta com dados da atividade"""
    activity_title: Optional[str] = None
    activity_status: Optional[str] = None
