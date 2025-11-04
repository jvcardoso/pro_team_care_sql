"""
Schemas Pydantic para Menus Dinâmicos.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# SCHEMAS BASE
# ============================================================================

class MenuItemBase(BaseModel):
    """Schema base para itens de menu"""
    name: str = Field(..., max_length=100, description="Identificador único")
    label: str = Field(..., max_length=200, description="Texto exibido")
    icon: Optional[str] = Field(None, max_length=50, description="Nome do ícone")
    path: Optional[str] = Field(None, max_length=500, description="Rota/URL")
    display_order: int = Field(0, description="Ordem de exibição")
    is_active: bool = Field(True, description="Menu ativo/inativo")


class MenuItemCreate(MenuItemBase):
    """Schema para criar item de menu"""
    parent_id: Optional[int] = Field(None, description="ID do menu pai")
    permission_ids: Optional[List[int]] = Field(None, description="IDs das permissões necessárias")


class MenuItemUpdate(BaseModel):
    """Schema para atualizar item de menu"""
    label: Optional[str] = Field(None, max_length=200)
    icon: Optional[str] = Field(None, max_length=50)
    path: Optional[str] = Field(None, max_length=500)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None


class MenuItemResponse(MenuItemBase):
    """Schema de resposta de item de menu"""
    id: int
    parent_id: Optional[int]

    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS COM RELACIONAMENTOS
# ============================================================================

class PermissionSimple(BaseModel):
    """Schema simplificado de permissão"""
    id: int
    name: str
    display_name: str

    class Config:
        from_attributes = True


class MenuItemWithPermissions(MenuItemResponse):
    """Schema de menu com permissões"""
    permissions: List[PermissionSimple] = []


class MenuItemNested(MenuItemResponse):
    """Schema de menu com hierarquia (recursivo)"""
    children: List['MenuItemNested'] = []
    permissions: List[PermissionSimple] = []
    has_children: bool = False
    is_root: bool = True


# Atualizar forward reference
MenuItemNested.model_rebuild()


# ============================================================================
# SCHEMAS DE MENUS DINÂMICOS
# ============================================================================

class DynamicMenuRequest(BaseModel):
    """Schema de requisição para menus dinâmicos"""
    user_id: Optional[int] = Field(None, description="ID do usuário (opcional, usa current_user se não fornecido)")
    include_inactive: bool = Field(False, description="Incluir menus inativos")


class DynamicMenuResponse(BaseModel):
    """Schema de resposta para menus dinâmicos"""
    menus: List[MenuItemNested]
    total_menus: int
    user_id: int
    user_permissions: List[str] = Field(..., description="Permissões do usuário")


# ============================================================================
# SCHEMAS DE PERMISSÕES DE MENU
# ============================================================================

class MenuPermissionCreate(BaseModel):
    """Schema para associar permissões a um menu"""
    permission_ids: List[int] = Field(..., description="IDs das permissões")


class MenuPermissionResponse(BaseModel):
    """Schema de resposta de permissões de menu"""
    menu_id: int
    menu_name: str
    permissions: List[PermissionSimple]
    count: int = Field(..., description="Número de permissões")


# ============================================================================
# SCHEMAS DE LISTAGEM
# ============================================================================

class MenuListResponse(BaseModel):
    """Schema de resposta para lista de menus"""
    menus: List[MenuItemResponse]
    total: int
    page: int
    page_size: int


class MenuTreeResponse(BaseModel):
    """Schema de resposta para árvore de menus"""
    tree: List[MenuItemNested]
    total_items: int
    total_root_items: int


# ============================================================================
# SCHEMAS DE REORDENAÇÃO
# ============================================================================

class MenuReorderItem(BaseModel):
    """Schema para item de reordenação"""
    id: int
    display_order: int


class MenuReorderRequest(BaseModel):
    """Schema para reordenar menus"""
    items: List[MenuReorderItem] = Field(..., description="Lista de menus com nova ordem")


class MenuReorderResponse(BaseModel):
    """Schema de resposta de reordenação"""
    count: int = Field(..., description="Número de menus reordenados")
    message: str = "Menus reordenados com sucesso"


# ============================================================================
# SCHEMAS DE VALIDAÇÃO
# ============================================================================

class MenuValidationResponse(BaseModel):
    """Schema de resposta de validação de menu"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
