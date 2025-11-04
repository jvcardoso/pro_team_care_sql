"""
Model de Companies (Empresas/Tenants).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: companies
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Company(BaseModel):
    """
    Modelo de empresas clientes (tenants) do sistema SaaS.

    Armazena as empresas clientes (tenants) do sistema SaaS.
    """

    __tablename__ = "companies"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # Relacionamento com Person (PJ principal)
    person_id = Column(
        BigInteger,
        nullable=True,
        unique=True,
        comment="FK para person (PJ principal da empresa)"
    )

    # Configurações e metadados (JSON string)
    settings = Column(
        String(1000),  # Usar String em vez de JSON para compatibilidade
        nullable=True,
        comment="Configurações da empresa (JSON string)"
    )

    company_metadata = Column(
        "metadata",  # Nome da coluna no banco
        String,  # Usar String em vez de JSON para evitar conflitos
        nullable=True,
        comment="Metadados adicionais (JSON string)"
    )

    # Ordenação e exibição
    display_order = Column(
        Integer,
        default=0,
        comment="Ordem de exibição"
    )

    # Status de acesso
    access_status = Column(
        String(40),
        default='pending_contract',
        comment="Status de acesso (pending_contract, contract_signed, active, suspended)"
    )

    # Contrato
    contract_terms_version = Column(
        String(20),
        nullable=True,
        comment="Versão dos termos do contrato"
    )

    contract_accepted_at = Column(
        DateTime,
        nullable=True,
        comment="Data de aceitação do contrato"
    )

    contract_accepted_by = Column(
        String(510),
        nullable=True,
        comment="Quem aceitou o contrato"
    )

    contract_ip_address = Column(
        String(90),
        nullable=True,
        comment="IP de onde foi aceito o contrato"
    )

    # Ativação
    activation_sent_at = Column(
        DateTime,
        nullable=True,
        comment="Data de envio da ativação"
    )

    activation_sent_to = Column(
        String(510),
        nullable=True,
        comment="Para quem foi enviada a ativação"
    )

    activated_at = Column(
        DateTime,
        nullable=True,
        comment="Data de ativação"
    )

    activated_by_user_id = Column(
        BigInteger,
        nullable=True,
        comment="Usuário que ativou"
    )

    # Soft delete
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Data de exclusão lógica (soft delete)"
    )

    # Relacionamentos
    pj_profiles = relationship(
        "PJProfile",
        back_populates="company",
        lazy="select"
    )

    def __repr__(self):
        return f"<Company {self.id}>"
