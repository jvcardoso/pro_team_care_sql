"""
Model de Roles (Papéis/Permissões).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: roles
"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, JSON
from .base import BaseModel


class Role(BaseModel):
    """
    Modelo de papéis/perfis de acesso do sistema.

    Define permissões e níveis de acesso.
    """

    __tablename__ = "roles"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # Identificação
    name = Column(
        String(250),
        nullable=False,
        unique=True,
        comment="Nome único do papel (ex: admin, medico, enfermeiro)"
    )

    display_name = Column(
        String(400),
        nullable=False,
        comment="Nome de exibição"
    )

    description = Column(
        String,  # NVARCHAR(MAX)
        nullable=True,
        comment="Descrição do papel"
    )

    # Nível de acesso
    level = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Nível hierárquico do papel (0=mais alto)"
    )

    # Contexto
    context_type = Column(
        String(510),
        nullable=False,
        default='establishment',
        comment="Contexto: system, company, establishment"
    )

    # Flags
    is_active = Column(
        Boolean,
        default=True,
        comment="Flag de ativo"
    )

    is_system_role = Column(
        Boolean,
        default=False,
        comment="Flag de papel do sistema (não editável)"
    )

    # Configurações (JSON)
    settings = Column(
        JSON,
        nullable=True,
        comment="Configurações e permissões específicas"
    )

    # Soft delete
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Data/hora de exclusão lógica"
    )

    def __repr__(self):
        return f"<Role {self.name}>"
