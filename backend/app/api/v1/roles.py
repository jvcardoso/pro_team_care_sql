"""
Endpoints de Roles e Permissões (RBAC).

Sistema de controle de acesso baseado em roles.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission, RolePermission, UserRole
from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissions,
    PermissionResponse,
    RolePermissionCreate,
    UserRoleCreate,
    UserRoleResponse,
    UserRoleWithDetails,
    BulkUserRoleCreate,
    BulkUserRoleResponse,
    PermissionCheckRequest,
    PermissionCheckResponse
)

router = APIRouter(prefix="/roles", tags=["Roles e Permissões"])


# ============================================================================
# ROLES ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    context_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todos os roles do sistema.
    
    **Filtros:**
    - is_active: Filtrar por status ativo/inativo
    - context_type: Filtrar por tipo de contexto (system, company, establishment)
    
    **Paginação:**
    - skip: Número de registros para pular
    - limit: Número máximo de registros (máx: 1000)
    """
    query = select(Role).where(Role.deleted_at.is_(None))
    
    # Aplicar filtros
    if is_active is not None:
        query = query.where(Role.is_active == is_active)
    
    if context_type:
        query = query.where(Role.context_type == context_type)
    
    # Ordenar e paginar
    query = query.order_by(Role.level, Role.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    roles = result.scalars().all()
    
    return roles


@router.get("/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém detalhes de um role específico, incluindo suas permissões.
    """
    # Buscar role
    query = select(Role).where(
        and_(
            Role.id == role_id,
            Role.deleted_at.is_(None)
        )
    )
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    # Buscar permissões do role
    permissions_query = text("""
        SELECT p.*
        FROM [core].[permissions] p
        INNER JOIN [core].[role_permissions] rp ON rp.permission_id = p.id
        WHERE rp.role_id = :role_id
          AND p.deleted_at IS NULL
        ORDER BY p.resource, p.action
    """)
    
    permissions_result = await db.execute(permissions_query, {"role_id": role_id})
    permissions = [
        PermissionResponse(
            id=row.id,
            name=row.name,
            display_name=row.display_name,
            description=row.description,
            resource=row.resource,
            action=row.action,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        for row in permissions_result.fetchall()
    ]
    
    # Montar resposta
    role_dict = {
        "id": role.id,
        "name": role.name,
        "display_name": role.display_name,
        "description": role.description,
        "level": role.level,
        "context_type": role.context_type,
        "is_active": role.is_active,
        "is_system_role": role.is_system_role,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "deleted_at": role.deleted_at,
        "permissions": permissions
    }
    
    return role_dict


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria um novo role.
    
    **Requer:** Permissão roles.create ou system_admin
    """
    # Verificar se nome já existe
    existing = await db.execute(
        select(Role).where(
            and_(
                Role.name == role_data.name,
                Role.deleted_at.is_(None)
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role com nome '{role_data.name}' já existe"
        )
    
    # Criar role
    new_role = Role(
        name=role_data.name,
        display_name=role_data.display_name,
        description=role_data.description,
        level=role_data.level,
        context_type=role_data.context_type,
        is_active=role_data.is_active,
        is_system_role=role_data.is_system_role
    )
    
    db.add(new_role)
    await db.flush()
    
    # Associar permissões se fornecidas
    if role_data.permission_ids:
        for permission_id in role_data.permission_ids:
            role_permission = RolePermission(
                role_id=new_role.id,
                permission_id=permission_id
            )
            db.add(role_permission)
    
    await db.commit()
    await db.refresh(new_role)
    
    return new_role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza um role existente.
    
    **Requer:** Permissão roles.update ou system_admin
    **Nota:** Roles do sistema (is_system_role=true) têm restrições de edição
    """
    # Buscar role
    result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.deleted_at.is_(None)
            )
        )
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    # Atualizar campos fornecidos
    update_data = role_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)
    
    await db.commit()
    await db.refresh(role)
    
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deleta um role (soft delete).
    
    **Requer:** Permissão roles.delete ou system_admin
    **Nota:** Roles do sistema (is_system_role=true) não podem ser deletados
    """
    # Buscar role
    result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.deleted_at.is_(None)
            )
        )
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    # Verificar se é role do sistema
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Roles do sistema não podem ser deletados"
        )
    
    # Soft delete
    from datetime import datetime
    role.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return None


# ============================================================================
# ROLE PERMISSIONS ENDPOINTS
# ============================================================================

@router.get("/{role_id}/permissions", response_model=List[PermissionResponse])
async def get_role_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todas as permissões de um role.
    """
    # Verificar se role existe
    role_result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.deleted_at.is_(None)
            )
        )
    )
    if not role_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    # Buscar permissões
    query = text("""
        SELECT p.*
        FROM [core].[permissions] p
        INNER JOIN [core].[role_permissions] rp ON rp.permission_id = p.id
        WHERE rp.role_id = :role_id
          AND p.deleted_at IS NULL
        ORDER BY p.resource, p.action
    """)
    
    result = await db.execute(query, {"role_id": role_id})
    permissions = [
        PermissionResponse(
            id=row.id,
            name=row.name,
            display_name=row.display_name,
            description=row.description,
            resource=row.resource,
            action=row.action,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        for row in result.fetchall()
    ]
    
    return permissions


@router.put("/{role_id}/permissions")
async def update_role_permissions(
    role_id: int,
    permissions_data: RolePermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza as permissões de um role.
    
    **Requer:** Permissão roles.manage ou system_admin
    **Nota:** Substitui todas as permissões existentes pelas fornecidas
    """
    # Verificar se role existe
    role_result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.deleted_at.is_(None)
            )
        )
    )
    role = role_result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    # Remover permissões existentes
    await db.execute(
        text("DELETE FROM [core].[role_permissions] WHERE role_id = :role_id"),
        {"role_id": role_id}
    )
    
    # Adicionar novas permissões
    for permission_id in permissions_data.permission_ids:
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id
        )
        db.add(role_permission)
    
    await db.commit()
    
    return {
        "success": True,
        "message": f"{len(permissions_data.permission_ids)} permissões atualizadas"
    }


