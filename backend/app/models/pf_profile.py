"""
Model de PF Profile (Perfil Pessoa Física).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: pf_profiles

Perfil específico para dados de Pessoa Física.
"""
from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class PFProfile(BaseModel):
    """
    Modelo para perfil de Pessoa Física.

    Contém dados específicos de PF: CPF, data nascimento, gênero, etc.
    """

    __tablename__ = "pf_profiles"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # FK para person (raiz)
    person_id = Column(
        BigInteger,
        ForeignKey("core.people.id"),
        nullable=False,
        comment="Pessoa raiz"
    )

    # Relacionamento com Person
    person = relationship("Person", back_populates="pf_profile")

    # Documento principal
    tax_id = Column(
        String(22),  # CPF: 11 dígitos + formatação
        nullable=False,
        unique=True,
        comment="CPF (formato: 000.000.000-00)"
    )

    # Dados pessoais
    birth_date = Column(
        Date,
        nullable=True,
        comment="Data de nascimento"
    )

    gender = Column(
        String(40),
        nullable=True,
        comment="Gênero"
    )

    marital_status = Column(
        String(100),
        nullable=True,
        comment="Estado civil"
    )

    occupation = Column(
        String(200),
        nullable=True,
        comment="Profissão/Ocupação"
    )

    def __repr__(self):
        return f"<PFProfile {self.tax_id} - Person {self.person_id}>"