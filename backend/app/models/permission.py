"""
Models para Sistema de Permissões (RBAC).

⚠️ DATABASE FIRST: Tabelas criadas manualmente no SQL Server.
   Schema: [core]
   Tabelas: permissions, role_permissions, user_roles
"""
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Permission(BaseModel):
    """
    Modelo de permissões do sistema.
    
    Define ações específicas que podem ser realizadas.
    Formato: resource.action (ex: users.view, companies.create)
    """
    
    __tablename__ = "permissions"
    __table_args__ = {"schema": "core", "extend_existing": True}
    
    # Identificação
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="Nome único da permissão (ex: users.view)"
    )
    
    display_name = Column(
        String(100),
        nullable=False,
        comment="Nome de exibição"
    )
    
    description = Column(
        String(500),
        nullable=True,
        comment="Descrição da permissão"
    )
    
    # Categorização
    resource = Column(
        String(50),
        nullable=False,
        comment="Recurso (ex: users, companies)"
    )
    
    action = Column(
        String(50),
        nullable=False,
        comment="Ação (ex: view, create, update, delete)"
    )
    
    # Flags
    is_active = Column(
        Boolean,
        default=True,
        comment="Flag de ativo"
    )
    
    # Relacionamentos (Fase 2)
    # menu_items será definido via secondary no MenuItem
    
    def __repr__(self):
        return f"<Permission {self.name}>"


class RolePermission(BaseModel):
    """
    Modelo de relacionamento N:N entre Roles e Permissions.
    
    Define quais permissões cada role possui.
    """
    
    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "core", "extend_existing": True}
    
    # Relacionamentos
    role_id = Column(
        BigInteger,
        ForeignKey("core.roles.id"),
        nullable=False,
        comment="ID do role"
    )
    
    permission_id = Column(
        BigInteger,
        ForeignKey("core.permissions.id"),
        nullable=False,
        comment="ID da permissão"
    )
    
    # Relationships
    role = relationship("Role", backref="role_permissions")
    permission = relationship("Permission", backref="role_permissions")
    
    def __repr__(self):
        return f"<RolePermission role_id={self.role_id} permission_id={self.permission_id}>"


class UserRole(BaseModel):
    """
    Modelo de relacionamento entre Users e Roles.
    
    Define quais roles cada usuário possui, com contexto e expiração.
    """
    
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "core", "extend_existing": True}
    
    # Relacionamentos
    user_id = Column(
        BigInteger,
        ForeignKey("core.users.id"),
        nullable=False,
        comment="ID do usuário"
    )
    
    role_id = Column(
        BigInteger,
        ForeignKey("core.roles.id"),
        nullable=False,
        comment="ID do role"
    )
    
    # Contexto
    context_type = Column(
        String(20),
        nullable=False,
        default='establishment',
        comment="Tipo de contexto: system, company, establishment"
    )
    
    context_id = Column(
        BigInteger,
        nullable=True,
        comment="ID do contexto (company_id ou establishment_id)"
    )
    
    # Status
    status = Column(
        String(20),
        nullable=False,
        default='active',
        comment="Status: active, inactive, expired, revoked"
    )
    
    # Expiração
    expires_at = Column(
        DateTime,
        nullable=True,
        comment="Data de expiração do role (opcional)"
    )
    
    # Auditoria
    assigned_by_user_id = Column(
        BigInteger,
        ForeignKey("core.users.id"),
        nullable=True,
        comment="ID do usuário que atribuiu o role"
    )
    
    assigned_at = Column(
        DateTime,
        nullable=False,
        server_default="GETDATE()",
        comment="Data de atribuição"
    )
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="user_roles")
    role = relationship("Role", backref="user_roles")
    assigned_by = relationship("User", foreign_keys=[assigned_by_user_id])
    
    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
