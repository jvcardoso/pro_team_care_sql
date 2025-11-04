"""
Endpoints de Dashboard.

Fornece estatísticas e atividade recente do sistema.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.company import Company
from app.models.establishment import Establishment
from app.models.role import Role
from app.models.notification import Notification
from app.models.session import UserSession
from app.schemas.dashboard import (
    DashboardStats,
    StatsResponse,
    EntityStats,
    RecentActivityResponse,
    ActivityLog,
    DashboardSummary,
    QuickStat
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=StatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna estatísticas gerais do sistema.
    
    **Estatísticas incluídas:**
    - Usuários (total, ativos, inativos)
    - Empresas (total, ativos, inativos)
    - Estabelecimentos (total, ativos, inativos)
    - Roles (contagem por tipo)
    - Notificações (total, não lidas)
    - Sessões ativas
    """
    
    # Estatísticas de Usuários
    users_total = (await db.scalar(
        select(func.count(User.id)).where(User.deleted_at.is_(None))
    )) or 0
    users_active = (await db.scalar(
        select(func.count(User.id)).where(
            and_(User.is_active, User.deleted_at.is_(None))
        )
    )) or 0
    users_inactive = users_total - users_active

    # Estatísticas de Empresas
    companies_total = (await db.scalar(
        select(func.count(Company.id)).where(Company.deleted_at.is_(None))
    )) or 0
    companies_active = (await db.scalar(
        select(func.count(Company.id)).where(
            and_(Company.access_status == 'active', Company.deleted_at.is_(None))
        )
    )) or 0
    companies_inactive = companies_total - companies_active

    # Estatísticas de Estabelecimentos
    establishments_total = (await db.scalar(
        select(func.count(Establishment.id)).where(Establishment.deleted_at.is_(None))
    )) or 0
    establishments_active = (await db.scalar(
        select(func.count(Establishment.id)).where(
            and_(Establishment.is_active, Establishment.deleted_at.is_(None))
        )
    )) or 0
    establishments_inactive = establishments_total - establishments_active

    # Estatísticas de Roles
    roles_total = (await db.scalar(
        select(func.count(Role.id)).where(Role.deleted_at.is_(None))
    )) or 0
    roles_active = (await db.scalar(
        select(func.count(Role.id)).where(
            and_(Role.is_active, Role.deleted_at.is_(None))
        )
    )) or 0
    
    # Estatísticas de Notificações
    notifications_total = (await db.scalar(
        select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.deleted_at.is_(None)
            )
        )
    )) or 0
    notifications_unread = (await db.scalar(
        select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False,
                Notification.deleted_at.is_(None)
            )
        )
    )) or 0

    # Estatísticas de Sessões (simplificado)
    sessions_active = (await db.scalar(
        select(func.count(UserSession.id)).where(
            UserSession.expires_at > datetime.utcnow()
        )
    )) or 0

    # Construir resposta
    stats = DashboardStats(
        users=EntityStats(
            total=users_total,
            active=users_active,
            inactive=users_inactive
        ),
        companies=EntityStats(
            total=companies_total,
            active=companies_active,
            inactive=companies_inactive
        ),
        establishments=EntityStats(
            total=establishments_total,
            active=establishments_active,
            inactive=establishments_inactive
        ),
        roles={
            "total": roles_total,
            "active": roles_active,
            "inactive": roles_total - roles_active
        },
        notifications={
            "total": notifications_total,
            "unread": notifications_unread
        },
        sessions={
            "active": sessions_active
        }
    )

    return StatsResponse(
        stats=stats,
        user_id=current_user.id,
        user_context="company" if current_user.company_id else "system"
    )
