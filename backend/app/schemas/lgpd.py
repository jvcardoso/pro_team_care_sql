"""
Schemas Pydantic para endpoints LGPD.

Inclui schemas para:
- Reveal de campos sensíveis
- Auditoria de ações
- Logs de auditoria
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Request Schemas
class RevealFieldRequest(BaseModel):
    """Request para revelar um campo sensível."""
    field_name: str = Field(..., description="Nome do campo a revelar (ex: tax_id, email)")

    class Config:
        json_schema_extra = {
            "example": {
                "field_name": "tax_id"
            }
        }


class RevealFieldsRequest(BaseModel):
    """Request para revelar múltiplos campos sensíveis."""
    field_names: List[str] = Field(..., description="Lista de nomes dos campos a revelar")

    class Config:
        json_schema_extra = {
            "example": {
                "field_names": ["tax_id", "email"]
            }
        }


class AuditActionRequest(BaseModel):
    """Request para auditar uma ação sensível."""
    action_type: str = Field(..., description="Tipo da ação (call, email, maps, waze, whatsapp)")
    resource_type: str = Field(..., description="Tipo do recurso (phone, email, address)")
    resource_id: int = Field(..., description="ID do recurso acessado")

    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "call",
                "resource_type": "phone",
                "resource_id": 123
            }
        }


class AuditLogFilters(BaseModel):
    """Filtros para busca de logs de auditoria."""
    page: int = Field(1, ge=1, description="Página atual")
    size: int = Field(50, ge=1, le=500, description="Itens por página (máximo 500)")
    entity_type: Optional[str] = Field(None, description="Tipo da entidade (companies, clients, etc.)")
    entity_id: Optional[int] = Field(None, description="ID da entidade específica")
    user_id: Optional[int] = Field(None, description="ID do usuário")
    action_type: Optional[str] = Field(None, description="Tipo da ação")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 50,
                "entity_id": 164,
                "user_id": 5,
                "action_type": "VIEW"
            }
        }


# Response Schemas
class RevealFieldResponse(BaseModel):
    """Response para reveal de campo único."""
    status: str = Field(..., description="Status da operação")
    field_name: str = Field(..., description="Nome do campo revelado")
    field_value: str = Field(..., description="Valor do campo revelado")
    revealed_at: datetime = Field(..., description="Data/hora do reveal")
    revealed_by: int = Field(..., description="ID do usuário que revelou")
    message: str = Field(..., description="Mensagem de confirmação")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "revealed",
                "field_name": "tax_id",
                "field_value": "12345678000123",
                "revealed_at": "2025-01-15T10:30:00Z",
                "revealed_by": 1,
                "message": "Campo revelado com sucesso"
            }
        }


class RevealFieldsResponse(BaseModel):
    """Response para reveal de múltiplos campos."""
    status: str = Field(..., description="Status da operação")
    revealed_data: Dict[str, str] = Field(..., description="Dados revelados (campo -> valor)")
    revealed_count: int = Field(..., description="Quantidade de campos revelados")
    revealed_at: datetime = Field(..., description="Data/hora do reveal")
    revealed_by: int = Field(..., description="ID do usuário que revelou")
    message: str = Field(..., description="Mensagem de confirmação")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "revealed",
                "revealed_data": {
                    "tax_id": "12345678000123",
                    "email": "contato@empresa.com"
                },
                "revealed_count": 2,
                "revealed_at": "2025-01-15T10:30:00Z",
                "revealed_by": 1,
                "message": "2 campos revelados com sucesso"
            }
        }


class AuditActionResponse(BaseModel):
    """Response para auditoria de ação."""
    status: str = Field(..., description="Status da operação")
    action_type: str = Field(..., description="Tipo da ação auditada")
    resource_type: str = Field(..., description="Tipo do recurso auditado")
    resource_id: int = Field(..., description="ID do recurso auditado")
    audited_at: datetime = Field(..., description="Data/hora da auditoria")
    audited_by: int = Field(..., description="ID do usuário que auditou")
    message: str = Field(..., description="Mensagem de confirmação")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "audited",
                "action_type": "call",
                "resource_type": "phone",
                "resource_id": 123,
                "audited_at": "2025-01-15T10:30:00Z",
                "audited_by": 1,
                "message": "Ação auditada com sucesso"
            }
        }


class AuditLogEntry(BaseModel):
    """Entrada individual do log de auditoria."""
    id: int = Field(..., description="ID do log")
    created_at: datetime = Field(..., description="Data/hora da ação")
    user_id: int = Field(..., description="ID do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")
    action_type: str = Field(..., description="Tipo da ação")
    entity_type: str = Field(..., description="Tipo da entidade")
    entity_id: Optional[int] = Field(None, description="ID da entidade")
    sensitive_fields: Optional[List[str]] = Field(None, description="Campos sensíveis acessados")
    changed_fields: Optional[Dict[str, Any]] = Field(None, description="Campos alterados")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    endpoint: Optional[str] = Field(None, description="Endpoint acessado")
    description: Optional[str] = Field(None, description="Descrição da ação")
    additional_info: Optional[Dict[str, Any]] = Field(None, description="Informações adicionais")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "created_at": "2025-01-15T10:30:00Z",
                "user_id": 5,
                "user_email": "admin@proteamcare.com.br",
                "action_type": "VIEW",
                "entity_type": "company",
                "entity_id": 164,
                "sensitive_fields": ["tax_id"],
                "ip_address": "192.168.11.83",
                "endpoint": "GET /api/v1/companies/164",
                "description": "Visualização de empresa"
            }
        }


class AuditLogResponse(BaseModel):
    """Response paginado para logs de auditoria."""
    items: List[AuditLogEntry] = Field(..., description="Lista de entradas do log")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Itens por página")
    pages: int = Field(..., description="Total de páginas")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 123,
                        "created_at": "2025-01-15T10:30:00Z",
                        "user_id": 5,
                        "user_email": "admin@proteamcare.com.br",
                        "action_type": "VIEW",
                        "entity_type": "company",
                        "entity_id": 164,
                        "sensitive_fields": ["tax_id"],
                        "ip_address": "192.168.11.83",
                        "endpoint": "GET /api/v1/companies/164",
                        "description": "Visualização de empresa"
                    }
                ],
                "total": 25,
                "page": 1,
                "size": 50,
                "pages": 1
            }
        }


class CompanyContactsResponse(BaseModel):
    """Response para contatos da empresa."""
    company_id: int = Field(..., description="ID da empresa")
    name: str = Field(..., description="Nome da empresa")
    trade_name: Optional[str] = Field(None, description="Nome fantasia")
    phones: List[Dict[str, Any]] = Field(..., description="Lista de telefones")
    emails: List[Dict[str, Any]] = Field(..., description="Lista de emails")

    class Config:
        json_schema_extra = {
            "example": {
                "company_id": 164,
                "name": "Empresa Exemplo Ltda",
                "trade_name": "Empresa Exemplo",
                "phones": [
                    {
                        "number": "11999999999",
                        "type": "COMMERCIAL",
                        "is_principal": True
                    }
                ],
                "emails": [
                    {
                        "email": "contato@empresa.com",
                        "type": "WORK",
                        "is_principal": True
                    }
                ]
            }
        }