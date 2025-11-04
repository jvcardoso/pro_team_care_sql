"""
Schemas Pydantic para Establishments.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class EstablishmentBase(BaseModel):
    """Campos base de establishment"""
    person_id: int = Field(..., description="ID da pessoa (dados cadastrais)")
    company_id: int = Field(..., description="ID da empresa proprietária")
    code: str = Field(..., max_length=100, description="Código interno único")
    type: Optional[str] = Field(None, max_length=40, description="Tipo: matriz, filial, unidade, posto")
    category: Optional[str] = Field(None, max_length=60, description="Categoria: clinica, hospital, laboratorio, farmacia, etc")
    is_active: bool = Field(default=True, description="Flag de ativo")
    is_principal: bool = Field(default=False, description="Flag de unidade matriz/principal")
    display_order: int = Field(default=0, description="Ordem de exibição")
    settings: Optional[str] = Field(None, description="Configurações específicas (JSON string)")
    # metadata_: Optional[str] = Field(None, alias="metadata", description="Metadados adicionais (JSON string)")  # Temporariamente desabilitado devido a conflito com SQLAlchemy MetaData
    operating_hours: Optional[str] = Field(None, description="Horários de funcionamento (JSON string)")
    service_areas: Optional[str] = Field(None, description="Áreas de atendimento/serviço (JSON string)")


class EstablishmentCreate(EstablishmentBase):
    """Schema para criação de establishment"""


class EstablishmentUpdate(BaseModel):
    """Schema para atualização de establishment"""
    code: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=40)
    category: Optional[str] = Field(None, max_length=60)
    is_active: Optional[bool] = None
    is_principal: Optional[bool] = None
    display_order: Optional[int] = None
    settings: Optional[str] = None
    # metadata_: Optional[str] = Field(None, alias="metadata")  # Temporariamente desabilitado
    operating_hours: Optional[str] = None
    service_areas: Optional[str] = None


class EstablishmentResponse(EstablishmentBase):
    """Schema de resposta"""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class EstablishmentListResponse(BaseModel):
    """Schema para lista de establishments"""
    total: int
    establishments: list[EstablishmentResponse]