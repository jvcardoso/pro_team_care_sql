"""
Schemas Pydantic para Addresses.
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class AddressBase(BaseModel):
    """Campos base de address"""
    addressable_type: str = Field(..., max_length=255, description="Tipo da entidade (Person, Establishment, etc)")
    addressable_id: int = Field(..., description="ID da entidade proprietária")
    street: str = Field(..., max_length=255, description="Logradouro")
    number: Optional[str] = Field(None, max_length=20, description="Número")
    details: Optional[str] = Field(None, max_length=100, description="Detalhes/complemento")
    neighborhood: str = Field(..., max_length=100, description="Bairro")
    city: str = Field(..., max_length=100, description="Cidade")
    state: str = Field(..., max_length=2, description="UF")
    zip_code: str = Field(..., max_length=10, description="CEP")
    country: str = Field(default="BR", max_length=2, description="Código do país")
    type: str = Field(default="commercial", max_length=20, description="Tipo: residencial, comercial, cobranca, entrega, correspondencia, outro")
    is_principal: bool = Field(default=False, description="Endereço principal")
    latitude: Optional[Decimal] = Field(None, description="Latitude")
    longitude: Optional[Decimal] = Field(None, description="Longitude")
    google_place_id: Optional[str] = Field(None, max_length=255, description="ID do lugar no Google")
    formatted_address: Optional[str] = Field(None, description="Endereço formatado")
    ibge_city_code: Optional[int] = Field(None, description="Código IBGE da cidade")
    access_notes: Optional[str] = Field(None, description="Notas de acesso")
    is_validated: bool = Field(default=False, description="Endereço validado")
    validation_source: Optional[str] = Field(None, max_length=100, description="Fonte da validação")


class AddressCreate(AddressBase):
    """Schema para criação de address"""
    company_id: int = Field(..., description="ID da empresa (multi-tenant)")
    api_data: Optional[str] = Field(None, description="Dados de APIs externas (JSON)")


class AddressUpdate(BaseModel):
    """Schema para atualização de address"""
    street: Optional[str] = Field(None, max_length=255)
    number: Optional[str] = Field(None, max_length=20)
    details: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=2)
    type: Optional[str] = Field(None, max_length=20)
    is_principal: Optional[bool] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    google_place_id: Optional[str] = Field(None, max_length=255)
    formatted_address: Optional[str] = Field(None)
    ibge_city_code: Optional[int] = None
    access_notes: Optional[str] = Field(None)
    is_validated: Optional[bool] = None
    validation_source: Optional[str] = Field(None, max_length=100)
    api_data: Optional[str] = Field(None)


class AddressResponse(AddressBase):
    """Schema de resposta"""
    id: int
    company_id: int
    last_validated_at: Optional[datetime] = None
    api_data: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AddressListResponse(BaseModel):
    """Schema para lista de addresses"""
    total: int
    addresses: list[AddressResponse]
