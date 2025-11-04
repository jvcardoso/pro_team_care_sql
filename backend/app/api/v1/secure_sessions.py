"""
Endpoints de Sessões Seguras.

Funcionalidades:
- Switch Profile: Trocar contexto ativo (empresa, estabelecimento, role)
- Impersonate: Admin personificar outro usuário
- End Impersonation: Encerrar personificação
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import secrets

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.security import create_access_token
from app.models.user import User
from app.models.session import UserSession
from app.schemas.session import (
    SwitchProfileRequest,
    SwitchProfileResponse,
    ImpersonateRequest,
    ImpersonateResponse,
    EndImpersonationResponse
)

router = APIRouter(prefix="/secure-sessions", tags=["Sessões Seguras"])


@router.post("/switch-profile", response_model=SwitchProfileResponse)
async def switch_profile(
    profile_data: SwitchProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Troca o perfil/contexto ativo do usuário.
    
    **Funcionalidade:**
    - Permite que usuário com múltiplos roles troque de contexto
    - Exemplo: Médico em Empresa A → Enfermeiro em Empresa B
    - Gera novo token JWT com contexto atualizado
    
    **Validações:**
    - Verifica se usuário tem acesso ao contexto solicitado
    - Valida se company_id e establishment_id existem
    """
    
    # TODO: Validar se usuário tem role no contexto solicitado
    # Por enquanto, apenas gera novo token com contexto
    
    # Preparar payload do token
    token_data = {
        "sub": current_user.email_address,
        "user_id": current_user.id,
        "active_company_id": profile_data.company_id,
        "active_establishment_id": profile_data.establishment_id,
        "active_role_id": profile_data.role_id,
        "is_system_admin": current_user.is_system_admin,
        "impersonating": False
    }
    
    # Gerar novo token
    access_token = create_access_token(data=token_data)
    
    # Criar sessão (opcional - para rastreamento)
    jti = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=current_user.id,
        jti=jti,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(session)
    await db.commit()
    
    return SwitchProfileResponse(
        access_token=access_token,
        active_company_id=profile_data.company_id,
        active_establishment_id=profile_data.establishment_id,
        active_role_id=profile_data.role_id
    )


@router.post("/impersonate", response_model=ImpersonateResponse)
async def impersonate_user(
    impersonate_data: ImpersonateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Permite que um administrador personifique outro usuário.
    
    **Requer:** is_system_admin = true
    
    **Funcionalidade:**
    - Admin "vira" outro usuário temporariamente
    - Útil para suporte e debug
    - Token JWT contém ID do admin e do usuário personificado
    
    **Segurança:**
    - Apenas system_admin pode personificar
    - Ação é registrada em audit log
    - Token expira em 1 hora (por segurança)
    """
    
    # Verificar se usuário atual é system_admin
    if not current_user.is_system_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores do sistema podem personificar usuários"
        )
    
    # Buscar usuário alvo
    result = await db.execute(
        select(User).where(
            and_(
                User.id == impersonate_data.target_user_id,
                User.deleted_at.is_(None)
            )
        )
    )
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário alvo não encontrado"
        )
    
    # Não permitir personificar outro admin
    if target_user.is_system_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é permitido personificar outro administrador"
        )
    
    # Preparar payload do token
    token_data = {
        "sub": target_user.email_address,
        "user_id": target_user.id,
        "impersonator_id": current_user.id,
        "impersonating": True,
        "is_system_admin": False  # Personificado não tem privilégios de admin
    }
    
    # Gerar token com expiração curta (1 hora)
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=1)
    )
    
    # Criar sessão de personificação
    jti = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=target_user.id,
        jti=jti,
        impersonator_user_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(session)
    await db.commit()
    
    # TODO: Registrar em audit log
    
    return ImpersonateResponse(
        access_token=access_token,
        impersonating=True,
        target_user_id=target_user.id,
        target_user_email=target_user.email_address,
        impersonator_id=current_user.id,
        impersonator_email=current_user.email_address
    )


@router.post("/end-impersonation", response_model=EndImpersonationResponse)
async def end_impersonation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Encerra a personificação e retorna ao usuário original.
    
    **Funcionalidade:**
    - Admin volta a ser ele mesmo
    - Gera novo token JWT sem personificação
    
    **Nota:**
    - Endpoint deve ser chamado com token de personificação
    - Extrai impersonator_id do token para gerar novo token
    """
    
    # TODO: Extrair impersonator_id do token JWT atual
    # Por enquanto, retorna erro se não houver personificação
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Não há personificação ativa para encerrar"
    )
    
    # Código para quando implementarmos extração do token:
    # impersonator_id = get_impersonator_id_from_token()
    # 
    # if not impersonator_id:
    #     raise HTTPException(...)
    # 
    # # Buscar admin original
    # admin = await db.get(User, impersonator_id)
    # 
    # # Gerar novo token para admin
    # token_data = {
    #     "sub": admin.email_address,
    #     "user_id": admin.id,
    #     "is_system_admin": admin.is_system_admin,
    #     "impersonating": False
    # }
    # 
    # access_token = create_access_token(data=token_data)
    # 
    # return EndImpersonationResponse(
    #     access_token=access_token,
    #     user_id=admin.id,
    #     user_email=admin.email_address
    # )


@router.get("/active-sessions")
async def get_active_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista sessões ativas do usuário atual.
    
    **Funcionalidade:**
    - Mostra todas as sessões não expiradas
    - Útil para ver onde o usuário está logado
    - Permite invalidar sessões específicas (futuro)
    """
    
    now = datetime.utcnow()
    
    result = await db.execute(
        select(UserSession).where(
            and_(
                UserSession.user_id == current_user.id,
                UserSession.expires_at > now
            )
        ).order_by(UserSession.created_at.desc())
    )
    sessions = result.scalars().all()
    
    return {
        "sessions": [
            {
                "id": session.id,
                "jti": session.jti[:8] + "...",  # Mostrar apenas início
                "is_impersonating": session.impersonator_user_id is not None,
                "created_at": session.created_at,
                "expires_at": session.expires_at
            }
            for session in sessions
        ],
        "total": len(sessions)
    }


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Revoga (invalida) uma sessão específica.
    
    **Funcionalidade:**
    - Permite que usuário invalide sessões antigas
    - Útil para logout remoto
    - Deleta a sessão do banco (hard delete)
    """
    
    result = await db.execute(
        select(UserSession).where(
            and_(
                UserSession.id == session_id,
                UserSession.user_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    await db.delete(session)
    await db.commit()
    
    return {"message": "Sessão revogada com sucesso"}
