"""
Models para notificações in-app.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Notification(Base):
    """
    Modelo para notificações in-app.
    
    Tipos de notificação:
    - info: Informação geral
    - warning: Aviso/Alerta
    - success: Sucesso
    - error: Erro
    """
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "type IN ('info', 'warning', 'success', 'error')",
            name="CHK_notifications_type"
        ),
        {"schema": "core"}
    )

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        BigInteger, 
        ForeignKey("core.users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True,
        comment="Destinatário da notificação"
    )
    type = Column(String(20), nullable=False, comment="Tipo: info, warning, success, error")
    title = Column(String(200), nullable=False, comment="Título da notificação")
    message = Column(Text, nullable=False, comment="Mensagem completa")
    link = Column(String(500), nullable=True, comment="Link para recurso relacionado (ex: /patients/123)")
    is_read = Column(Boolean, nullable=False, default=False, index=True, comment="Flag de leitura")
    read_at = Column(DateTime, nullable=True, comment="Data/hora de leitura")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    deleted_at = Column(DateTime, nullable=True, comment="Soft delete")

    # Relacionamentos
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"

    def mark_as_read(self):
        """Marca a notificação como lida"""
        self.is_read = True
        self.read_at = datetime.utcnow()
