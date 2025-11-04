"""
Schemas Pydantic para Phones.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PhoneBase(BaseModel):
    """Campos base de phone"""
    phoneable_type: str = Field(..., max_length=255, description="Tipo da entidade (Person, Establishment, etc)")
    phoneable_id: int = Field(..., description="ID da entidade proprietária")
    number: str = Field(..., max_length=20, description="Número do telefone")
    country_code: str = Field(default="55", max_length=3, description="Código do país")
    extension: Optional[str] = Field(None, max_length=10, description="Ramal")
    type: str = Field(default="mobile", max_length=20, description="Tipo: landline, mobile, whatsapp, commercial, emergency, fax")
    is_principal: bool = Field(default=False, description="Telefone principal")
    is_active: bool = Field(default=True, description="Telefone ativo")
    phone_name: Optional[str] = Field(None, max_length=100, description="Nome do telefone/contato")
    is_whatsapp: bool = Field(default=False, description="Possui WhatsApp")
    whatsapp_formatted: Optional[str] = Field(None, max_length=15, description="Número formatado para WhatsApp")
    whatsapp_verified: bool = Field(default=False, description="WhatsApp verificado")
    whatsapp_business: bool = Field(default=False, description="É WhatsApp Business")
    whatsapp_name: Optional[str] = Field(None, max_length=100, description="Nome no WhatsApp")
    accepts_whatsapp_marketing: bool = Field(default=True, description="Aceita marketing via WhatsApp")
    accepts_whatsapp_notifications: bool = Field(default=True, description="Aceita notificações via WhatsApp")
    carrier: Optional[str] = Field(None, max_length=30, description="Nome da operadora")
    line_type: Optional[str] = Field(None, max_length=20, description="Tipo da linha")
    contact_priority: int = Field(default=5, description="Prioridade de contato")
    can_receive_calls: bool = Field(default=True, description="Pode receber chamadas")
    can_receive_sms: bool = Field(default=True, description="Pode receber SMS")
    verification_method: Optional[str] = Field(None, max_length=50, description="Método de verificação")


class PhoneCreate(PhoneBase):
    """Schema para criação de phone"""
    company_id: int = Field(..., description="ID da empresa (multi-tenant)")
    api_data: Optional[str] = Field(None, description="Dados de APIs externas (JSON)")


class PhoneUpdate(BaseModel):
    """Schema para atualização de phone"""
    number: Optional[str] = Field(None, max_length=20)
    country_code: Optional[str] = Field(None, max_length=3)
    extension: Optional[str] = Field(None, max_length=10)
    type: Optional[str] = Field(None, max_length=20)
    is_principal: Optional[bool] = None
    is_active: Optional[bool] = None
    phone_name: Optional[str] = Field(None, max_length=100)
    is_whatsapp: Optional[bool] = None
    whatsapp_formatted: Optional[str] = Field(None, max_length=15)
    whatsapp_verified: Optional[bool] = None
    whatsapp_business: Optional[bool] = None
    whatsapp_name: Optional[str] = Field(None, max_length=100)
    accepts_whatsapp_marketing: Optional[bool] = None
    accepts_whatsapp_notifications: Optional[bool] = None
    carrier: Optional[str] = Field(None, max_length=30)
    line_type: Optional[str] = Field(None, max_length=20)
    contact_priority: Optional[int] = None
    can_receive_calls: Optional[bool] = None
    can_receive_sms: Optional[bool] = None
    verification_method: Optional[str] = Field(None, max_length=50)
    api_data: Optional[str] = Field(None)


class PhoneResponse(PhoneBase):
    """Schema de resposta"""
    id: int
    company_id: int
    whatsapp_verified_at: Optional[datetime] = None
    last_contact_attempt: Optional[datetime] = None
    last_contact_success: Optional[datetime] = None
    contact_attempts_count: int
    verified_at: Optional[datetime] = None
    api_data: Optional[str] = None
    created_by_user_id: Optional[int] = None
    updated_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PhoneListResponse(BaseModel):
    """Schema para lista de phones"""
    total: int
    phones: list[PhoneResponse]
