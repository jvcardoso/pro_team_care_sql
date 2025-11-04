"""
Schemas Pydantic para serviços externos
ViaCEP, ReceitaWS, Nominatim
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# ========================================
# VIA CEP SCHEMAS
# ========================================

class AddressEnrichmentRequest(BaseModel):
    """Request para enriquecimento de endereço"""
    cep: str = Field(..., description="CEP com ou sem formatação")

    @validator('cep')
    def validate_cep(cls, v):
        if not v:
            raise ValueError('CEP não pode ser vazio')
        # Remove formatação e valida tamanho mínimo
        clean_cep = ''.join(filter(str.isdigit, v))
        if len(clean_cep) < 8:
            raise ValueError('CEP deve ter pelo menos 8 dígitos')
        return v


class AddressEnrichmentResponse(BaseModel):
    """Response do enriquecimento de endereço"""
    cep: str
    logradouro: str
    complemento: Optional[str]
    bairro: str
    localidade: str
    uf: str
    ibge: str
    gia: Optional[str]
    ddd: str
    siafi: str

    # Campos enriquecidos
    ibge_state_code: Optional[int]
    endereco_completo: Optional[str]

    # Metadata
    _metadata: Optional[Dict[str, Any]]


# ========================================
# RECEITA WS SCHEMAS
# ========================================

class CNPJConsultRequest(BaseModel):
    """Request para consulta CNPJ"""
    cnpj: str = Field(..., description="CNPJ com ou sem formatação")

    @validator('cnpj')
    def validate_cnpj(cls, v):
        if not v:
            raise ValueError('CNPJ não pode ser vazio')
        # Remove formatação e valida tamanho mínimo
        clean_cnpj = ''.join(filter(str.isdigit, v))
        if len(clean_cnpj) < 14:
            raise ValueError('CNPJ deve ter pelo menos 14 dígitos')
        return v


class CNPJActivity(BaseModel):
    """Atividade econômica da empresa"""
    code: str
    text: str


class CNPJConsultResponse(BaseModel):
    """Response da consulta CNPJ"""
    cnpj: str
    nome: str
    fantasia: Optional[str]
    status: str
    ultima_atualizacao: str
    tipo: str
    abertura: str
    situacao: str
    logradouro: str
    numero: str
    complemento: Optional[str]
    bairro: str
    municipio: str
    uf: str
    cep: str
    telefone: Optional[str]
    email: Optional[str]
    atividade_principal: List[CNPJActivity]
    atividades_secundarias: List[CNPJActivity]
    natureza_juridica: str
    capital_social: str
    porte: str
    data_situacao: str
    motivo_situacao: Optional[str]
    situacao_especial: Optional[str]
    data_situacao_especial: Optional[str]

    # Campos enriquecidos
    atividade_principal_descricao: Optional[str]
    endereco_completo: Optional[str]

    # Metadata
    _metadata: Optional[Dict[str, Any]]


# ========================================
# NOMINATIM GEOCODING SCHEMAS
# ========================================

class GeocodingRequest(BaseModel):
    """Request para geocoding"""
    address: str = Field(..., description="Endereço completo")
    city: Optional[str] = Field(None, description="Cidade para melhorar precisão")
    state: Optional[str] = Field(None, description="Estado para melhorar precisão")


class GeocodingResponse(BaseModel):
    """Response do geocoding"""
    latitude: float
    longitude: float
    display_name: str
    type: str
    importance: float
    address: Dict[str, Any]
    boundingbox: List[str]
    original_query: str

    # Metadata
    _metadata: Optional[Dict[str, Any]]


class ReverseGeocodingRequest(BaseModel):
    """Request para reverse geocoding"""
    latitude: float = Field(..., description="Latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude", ge=-180, le=180)


class ReverseGeocodingResponse(BaseModel):
    """Response do reverse geocoding"""
    latitude: float
    longitude: float
    display_name: str
    type: str
    importance: float
    address: Dict[str, Any]
    boundingbox: List[str]

    # Metadata
    _metadata: Optional[Dict[str, Any]]


# ========================================
# COMBINED SCHEMAS PARA INTEGRAÇÃO
# ========================================

class CompanyEnrichmentRequest(BaseModel):
    """Request para enriquecimento completo de empresa"""
    cnpj: Optional[str] = None
    cep: Optional[str] = None
    endereco_completo: Optional[str] = None


class CompanyEnrichmentResponse(BaseModel):
    """Response do enriquecimento completo de empresa"""
    cnpj_data: Optional[CNPJConsultResponse]
    address_data: Optional[AddressEnrichmentResponse]
    geocoding_data: Optional[GeocodingResponse]

    # Status dos serviços
    services_status: Dict[str, str] = Field(
        ...,
        description="Status de cada serviço: 'success', 'error', 'not_requested'"
    )

    # Metadata
    _metadata: Dict[str, Any]