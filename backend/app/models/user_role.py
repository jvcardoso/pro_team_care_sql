"""
Model de User Roles (Atribuição de Papéis a Usuários).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: user_roles
"""
from sqlalchemy import Column, BigInteger, String, DateTime
from .base import BaseModel


class UserRole(BaseModel):
    """
    Modelo de atribuição de papéis (roles) a usuários.

    Relacionamento many-to-many entre users e roles com contexto.
    """

    __tablename__ = "user_roles"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # Relacionamentos
    user_id = Column(
        BigInteger,
        nullable=False,
        comment="FK para user"
    )

    role_id = Column(
        BigInteger,
        nullable=False,
        comment="FK para role"
    )

    # Contexto onde o papel é válido
    context_type = Column(
        String(510),
        nullable=False,
        comment="Tipo de contexto: system, company, establishment"
    )

    context_id = Column(
        BigInteger,
        nullable=False,
        comment="ID do contexto (company_id ou establishment_id). Use 0 para context_type='system'"
    )

    # Status
    status = Column(
        String(510),
        nullable=False,
        default='active',
        comment="Status: active, inactive, suspended, expired"
    )

    # Auditoria de atribuição
    assigned_by_user_id = Column(
        BigInteger,
        nullable=True,
        comment="Usuário que fez a atribuição"
    )

    assigned_at = Column(
        DateTime,
        nullable=True,
        comment="Data de atribuição"
    )

    expires_at = Column(
        DateTime,
        nullable=True,
        comment="Data de expiração (se aplicável)"
    )

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
