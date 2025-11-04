"""
Model de PJ Profile (Perfil Pessoa Jurídica).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: pj_profiles

Perfil específico para dados de Pessoa Jurídica.
"""
from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class PJProfile(BaseModel):
    """
    Modelo para perfil de Pessoa Jurídica.

    Contém dados específicos de PJ: CNPJ, razão social, regime tributário, etc.
    """

    __tablename__ = "pj_profiles"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # FK para person (raiz)
    person_id = Column(
        BigInteger,
        ForeignKey("core.people.id"),
        nullable=False,
        comment="Pessoa raiz"
    )

    # FK para company (obrigatório para PJ)
    company_id = Column(
        BigInteger,
        ForeignKey("core.companies.id"),
        nullable=False,
        comment="Empresa à qual esta PJ pertence"
    )

    # Relacionamentos
    person = relationship("Person", back_populates="pj_profile")
    company = relationship("Company", back_populates="pj_profiles")

    # Documento principal
    tax_id = Column(
        String(28),  # CNPJ: 14 dígitos + formatação
        nullable=False,
        comment="CNPJ (formato: 00.000.000/0000-00)"
    )

    # Dados empresariais
    trade_name = Column(
        String(400),
        nullable=True,
        comment="Nome Fantasia"
    )

    incorporation_date = Column(
        Date,
        nullable=True,
        comment="Data de constituição"
    )

    tax_regime = Column(
        String(100),
        nullable=True,
        comment="Regime tributário (Simples, Lucro Real, etc)"
    )

    legal_nature = Column(
        String(200),
        nullable=True,
        comment="Natureza jurídica"
    )

    municipal_registration = Column(
        String(40),
        nullable=True,
        comment="Inscrição municipal"
    )

    # Constraint de unicidade: uma empresa não pode ter duas PJ com mesmo CNPJ
    __table_args__ = (
        {"schema": "core", "extend_existing": True},
    )

    def __repr__(self):
        return f"<PJProfile {self.tax_id} - Person {self.person_id}>"