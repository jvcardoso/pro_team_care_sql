"""
Models para menus dinâmicos.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.core.database import Base


# Tabela de associação N:N entre MenuItem e Permission
menu_item_permissions = Table(
    'menu_item_permissions',
    Base.metadata,
    Column('menu_item_id', BigInteger, ForeignKey('core.menu_items.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', BigInteger, ForeignKey('core.permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
    schema='core'
)


class MenuItem(Base):
    """
    Modelo para itens de menu dinâmicos.
    
    Suporta:
    - Hierarquia (parent_id para submenus)
    - Ordenação customizada (display_order)
    - Integração com permissões
    - Soft delete
    """
    __tablename__ = "menu_items"
    __table_args__ = {"schema": "core"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(
        BigInteger, 
        ForeignKey("core.menu_items.id"), 
        nullable=True,
        index=True,
        comment="ID do menu pai (NULL para menus raiz)"
    )
    name = Column(String(100), nullable=False, unique=True, comment="Identificador único do menu")
    label = Column(String(200), nullable=False, comment="Texto exibido no menu")
    icon = Column(String(50), nullable=True, comment="Nome do ícone (ex: lucide icons)")
    path = Column(String(500), nullable=True, comment="Rota/URL do menu")
    display_order = Column(Integer, nullable=False, default=0, index=True, comment="Ordem de exibição")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Menu ativo/inativo")

    # Relacionamentos
    parent = relationship("MenuItem", remote_side=[id], back_populates="children")
    children = relationship(
        "MenuItem",
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="MenuItem.display_order"
    )
    permissions = relationship(
        "Permission",
        secondary=menu_item_permissions,
        lazy="selectin"
    )

    def __repr__(self):
        return f"<MenuItem(id={self.id}, name={self.name}, label={self.label})>"

    @property
    def has_children(self) -> bool:
        """Verifica se o menu tem submenus"""
        return len(self.children) > 0

    @property
    def is_root(self) -> bool:
        """Verifica se é um menu raiz (sem pai)"""
        return self.parent_id is None
