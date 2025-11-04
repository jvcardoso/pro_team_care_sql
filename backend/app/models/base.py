"""
Model base com campos comuns (timestamps, soft delete).

⚠️ DATABASE FIRST: Este model não cria tabelas automaticamente.
   As tabelas foram criadas manualmente no SQL Server.
   Schema: [core]
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, DateTime
from app.core.database import Base


class BaseModel(Base):
    """
    Model abstrato com campos padrão para todas as tabelas.

    Inclui:
    - id (auto-increment)
    - created_at (timestamp de criação)
    - updated_at (timestamp de atualização)
    - deleted_at (soft delete) - quando aplicável
    """
    __abstract__ = True

    id = Column(
        BigInteger,
        primary_key=True,
        comment="ID único auto-incrementado"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        comment="Data/hora de criação do registro"
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        comment="Data/hora da última atualização"
    )

    @property
    def is_deleted(self) -> bool:
        """Verifica se registro foi deletado (soft delete)"""
        return hasattr(self, 'deleted_at') and self.deleted_at is not None
