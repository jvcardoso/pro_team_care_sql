"""
Model de Users (Usuários).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
    Schema: [core]
    Tabela: users
"""
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
from .session import UserSession


class User(BaseModel):
    """
    Modelo de usuários do sistema.

    Contas de usuários que podem autenticar e acessar o sistema.
    """

    __tablename__ = "users"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # Relacionamentos (opcionais)
    person_id = Column(
        BigInteger,
        nullable=True,
        comment="FK opcional para person (dados pessoais)"
    )

    company_id = Column(
        BigInteger,
        nullable=True,
        comment="FK para company"
    )

    establishment_id = Column(
        BigInteger,
        nullable=True,
        comment="FK para establishment padrão"
    )

    invited_by_user_id = Column(
        BigInteger,
        nullable=True,
        comment="Usuário que convidou"
    )

    # Autenticação
    email_address = Column(
        String(510),
        nullable=False,
        unique=True,
        comment="Email único do usuário"
    )

    password = Column(
        String(510),
        nullable=False,
        comment="Hash da senha (bcrypt)"
    )

    # Status e flags
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Flag de ativo"
    )

    is_system_admin = Column(
        Boolean,
        default=False,
        comment="Flag de administrador do sistema"
    )

    # Contexto
    context_type = Column(
        String(510),
        nullable=True,
        comment="Tipo de contexto do usuário"
    )

    # Notificações (JSON)
    notification_settings = Column(
        JSON,
        nullable=True,
        comment="Configurações de notificação"
    )

    # Autenticação de dois fatores
    two_factor_secret = Column(
        String,  # NVARCHAR(MAX)
        nullable=True,
        comment="Segredo para 2FA"
    )

    two_factor_recovery_codes = Column(
        JSON,
        nullable=True,
        comment="Códigos de recuperação 2FA"
    )

    # Timestamps de atividade
    last_login_at = Column(
        DateTime,
        nullable=True,
        comment="Data do último login"
    )

    password_changed_at = Column(
        DateTime,
        nullable=True,
        comment="Data da última troca de senha"
    )

    # Soft delete
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Data de exclusão lógica (soft delete)"
    )

    # Relacionamentos (Fase 2)
    sessions = relationship("UserSession", foreign_keys=[UserSession.user_id], back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email_address}>"
