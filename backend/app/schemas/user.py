"""
Schemas Pydantic para Users.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Campos base de user"""
    email_address: EmailStr


class UserCreate(UserBase):
    """Schema para criação de user"""
    password: str = Field(..., min_length=8, description="Senha mínima de 8 caracteres")
    person_id: Optional[int] = None
    company_id: Optional[int] = None
    establishment_id: Optional[int] = None
    is_active: bool = True
    is_system_admin: bool = False


class UserUpdate(BaseModel):
    """Schema para atualização de user"""
    email_address: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    company_id: Optional[int] = None
    establishment_id: Optional[int] = None
    notification_settings: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema de resposta (sem senha)"""
    id: int
    person_id: Optional[int] = None
    company_id: Optional[int] = None
    establishment_id: Optional[int] = None
    is_active: bool
    is_system_admin: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema para lista de users"""
    total: int
    users: list[UserResponse]


class EstablishmentSimple(BaseModel):
    """Schema simplificado de establishment para /auth/me"""
    id: int
    name: str


class UserMeResponse(UserBase):
    """Schema estendido para /auth/me com dados de JOINs"""
    id: int
    person_id: Optional[int] = None
    company_id: Optional[int] = None
    establishment_id: Optional[int] = None
    is_active: bool
    is_system_admin: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Dados de JOINs
    full_name: Optional[str] = None  # De people
    company_name: Optional[str] = None  # De companies → people
    establishment_name: Optional[str] = None  # De establishments → people
    context_type: Optional[str] = None  # Tipo de contexto do usuário
    establishments: list[EstablishmentSimple] = []  # Lista de estabelecimentos da empresa
    
    model_config = ConfigDict(from_attributes=True)