# ============================================================================
# USER ROLES ENDPOINTS
# ============================================================================

@router.get("/users/{user_id}/roles", response_model=List[UserRoleWithDetails])
async def get_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todos os roles de um usuário.
    """
    query = text("""
        SELECT 
            ur.*,
            r.name as role_name,
            r.display_name as role_display_name,
            r.description as role_description,
            r.level as role_level,
            r.context_type as role_context_type,
            r.is_active as role_is_active,
            r.is_system_role as role_is_system_role,
            r.created_at as role_created_at,
            r.updated_at as role_updated_at
        FROM [core].[user_roles] ur
        INNER JOIN [core].[roles] r ON r.id = ur.role_id
        WHERE ur.user_id = :user_id
          AND ur.deleted_at IS NULL
          AND r.deleted_at IS NULL
        ORDER BY r.level, r.name
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    rows = result.fetchall()
    
    user_roles = []
    for row in rows:
        user_role = UserRoleWithDetails(
            id=row.id,
            user_id=row.user_id,
            role_id=row.role_id,
            context_type=row.context_type,
            context_id=row.context_id,
            status=row.status,
            expires_at=row.expires_at,
            assigned_by_user_id=row.assigned_by_user_id,
            assigned_at=row.assigned_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
            role=RoleResponse(
                id=row.role_id,
                name=row.role_name,
                display_name=row.role_display_name,
                description=row.role_description,
                level=row.role_level,
                context_type=row.role_context_type,
                is_active=row.role_is_active,
                is_system_role=row.role_is_system_role,
                created_at=row.role_created_at,
                updated_at=row.role_updated_at,
                deleted_at=None
            )
        )
        user_roles.append(user_role)
    
    return user_roles


@router.post("/users/{user_id}/roles", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    user_id: int,
    role_data: UserRoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atribui um role a um usuário.
    
    **Requer:** Permissão users.update ou system_admin
    """
    # Verificar se usuário existe
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.deleted_at.is_(None)
            )
        )
    )
    if not user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar se role existe
    role_result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_data.role_id,
                Role.deleted_at.is_(None)
            )
        )
    )
    if not role_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    # Verificar se já existe
    existing = await db.execute(
        select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_data.role_id,
                UserRole.deleted_at.is_(None)
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já possui este role"
        )
    
    # Criar user_role
    user_role = UserRole(
        user_id=user_id,
        role_id=role_data.role_id,
        context_type=role_data.context_type,
        context_id=role_data.context_id,
        expires_at=role_data.expires_at,
        assigned_by_user_id=current_user.id
    )
    
    db.add(user_role)
    await db.commit()
    await db.refresh(user_role)
    
    return user_role


@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove um role de um usuário (soft delete).
    
    **Requer:** Permissão users.update ou system_admin
    """
    # Buscar user_role
    result = await db.execute(
        select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.deleted_at.is_(None)
            )
        )
    )
    user_role = result.scalar_one_or_none()
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associação usuário-role não encontrada"
        )
    
    # Soft delete
    from datetime import datetime
    user_role.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return None


# ============================================================================
# PERMISSIONS ENDPOINTS
# ============================================================================

@router.get("/permissions/", response_model=List[PermissionResponse])
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todas as permissões do sistema.
    
    **Filtros:**
    - resource: Filtrar por recurso (ex: users, companies)
    - is_active: Filtrar por status ativo/inativo
    """
    query = select(Permission).where(Permission.deleted_at.is_(None))
    
    # Aplicar filtros
    if resource:
        query = query.where(Permission.resource == resource)
    
    if is_active is not None:
        query = query.where(Permission.is_active == is_active)
    
    # Ordenar e paginar
    query = query.order_by(Permission.resource, Permission.action).offset(skip).limit(limit)
    
    result = await db.execute(query)
    permissions = result.scalars().all()
    
    return permissions


@router.post("/permissions/check", response_model=PermissionCheckResponse)
async def check_permission(
    check_data: PermissionCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verifica se um usuário tem uma permissão específica.
    
    **Uso:** Validação de permissões no frontend ou em outros serviços
    """
    # Buscar permissões do usuário via roles
    query = text("""
        SELECT DISTINCT p.name
        FROM [core].[permissions] p
        INNER JOIN [core].[role_permissions] rp ON rp.permission_id = p.id
        INNER JOIN [core].[user_roles] ur ON ur.role_id = rp.role_id
        WHERE ur.user_id = :user_id
          AND ur.status = 'active'
          AND ur.deleted_at IS NULL
          AND p.is_active = 1
          AND p.deleted_at IS NULL
    """)
    
    result = await db.execute(query, {"user_id": check_data.user_id})
    user_permissions = {row.name for row in result.fetchall()}
    
    has_permission = check_data.permission_name in user_permissions
    
    return PermissionCheckResponse(
        has_permission=has_permission,
        reason=None if has_permission else "Usuário não possui esta permissão"
    )
