"""
Schemas Pydantic para Companies.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    """Campos base de company"""
    access_status: Optional[str] = 'pending_contract'
    settings: Optional[Dict[str, Any]] = None
    # company_metadata: Optional[Dict[str, Any]] = None  # Temporariamente desabilitado devido a conflito com SQLAlchemy MetaData
    display_order: Optional[int] = 0


class CompanyCreate(CompanyBase):
    """Schema para criação de company"""
    person_id: Optional[int] = None
    # Campos opcionais para verificação de duplicatas
    name: Optional[str] = None
    tax_id: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


# ============================================================================
# SCHEMAS PARA CADASTRO COMPLETO VIA JSON
# ============================================================================

class PJProfileData(BaseModel):
    """Dados do perfil PJ"""
    name: str = Field(..., description="Razão Social")
    trade_name: str = Field(..., description="Nome Fantasia")
    tax_id: str = Field(..., max_length=22, description="CNPJ")
    incorporation_date: Optional[str] = Field(None, description="Data de constituição")
    tax_regime: Optional[str] = Field(None, description="Regime tributário")
    legal_nature: Optional[str] = Field(None, description="Natureza jurídica")
    municipal_registration: Optional[str] = Field(None, description="Inscrição municipal")


class AddressData(BaseModel):
    """Dados de endereço"""
    street: str = Field(..., description="Logradouro")
    number: str = Field(..., description="Número")
    details: Optional[str] = Field(None, description="Complemento")
    neighborhood: str = Field(..., description="Bairro")
    city: str = Field(..., description="Cidade")
    state: str = Field(..., max_length=2, description="UF")
    zip_code: str = Field(..., max_length=10, description="CEP")
    country: str = Field(default="BR", max_length=2, description="País")
    type: str = Field(default="commercial", description="Tipo de endereço")
    is_principal: bool = Field(default=True, description="Endereço principal")


class PhoneData(BaseModel):
    """Dados de telefone"""
    country_code: Optional[str] = Field("55", max_length=3, description="Código do país")
    number: str = Field(..., description="Número do telefone")
    type: str = Field(default="commercial", description="Tipo de telefone")
    is_principal: bool = Field(default=True, description="Telefone principal")
    is_whatsapp: bool = Field(default=False, description="É WhatsApp")
    phone_name: Optional[str] = Field(None, description="Nome/Identificação do telefone")


class EmailData(BaseModel):
    """Dados de e-mail"""
    email_address: str = Field(..., description="Endereço de e-mail")
    type: str = Field(default="work", description="Tipo de e-mail")
    is_principal: bool = Field(default=True, description="E-mail principal")


class CompanyCompleteCreate(BaseModel):
    """Schema para criação completa de empresa via JSON"""
    access_status: str = Field(default="pending_contract", description="Status de acesso")
    pj_profile: PJProfileData = Field(..., description="Dados do perfil PJ")
    addresses: List[AddressData] = Field(default_factory=list, description="Lista de endereços")
    phones: List[PhoneData] = Field(default_factory=list, description="Lista de telefones")
    emails: List[EmailData] = Field(default_factory=list, description="Lista de e-mails")


class CompanyCompleteUpdate(BaseModel):
    """Schema para atualização completa de empresa via JSON"""
    access_status: Optional[str] = Field(None, description="Status de acesso")
    pj_profile: Optional[PJProfileData] = Field(None, description="Dados do perfil PJ")
    addresses: Optional[List[AddressData]] = Field(None, description="Lista de endereços")
    phones: Optional[List[PhoneData]] = Field(None, description="Lista de telefones")
    emails: Optional[List[EmailData]] = Field(None, description="Lista de e-mails")


class CompanyCompleteResponse(BaseModel):
    """Schema de resposta para criação completa"""
    new_company_id: int
    new_person_id: int
    new_pj_profile_id: int
    message: str = "Empresa criada com sucesso"


class CompanyUpdateCompleteResponse(BaseModel):
    """Schema de resposta para atualização completa"""
    updated_company_id: int
    updated_person_id: int
    updated_pj_profile_id: int
    message: str = "Empresa atualizada com sucesso"


class CompanyUpdate(BaseModel):
    """Schema para atualização de company"""
    person_id: Optional[int] = None
    access_status: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    # company_metadata: Optional[Dict[str, Any]] = None  # Temporariamente desabilitado
    display_order: Optional[int] = None
    contract_accepted_by: Optional[str] = None


class CompanyResponse(CompanyBase):
    """Schema de resposta"""
    id: int
    person_id: Optional[int] = None
    contract_terms_version: Optional[str] = None
    contract_accepted_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyListResponse(BaseModel):
    """Schema para lista de companies"""
    total: int
    companies: list[CompanyResponse]
