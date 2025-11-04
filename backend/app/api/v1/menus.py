"""
Endpoints de Menus Dinâmicos.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.permissions import get_user_permissions
from app.models.user import User
from app.models.menu import MenuItem
from app.models.permission import Permission
from app.schemas.menu import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemResponse,
    MenuItemWithPermissions,
    MenuItemNested,
    DynamicMenuResponse,
    MenuPermissionCreate,
    MenuPermissionResponse,
    MenuListResponse,
    MenuTreeResponse,
    PermissionSimple
)

router = APIRouter(prefix="/menus", tags=["Menus Dinâmicos"])


# ============================================================================
# ENDPOINTS DE LISTAGEM
# ============================================================================

@router.get("/", response_model=MenuListResponse)
async def list_menus(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    parent_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todos os menus do sistema.
    
    **Filtros:**
    - is_active: true (ativos), false (inativos), null (todos)
    - parent_id: ID do menu pai (null para menus raiz)
    """
    
    query = select(MenuItem).where(MenuItem.deleted_at.is_(None))
    
    # Aplicar filtros
    if is_active is not None:
        query = query.where(MenuItem.is_active == is_active)
    
    if parent_id is not None:
        query = query.where(MenuItem.parent_id == parent_id)
    elif parent_id == 0:  # Buscar apenas raiz
        query = query.where(MenuItem.parent_id.is_(None))
    
    # Contar total
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Buscar menus
    query = query.order_by(MenuItem.display_order).offset(skip).limit(limit)
    result = await db.execute(query)
    menus = result.scalars().all()
    
    return MenuListResponse(
        menus=menus,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/tree", response_model=MenuTreeResponse)
async def get_menu_tree(
    include_inactive: bool = Query(False, description="Incluir menus inativos"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna árvore completa de menus com hierarquia.
    """
    
    # Buscar todos os menus
    query = select(MenuItem).where(MenuItem.deleted_at.is_(None))
    
    if not include_inactive:
        query = query.where(MenuItem.is_active == True)
    
    query = query.options(selectinload(MenuItem.permissions))
    query = query.order_by(MenuItem.display_order)
    
    result = await db.execute(query)
    all_menus = result.scalars().all()
    
    # Construir árvore
    menu_dict = {menu.id: menu for menu in all_menus}
    root_menus = []
    
    def build_menu_tree(menu: MenuItem) -> MenuItemNested:
        """Constrói recursivamente a árvore de menus"""
        children = [
            build_menu_tree(child)
            for child in all_menus
            if child.parent_id == menu.id
        ]
        
        permissions = [
            PermissionSimple(
                id=perm.id,
                name=perm.name,
                display_name=perm.display_name
            )
            for perm in menu.permissions
        ]
        
        return MenuItemNested(
            id=menu.id,
            parent_id=menu.parent_id,
            name=menu.name,
            label=menu.label,
            icon=menu.icon,
            path=menu.path,
            display_order=menu.display_order,
            is_active=menu.is_active,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
            deleted_at=menu.deleted_at,
            children=children,
            permissions=permissions,
            has_children=len(children) > 0,
            is_root=menu.parent_id is None
        )
    
    # Construir árvore a partir dos menus raiz
    for menu in all_menus:
        if menu.parent_id is None:
            root_menus.append(build_menu_tree(menu))
    
    return MenuTreeResponse(
        tree=root_menus,
        total_items=len(all_menus),
        total_root_items=len(root_menus)
    )


@router.get("/dynamic", response_model=DynamicMenuResponse)
async def get_dynamic_menus(
    include_inactive: bool = Query(False, description="Incluir menus inativos"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna menus dinâmicos baseados nas permissões do usuário atual.

    Usa o stored procedure [core].[sp_get_dynamic_menus] para obter os menus visíveis.
    """
    try:
        # Chamar o stored procedure
        query = text("""
            EXEC [core].[sp_get_dynamic_menus] @user_id_input = :user_id
        """)

        result = await db.execute(query, {"user_id": current_user.id})
        rows = result.fetchall()

        # Usar permissões básicas para evitar conflito de conexão
        user_permissions = ["dashboard.view"] if not current_user.is_system_admin else ["*"]

        # Organizar menus por hierarquia
        menu_dict = {}
        root_menus = []

        for row in rows:
            menu_dict[row.id] = {
                "id": row.id,
                "parent_id": row.parent_id,
                "name": row.name,
                "label": row.label,
                "icon": row.icon,
                "path": row.path,
                "display_order": row.display_order,
                "is_active": True,
                "children": [],
                "permissions": [],
                "has_children": False,
                "is_root": row.parent_id is None
            }

        # Construir hierarquia
        for menu_id, menu_data in menu_dict.items():
            if menu_data["parent_id"] is None:
                root_menus.append(menu_data)
            else:
                parent_id = menu_data["parent_id"]
                if parent_id in menu_dict:
                    menu_dict[parent_id]["children"].append(menu_data)
                    menu_dict[parent_id]["has_children"] = True

        # Ordenar filhos por display_order
        for menu_data in menu_dict.values():
            menu_data["children"].sort(key=lambda x: x["display_order"])

        # Ordenar menus raiz
        root_menus.sort(key=lambda x: x["display_order"])

        # Função recursiva para converter
        def to_nested(menu_data):
            return MenuItemNested(
                id=menu_data["id"],
                parent_id=menu_data["parent_id"],
                name=menu_data["name"],
                label=menu_data["label"],
                icon=menu_data["icon"],
                path=menu_data["path"],
                display_order=menu_data["display_order"],
                is_active=menu_data["is_active"],
                children=[to_nested(child) for child in menu_data["children"]],
                permissions=[],
                has_children=menu_data["has_children"],
                is_root=menu_data["is_root"]
            )

        nested_menus = [to_nested(menu) for menu in root_menus]

        return DynamicMenuResponse(
            menus=nested_menus,
            total_menus=len(rows),
            user_id=current_user.id,
            user_permissions=list(user_permissions)
        )

    except Exception as e:
        print(f"Erro no stored procedure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar menus dinâmicos: {str(e)}"
        )
    
    return DynamicMenuResponse(
        menus=root_menus,
        total_menus=len(visible_menus),
        user_id=current_user.id,
        user_permissions=list(user_permissions)
    )


# ============================================================================
# ENDPOINTS DE CRUD
# ============================================================================

@router.get("/{menu_id}", response_model=MenuItemWithPermissions)
async def get_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém um menu específico com suas permissões.
    """
    
    result = await db.execute(
        select(MenuItem).where(
            and_(
                MenuItem.id == menu_id,
                MenuItem.deleted_at.is_(None)
            )
        ).options(selectinload(MenuItem.permissions))
    )
    menu = result.scalar_one_or_none()
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu não encontrado"
        )
    
    permissions = [
        PermissionSimple(
            id=perm.id,
            name=perm.name,
            display_name=perm.display_name
        )
        for perm in menu.permissions
    ]
    
    return MenuItemWithPermissions(
        id=menu.id,
        parent_id=menu.parent_id,
        name=menu.name,
        label=menu.label,
        icon=menu.icon,
        path=menu.path,
        display_order=menu.display_order,
        is_active=menu.is_active,
        created_at=menu.created_at,
        updated_at=menu.updated_at,
        deleted_at=menu.deleted_at,
        permissions=permissions
    )


@router.post("/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu(
    menu_data: MenuItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria um novo menu.
    
    **Requer:** Permissão menus.create ou system_admin
    """
    
    # Verificar se nome já existe
    existing = await db.execute(
        select(MenuItem).where(
            and_(
                MenuItem.name == menu_data.name,
                MenuItem.deleted_at.is_(None)
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Menu com nome '{menu_data.name}' já existe"
        )
    
    # Verificar se parent_id existe (se fornecido)
    if menu_data.parent_id:
        parent_result = await db.execute(
            select(MenuItem).where(
                and_(
                    MenuItem.id == menu_data.parent_id,
                    MenuItem.deleted_at.is_(None)
                )
            )
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu pai não encontrado"
            )
    
    # Criar menu
    menu = MenuItem(
        parent_id=menu_data.parent_id,
        name=menu_data.name,
        label=menu_data.label,
        icon=menu_data.icon,
        path=menu_data.path,
        display_order=menu_data.display_order,
        is_active=menu_data.is_active
    )
    
    db.add(menu)
    await db.flush()
    
    # Associar permissões (se fornecidas)
    if menu_data.permission_ids:
        for permission_id in menu_data.permission_ids:
            permission = await db.get(Permission, permission_id)
            if permission:
                menu.permissions.append(permission)
    
    await db.commit()
    await db.refresh(menu)
    
    return menu


@router.put("/{menu_id}", response_model=MenuItemResponse)
async def update_menu(
    menu_id: int,
    menu_data: MenuItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza um menu existente.
    
    **Requer:** Permissão menus.update ou system_admin
    """
    
    result = await db.execute(
        select(MenuItem).where(
            and_(
                MenuItem.id == menu_id,
                MenuItem.deleted_at.is_(None)
            )
        )
    )
    menu = result.scalar_one_or_none()
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu não encontrado"
        )
    
    # Atualizar campos fornecidos
    update_data = menu_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu, field, value)
    
    menu.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(menu)
    
    return menu


@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deleta um menu (soft delete).
    
    **Requer:** Permissão menus.delete ou system_admin
    **Nota:** Deleta também todos os submenus (cascade)
    """
    
    result = await db.execute(
        select(MenuItem).where(
            and_(
                MenuItem.id == menu_id,
                MenuItem.deleted_at.is_(None)
            )
        )
    )
    menu = result.scalar_one_or_none()
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu não encontrado"
        )
    
    # Soft delete
    from datetime import datetime
    menu.deleted_at = datetime.utcnow()
    
    # Soft delete dos filhos também
    children_result = await db.execute(
        select(MenuItem).where(
            and_(
                MenuItem.parent_id == menu_id,
                MenuItem.deleted_at.is_(None)
            )
        )
    )
    children = children_result.scalars().all()
    
    for child in children:
        child.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return None


# ============================================================================
# ENDPOINTS DE PERMISSÕES
# ============================================================================

@router.put("/{menu_id}/permissions", response_model=MenuPermissionResponse)
async def update_menu_permissions(
    menu_id: int,
    permissions_data: MenuPermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza as permissões de um menu.
    
    **Requer:** Permissão menus.manage ou system_admin
    **Nota:** Substitui todas as permissões existentes pelas fornecidas
    """
    
    result = await db.execute(
        select(MenuItem).where(
            and_(
                MenuItem.id == menu_id,
                MenuItem.deleted_at.is_(None)
            )
        ).options(selectinload(MenuItem.permissions))
    )
    menu = result.scalar_one_or_none()
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu não encontrado"
        )
    
    # Limpar permissões existentes
    menu.permissions.clear()
    
    # Adicionar novas permissões
    for permission_id in permissions_data.permission_ids:
        permission = await db.get(Permission, permission_id)
        if permission:
            menu.permissions.append(permission)
    
    await db.commit()
    await db.refresh(menu)
    
    permissions = [
        PermissionSimple(
            id=perm.id,
            name=perm.name,
            display_name=perm.display_name
        )
        for perm in menu.permissions
    ]
    
    return MenuPermissionResponse(
        menu_id=menu.id,
        menu_name=menu.name,
        permissions=permissions,
        count=len(permissions)
    )
