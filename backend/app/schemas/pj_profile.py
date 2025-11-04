"""
Schemas Pydantic para PJ Profile (Perfil Pessoa Jurídica).
"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class PJProfileBase(BaseModel):
    """Schema base para PJ Profile"""
    tax_id: str = Field(..., max_length=28, description="CNPJ (formato: XX.XXX.XXX/XXXX-XX onde X = letra ou número)")
    trade_name: Optional[str] = Field(None, max_length=400, description="Nome Fantasia")
    incorporation_date: Optional[date] = Field(None, description="Data de constituição")
    tax_regime: Optional[str] = Field(None, max_length=100, description="Regime tributário")
    legal_nature: Optional[str] = Field(None, max_length=200, description="Natureza jurídica")
    municipal_registration: Optional[str] = Field(None, max_length=40, description="Inscrição municipal")


class PJProfileCreate(PJProfileBase):
    """Schema para criação de PJ Profile"""
    person_id: int = Field(..., description="ID da pessoa raiz")
    company_id: int = Field(..., description="ID da empresa")


class PJProfileUpdate(BaseModel):
    """Schema para atualização de PJ Profile"""
    tax_id: Optional[str] = Field(None, max_length=28, description="CNPJ (formato: XX.XXX.XXX/XXXX-XX onde X = letra ou número)")
    trade_name: Optional[str] = Field(None, max_length=400, description="Nome Fantasia")
    incorporation_date: Optional[date] = Field(None, description="Data de constituição")
    tax_regime: Optional[str] = Field(None, max_length=100, description="Regime tributário")
    legal_nature: Optional[str] = Field(None, max_length=200, description="Natureza jurídica")
    municipal_registration: Optional[str] = Field(None, max_length=40, description="Inscrição municipal")


class PJProfileResponse(PJProfileBase):
    """Schema de resposta para PJ Profile"""
    id: int
    person_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True