"""
Schemas Pydantic para Notificações.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class NotificationType(str, Enum):
    """Tipos de notificação"""
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"


# ============================================================================
# SCHEMAS BASE
# ============================================================================

class NotificationBase(BaseModel):
    """Schema base para notificações"""
    type: NotificationType
    title: str = Field(..., max_length=200, description="Título da notificação")
    message: str = Field(..., description="Mensagem completa")
    link: Optional[str] = Field(None, max_length=500, description="Link para recurso relacionado")


class NotificationCreate(NotificationBase):
    """Schema para criar notificação"""
    user_id: int = Field(..., description="ID do destinatário")


class NotificationUpdate(BaseModel):
    """Schema para atualizar notificação"""
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Schema de resposta de notificação"""
    id: int
    user_id: int
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE AÇÕES
# ============================================================================

class MarkAsReadResponse(BaseModel):
    """Schema de resposta ao marcar como lida"""
    id: int
    is_read: bool
    read_at: datetime
    message: str = "Notificação marcada como lida"


class MarkAllAsReadResponse(BaseModel):
    """Schema de resposta ao marcar todas como lidas"""
    count: int = Field(..., description="Número de notificações marcadas")
    message: str = "Todas as notificações foram marcadas como lidas"


class DeleteNotificationResponse(BaseModel):
    """Schema de resposta ao deletar notificação"""
    id: int
    message: str = "Notificação deletada com sucesso"


# ============================================================================
# SCHEMAS DE LISTAGEM
# ============================================================================

class NotificationListResponse(BaseModel):
    """Schema de resposta para lista de notificações"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


class NotificationStats(BaseModel):
    """Schema de estatísticas de notificações"""
    total: int
    unread: int
    by_type: dict = Field(
        ...,
        description="Contagem por tipo",
        example={"info": 5, "warning": 2, "success": 3, "error": 1}
    )


# ============================================================================
# SCHEMAS DE CRIAÇÃO EM MASSA
# ============================================================================

class BulkNotificationCreate(BaseModel):
    """Schema para criar notificações em massa"""
    user_ids: List[int] = Field(..., description="IDs dos destinatários")
    type: NotificationType
    title: str = Field(..., max_length=200)
    message: str
    link: Optional[str] = Field(None, max_length=500)


class BulkNotificationResponse(BaseModel):
    """Schema de resposta para criação em massa"""
    count: int = Field(..., description="Número de notificações criadas")
    notification_ids: List[int]
    message: str = "Notificações criadas com sucesso"
