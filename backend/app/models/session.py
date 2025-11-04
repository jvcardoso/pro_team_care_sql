"""
Models para sessões de usuário e personificação.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserSession(Base):
    """
    Modelo para rastrear sessões ativas de usuários.
    
    Usado para:
    - Invalidar tokens JWT específicos via JTI
    - Rastrear personificação (impersonate)
    - Gerenciar sessões ativas
    """
    __tablename__ = "user_sessions"
    __table_args__ = {"schema": "core"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("core.users.id", ondelete="CASCADE"), nullable=False, index=True)
    jti = Column(String(255), nullable=False, unique=True, index=True, comment="JWT ID único do token")
    impersonator_user_id = Column(
        BigInteger, 
        ForeignKey("core.users.id"), 
        nullable=True,
        comment="ID do admin que está personificando (NULL se não houver personificação)"
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)

    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id], back_populates="sessions")
    impersonator = relationship("User", foreign_keys=[impersonator_user_id])

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, jti={self.jti[:8]}...)>"
