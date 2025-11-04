"""
Endpoints de Notificações In-App.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    MarkAsReadResponse,
    MarkAllAsReadResponse,
    DeleteNotificationResponse,
    NotificationStats,
    BulkNotificationCreate,
    BulkNotificationResponse
)

router = APIRouter(prefix="/notifications", tags=["Notificações"])


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_read: Optional[bool] = Query(None, description="Filtrar por lidas/não lidas"),
    type: Optional[str] = Query(None, description="Filtrar por tipo"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista notificações do usuário atual.
    
    **Filtros:**
    - is_read: true (lidas), false (não lidas), null (todas)
    - type: info, warning, success, error
    
    **Paginação:**
    - skip: Número de registros para pular
    - limit: Número máximo de registros (1-100)
    """
    
    # Query base
    query = select(Notification).where(
        and_(
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None)
        )
    )
    
    # Aplicar filtros
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)
    
    if type:
        query = query.where(Notification.type == type)
    
    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Contar não lidas
    unread_query = select(func.count(Notification.id)).where(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
            Notification.deleted_at.is_(None)
        )
    )
    unread_count = await db.scalar(unread_query) or 0
    
    # Buscar notificações
    query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return NotificationListResponse(
        notifications=notifications,
        total=total,
        unread_count=unread_count,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna estatísticas de notificações do usuário.
    """
    
    # Total
    total = await db.scalar(
        select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.deleted_at.is_(None)
            )
        )
    ) or 0
    
    # Não lidas
    unread = await db.scalar(
        select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False,
                Notification.deleted_at.is_(None)
            )
        )
    ) or 0
    
    # Por tipo
    by_type = {}
    for notification_type in ['info', 'warning', 'success', 'error']:
        count = await db.scalar(
            select(func.count(Notification.id)).where(
                and_(
                    Notification.user_id == current_user.id,
                    Notification.type == notification_type,
                    Notification.deleted_at.is_(None)
                )
            )
        ) or 0
        by_type[notification_type] = count
    
    return NotificationStats(
        total=total,
        unread=unread,
        by_type=by_type
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém uma notificação específica.
    """
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
                Notification.deleted_at.is_(None)
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    return notification


@router.put("/{notification_id}/read", response_model=MarkAsReadResponse)
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Marca uma notificação como lida.
    """
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
                Notification.deleted_at.is_(None)
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    # Marcar como lida
    notification.mark_as_read()
    await db.commit()
    await db.refresh(notification)
    
    return MarkAsReadResponse(
        id=notification.id,
        is_read=notification.is_read,
        read_at=notification.read_at
    )


@router.put("/mark-all-read", response_model=MarkAllAsReadResponse)
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Marca todas as notificações não lidas como lidas.
    """
    
    # Buscar todas as não lidas
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False,
                Notification.deleted_at.is_(None)
            )
        )
    )
    notifications = result.scalars().all()
    
    # Marcar todas como lidas
    count = 0
    for notification in notifications:
        notification.mark_as_read()
        count += 1
    
    await db.commit()
    
    return MarkAllAsReadResponse(count=count)


@router.delete("/{notification_id}", response_model=DeleteNotificationResponse)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deleta uma notificação (soft delete).
    """
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
                Notification.deleted_at.is_(None)
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    # Soft delete
    notification.deleted_at = datetime.utcnow()
    await db.commit()
    
    return DeleteNotificationResponse(id=notification.id)


# ============================================================================
# ENDPOINTS ADMINISTRATIVOS
# ============================================================================

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria uma nova notificação.
    
    **Requer:** Permissão notifications.create ou system_admin
    """
    
    # Verificar se usuário destinatário existe
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == notification_data.user_id,
                User.deleted_at.is_(None)
            )
        )
    )
    if not user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário destinatário não encontrado"
        )
    
    # Criar notificação
    notification = Notification(
        user_id=notification_data.user_id,
        type=notification_data.type,
        title=notification_data.title,
        message=notification_data.message,
        link=notification_data.link
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification


@router.post("/bulk", response_model=BulkNotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_bulk_notifications(
    bulk_data: BulkNotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria notificações em massa para múltiplos usuários.
    
    **Requer:** Permissão notifications.create ou system_admin
    """
    
    notification_ids = []
    
    for user_id in bulk_data.user_ids:
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
            continue  # Pular usuários inexistentes
        
        # Criar notificação
        notification = Notification(
            user_id=user_id,
            type=bulk_data.type,
            title=bulk_data.title,
            message=bulk_data.message,
            link=bulk_data.link
        )
        
        db.add(notification)
        await db.flush()
        notification_ids.append(notification.id)
    
    await db.commit()
    
    return BulkNotificationResponse(
        count=len(notification_ids),
        notification_ids=notification_ids
    )
