"""
Schemas Pydantic para Roles e Permissões (RBAC).
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# PERMISSION SCHEMAS
# ============================================================================

class PermissionBase(BaseModel):
    """Schema base para Permission"""
    name: str = Field(..., description="Nome único (ex: users.view)")
    display_name: str = Field(..., description="Nome de exibição")
    description: Optional[str] = Field(None, description="Descrição")
    resource: str = Field(..., description="Recurso (ex: users)")
    action: str = Field(..., description="Ação (ex: view, create)")


class PermissionCreate(PermissionBase):
    """Schema para criar Permission"""
    is_active: bool = True


class PermissionUpdate(BaseModel):
    """Schema para atualizar Permission"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    """Schema de resposta para Permission"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ROLE SCHEMAS
# ============================================================================

class RoleBase(BaseModel):
    """Schema base para Role"""
    name: str = Field(..., max_length=250, description="Nome único do role")
    display_name: str = Field(..., max_length=400, description="Nome de exibição")
    description: Optional[str] = Field(None, description="Descrição do role")
    level: int = Field(default=100, ge=0, le=1000, description="Nível hierárquico (0=mais alto)")
    context_type: str = Field(default="establishment", description="Contexto: system, company, establishment")


class RoleCreate(RoleBase):
    """Schema para criar Role"""
    is_active: bool = True
    is_system_role: bool = False
    permission_ids: Optional[List[int]] = Field(default=[], description="IDs das permissões")


class RoleUpdate(BaseModel):
    """Schema para atualizar Role"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = Field(None, ge=0, le=1000)
    context_type: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema de resposta para Role"""
    id: int
    is_active: bool
    is_system_role: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """Schema de Role com suas permissões"""
    permissions: List[PermissionResponse] = []


# ============================================================================
# USER ROLE SCHEMAS
# ============================================================================

class UserRoleBase(BaseModel):
    """Schema base para UserRole"""
    user_id: int
    role_id: int
    context_type: str = Field(default="establishment", description="Tipo de contexto")
    context_id: Optional[int] = Field(None, description="ID do contexto")
    status: str = Field(default="active", description="Status: active, inactive, expired, revoked")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração (opcional)")


class UserRoleCreate(BaseModel):
    """Schema para atribuir role a usuário"""
    role_id: int
    context_type: str = "establishment"
    context_id: Optional[int] = None
    expires_at: Optional[datetime] = None


class UserRoleUpdate(BaseModel):
    """Schema para atualizar UserRole"""
    status: Optional[str] = None
    expires_at: Optional[datetime] = None


class UserRoleResponse(UserRoleBase):
    """Schema de resposta para UserRole"""
    id: int
    assigned_by_user_id: Optional[int] = None
    assigned_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserRoleWithDetails(UserRoleResponse):
    """Schema de UserRole com detalhes do role"""
    role: RoleResponse


# ============================================================================
# ROLE PERMISSION SCHEMAS
# ============================================================================

class RolePermissionCreate(BaseModel):
    """Schema para associar permissão a role"""
    permission_ids: List[int] = Field(..., description="IDs das permissões")


class RolePermissionResponse(BaseModel):
    """Schema de resposta para RolePermission"""
    id: int
    role_id: int
    permission_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# BULK OPERATIONS
# ============================================================================

class BulkUserRoleCreate(BaseModel):
    """Schema para atribuir múltiplos roles a um usuário"""
    role_ids: List[int] = Field(..., description="IDs dos roles")
    context_type: str = "establishment"
    context_id: Optional[int] = None


class BulkUserRoleResponse(BaseModel):
    """Schema de resposta para operação em lote"""
    success: bool
    created_count: int
    roles: List[UserRoleResponse]


# ============================================================================
# PERMISSION CHECK
# ============================================================================

class PermissionCheckRequest(BaseModel):
    """Schema para verificar permissão"""
    user_id: int
    permission_name: str = Field(..., description="Nome da permissão (ex: users.view)")
    context_type: Optional[str] = None
    context_id: Optional[int] = None


class PermissionCheckResponse(BaseModel):
    """Schema de resposta para verificação de permissão"""
    has_permission: bool
    reason: Optional[str] = None
