"""
Model de People (Tabela Raiz de Pessoas).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: people

Tabela raiz que conecta perfis PF e PJ.
Cada pessoa pode ter zero ou um perfil PF e zero ou um perfil PJ.
"""
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Person(BaseModel):
    """
    Modelo da tabela raiz de Pessoas.

    Esta tabela contém apenas dados comuns a PF e PJ.
    Os dados específicos ficam nas tabelas pf_profiles e pj_profiles.
    """

    __tablename__ = "people"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # FK para company
    company_id = Column(
        BigInteger,
        nullable=False,
        comment="Empresa à qual esta pessoa pertence"
    )

    # Dados principais (comuns a PF e PJ)
    name = Column(
        String(400),
        nullable=False,
        comment="Nome completo (PF) ou Razão Social (PJ)"
    )

    # Informações adicionais
    website = Column(
        String,  # NVARCHAR(MAX)
        nullable=True,
        comment="Website"
    )

    description = Column(
        String,  # NVARCHAR(MAX)
        nullable=True,
        comment="Descrição"
    )

    # Status
    status = Column(
        String(40),
        nullable=False,
        default='active',
        comment="Status: active, inactive, pending, suspended, blocked"
    )

    is_active = Column(
        Boolean,
        default=True,
        comment="Flag de ativo"
    )

    # LGPD
    lgpd_consent_version = Column(
        String(20),
        nullable=True,
        comment="Versão do consentimento LGPD"
    )

    lgpd_consent_given_at = Column(
        DateTime,
        nullable=True,
        comment="Data de consentimento LGPD"
    )

    lgpd_data_retention_expires_at = Column(
        DateTime,
        nullable=True,
        comment="Data de expiração dos dados (LGPD)"
    )

    # Metadados (String para compatibilidade SQL Server)
    metadata_ = Column(
        "metadata",  # Nome da coluna no banco
        String(1000),
        nullable=True,
        comment="Metadados adicionais (JSON string)"
    )

    # Relacionamentos com perfis
    pf_profile = relationship(
        "PFProfile",
        back_populates="person",
        uselist=False,
        lazy="joined"
    )

    pj_profile = relationship(
        "PJProfile",
        back_populates="person",
        uselist=False,
        lazy="joined"
    )

    def __repr__(self):
        return f"<Person {self.name} (ID: {self.id})>"

    @property
    def has_pf_profile(self) -> bool:
        """Verifica se a pessoa tem perfil PF"""
        return self.pf_profile is not None

    @property
    def has_pj_profile(self) -> bool:
        """Verifica se a pessoa tem perfil PJ"""
        return self.pj_profile is not None

    @property
    def profiles(self) -> list:
        """Retorna lista de perfis disponíveis"""
        profiles = []
        if self.has_pf_profile:
            profiles.append("PF")
        if self.has_pj_profile:
            profiles.append("PJ")
        return profiles
