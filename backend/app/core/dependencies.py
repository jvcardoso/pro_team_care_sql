"""
Dependências de autenticação e autorização para FastAPI.

Este módulo contém:
- get_current_user: Valida token JWT e retorna usuário
- get_current_active_user: Verifica se usuário está ativo
- get_current_superuser: Verifica se usuário é superusuário
- get_current_user_with_company: Valida usuário e company_id (multi-tenant)
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.user import UserResponse

# ========================================
# SCHEMAS DE AUTENTICAÇÃO
# ========================================
security = HTTPBearer()


# ========================================
# DEPENDÊNCIAS DE AUTENTICAÇÃO
# ========================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependência para obter usuário atual a partir do token JWT.

    Args:
        credentials: Credenciais do header Authorization
        db: Sessão do banco de dados

    Returns:
        Instância do modelo User

    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decodificar token
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise credentials_exception

    # Extrair user_id do token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception

    # Buscar usuário no banco
    stmt = select(User).where(User.id == user_id_int)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependência para obter usuário atual ativo.

    Args:
        current_user: Usuário obtido da dependência get_current_user

    Returns:
        Instância do modelo User (ativo)

    Raises:
        HTTPException: Se usuário não estiver ativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este usuário está inativo e não pode acessar o sistema"
        )

    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependência para obter superusuário atual.

    Args:
        current_user: Usuário ativo obtido da dependência get_current_active_user

    Returns:
        Instância do modelo User (superusuário)

    Raises:
        HTTPException: Se usuário não for superusuário
    """
    if not current_user.is_system_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Requer privilégios de administrador"
        )

    return current_user


async def get_current_user_with_company(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependência para validar usuário e company_id (multi-tenant).

    Para usuários normais: company_id deve bater com o do usuário
    Para superusuários: pode acessar qualquer company_id

    Args:
        request: Requisição HTTP (para extrair company_id se necessário)
        current_user: Usuário ativo
        db: Sessão do banco

    Returns:
        Instância do modelo User

    Raises:
        HTTPException: Se company_id não autorizado
    """
    # Superusuários podem acessar tudo
    if current_user.is_system_admin:
        return current_user

    # Para usuários normais, verificar company_id
    # O company_id pode vir de:
    # 1. Header X-Company-ID
    # 2. Query parameter company_id
    # 3. Path parameter (depende da rota)

    company_id_header = request.headers.get("X-Company-ID")
    company_id_query = request.query_params.get("company_id")

    # Usar header se disponível, senão query
    requested_company_id = company_id_header or company_id_query

    if requested_company_id:
        try:
            requested_company_id_int = int(requested_company_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company ID inválido"
            )

        # Verificar se usuário pertence à empresa solicitada
        if current_user.company_id != requested_company_id_int:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Você não tem permissão para acessar esta empresa"
            )

    return current_user


# ========================================
# HELPERS PARA AUTENTICAÇÃO OPCIONAL
# ========================================

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependência opcional para obter usuário atual.
    Não lança erro se token não for fornecido ou for inválido.

    Returns:
        User ou None
    """
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def get_current_active_user_optional(
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Optional[User]:
    """
    Dependência opcional para obter usuário ativo.

    Returns:
        User ativo ou None
    """
    if current_user and current_user.is_active:
        return current_user
    return None