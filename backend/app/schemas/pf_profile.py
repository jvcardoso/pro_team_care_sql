"""
Schemas Pydantic para PF Profile (Perfil Pessoa Física).
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PFProfileBase(BaseModel):
    """Schema base para PF Profile"""
    tax_id: str = Field(..., max_length=22, description="CPF (formato: 000.000.000-00)")
    birth_date: Optional[datetime] = Field(None, description="Data de nascimento")
    gender: Optional[str] = Field(None, max_length=40, description="Gênero")
    marital_status: Optional[str] = Field(None, max_length=100, description="Estado civil")
    occupation: Optional[str] = Field(None, max_length=200, description="Profissão/Ocupação")


class PFProfileCreate(PFProfileBase):
    """Schema para criação de PF Profile"""
    person_id: int = Field(..., description="ID da pessoa raiz")


class PFProfileUpdate(BaseModel):
    """Schema para atualização de PF Profile"""
    tax_id: Optional[str] = Field(None, max_length=22, description="CPF")
    birth_date: Optional[datetime] = Field(None, description="Data de nascimento")
    gender: Optional[str] = Field(None, max_length=40, description="Gênero")
    marital_status: Optional[str] = Field(None, max_length=100, description="Estado civil")
    occupation: Optional[str] = Field(None, max_length=200, description="Profissão/Ocupação")


class PFProfileResponse(PFProfileBase):
    """Schema de resposta para PF Profile"""
    id: int
    person_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True