"""
Sistema de verificação de permissões (RBAC).

Decorators e funções auxiliares para controle de acesso.
"""
from functools import wraps
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User


async def check_user_permission(
    user: User,
    permission_name: str,
    db: AsyncSession,
    context_type: Optional[str] = None,
    context_id: Optional[int] = None
) -> bool:
    """
    Verifica se um usuário tem uma permissão específica.
    
    Args:
        user: Usuário a verificar
        permission_name: Nome da permissão (ex: users.view)
        db: Sessão do banco de dados
        context_type: Tipo de contexto (opcional)
        context_id: ID do contexto (opcional)
        
    Returns:
        True se o usuário tem a permissão, False caso contrário
    """
    # System admin tem todas as permissões
    if user.is_system_admin:
        return True
    
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
          AND p.name = :permission_name
    """)
    
    result = await db.execute(query, {
        "user_id": user.id,
        "permission_name": permission_name
    })
    
    return result.fetchone() is not None


async def check_user_permissions(
    user: User,
    permission_names: List[str],
    db: AsyncSession,
    require_all: bool = True
) -> bool:
    """
    Verifica se um usuário tem múltiplas permissões.
    
    Args:
        user: Usuário a verificar
        permission_names: Lista de nomes de permissões
        db: Sessão do banco de dados
        require_all: Se True, requer todas as permissões. Se False, requer pelo menos uma.
        
    Returns:
        True se o usuário atende aos requisitos, False caso contrário
    """
    # System admin tem todas as permissões
    if user.is_system_admin:
        return True
    
    # Verificar cada permissão
    checks = []
    for permission_name in permission_names:
        has_permission = await check_user_permission(user, permission_name, db)
        checks.append(has_permission)
    
    if require_all:
        return all(checks)
    else:
        return any(checks)


async def get_user_permissions(
    user: User,
    db: AsyncSession
) -> List[str]:
    """
    Retorna lista de todas as permissões de um usuário.
    
    Args:
        user: Usuário
        db: Sessão do banco de dados
        
    Returns:
        Lista de nomes de permissões
    """
    # System admin tem todas as permissões
    if user.is_system_admin:
        query = text("""
            SELECT name
            FROM [core].[permissions]
            WHERE is_active = 1
              AND deleted_at IS NULL
            ORDER BY resource, action
        """)
        result = await db.execute(query)
        return [row.name for row in result.fetchall()]
    
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
        ORDER BY p.resource, p.action
    """)
    
    result = await db.execute(query, {"user_id": user.id})
    return [row.name for row in result.fetchall()]


def require_permission(permission_name: str):
    """
    Decorator para exigir uma permissão específica.
    
    Uso:
        @router.get("/users")
        @require_permission("users.view")
        async def list_users(...):
            ...
    
    Args:
        permission_name: Nome da permissão requerida (ex: users.view)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair dependências
            current_user = kwargs.get("current_user")
            db = kwargs.get("db")
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro interno: dependências não encontradas"
                )
            
            # Verificar permissão
            has_permission = await check_user_permission(
                user=current_user,
                permission_name=permission_name,
                db=db
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão negada: {permission_name} requerida"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*permission_names: str):
    """
    Decorator para exigir pelo menos uma das permissões listadas.
    
    Uso:
        @router.get("/dashboard")
        @require_any_permission("dashboard.view", "admin.access")
        async def view_dashboard(...):
            ...
    
    Args:
        permission_names: Nomes das permissões (pelo menos uma requerida)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair dependências
            current_user = kwargs.get("current_user")
            db = kwargs.get("db")
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro interno: dependências não encontradas"
                )
            
            # Verificar permissões
            has_permission = await check_user_permissions(
                user=current_user,
                permission_names=list(permission_names),
                db=db,
                require_all=False
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão negada: uma das seguintes é requerida: {', '.join(permission_names)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_all_permissions(*permission_names: str):
    """
    Decorator para exigir todas as permissões listadas.
    
    Uso:
        @router.post("/sensitive-operation")
        @require_all_permissions("admin.access", "sensitive.execute")
        async def sensitive_operation(...):
            ...
    
    Args:
        permission_names: Nomes das permissões (todas requeridas)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair dependências
            current_user = kwargs.get("current_user")
            db = kwargs.get("db")
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro interno: dependências não encontradas"
                )
            
            # Verificar permissões
            has_permission = await check_user_permissions(
                user=current_user,
                permission_names=list(permission_names),
                db=db,
                require_all=True
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão negada: todas as seguintes são requeridas: {', '.join(permission_names)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
