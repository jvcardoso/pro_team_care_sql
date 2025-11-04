"""
Model de Emails (emails polimórficos).

Schema: [core]

⚠️ DATABASE FIRST: Este model apenas mapeia a tabela existente.
   A tabela foi criada manualmente no SQL Server.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Email(BaseModel):
    """
    Model de emails polimórficos.

    Permite associar múltiplos emails a diferentes entidades (Person, Establishment, etc)
    através do padrão polimórfico emailable_type/emailable_id.
    """
    __tablename__ = "emails"
    __table_args__ = (
        # Índice único para is_principal (apenas 1 email principal por entidade)
        Index(
            'UQ_emails_emailable_principal',
            'emailable_type', 'emailable_id',
            unique=True,
            mssql_where="is_principal = 1 AND deleted_at IS NULL"
        ),
        # Índice único para email_address (não pode duplicar)
        Index(
            'UQ_emails_address',
            'email_address',
            unique=True,
            mssql_where="deleted_at IS NULL"
        ),
        # Índice de busca por entidade
        Index(
            'IX_emails_emailable',
            'emailable_type', 'emailable_id', 'deleted_at'
        ),
        # Índice de busca por company
        Index(
            'IX_emails_company_deleted',
            'company_id', 'deleted_at'
        ),
        {"schema": "core"}
    )

    # FK para company
    company_id = Column(
        BigInteger,
        ForeignKey("core.companies.id"),
        nullable=False,
        comment="ID da empresa (multi-tenant)"
    )

    # Campos polimórficos
    emailable_type = Column(
        String(50),
        nullable=False,
        comment="Tipo da entidade (Person, Establishment, etc)"
    )

    emailable_id = Column(
        BigInteger,
        nullable=False,
        comment="ID da entidade proprietária do email"
    )

    # Dados do email
    email_address = Column(
        String(255),
        nullable=False,
        comment="Endereço de email (único no sistema)"
    )

    type = Column(
        String(20),
        nullable=False,
        default="pessoal",
        comment="Tipo: pessoal, profissional, comercial, financeiro, suporte, outro"
    )

    # Flags
    is_principal = Column(
        Boolean,
        nullable=True,
        default=False,
        comment="Email principal (apenas 1 por entidade)"
    )

    is_active = Column(
        Boolean,
        nullable=True,
        default=True,
        comment="Email ativo"
    )

    verified_at = Column(
        DateTime,
        nullable=True,
        comment="Data/hora da verificação do email"
    )

    # Soft delete
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Data/hora da exclusão lógica (soft delete)"
    )

    # Relacionamentos
    company = relationship("Company", foreign_keys=[company_id])
