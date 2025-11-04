"""
Schemas Pydantic para Emails.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class EmailBase(BaseModel):
    """Campos base de email"""
    emailable_type: str = Field(..., max_length=50, description="Tipo da entidade (Person, Establishment, etc)")
    emailable_id: int = Field(..., description="ID da entidade proprietária")
    email_address: EmailStr = Field(..., description="Endereço de email")
    type: str = Field(default="pessoal", max_length=20, description="Tipo: pessoal, profissional, comercial, financeiro, suporte, outro")
    is_principal: bool = Field(default=False, description="Email principal")
    notes: Optional[str] = Field(None, max_length=500, description="Observações")


class EmailCreate(EmailBase):
    """Schema para criação de email"""
    company_id: int = Field(..., description="ID da empresa (multi-tenant)")


class EmailUpdate(BaseModel):
    """Schema para atualização de email"""
    email_address: Optional[EmailStr] = None
    type: Optional[str] = Field(None, max_length=20)
    is_principal: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class EmailResponse(EmailBase):
    """Schema de resposta"""
    id: int
    company_id: int
    is_verified: bool
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EmailListResponse(BaseModel):
    """Schema para lista de emails"""
    total: int
    emails: list[EmailResponse]
