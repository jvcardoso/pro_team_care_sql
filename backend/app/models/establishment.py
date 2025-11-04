"""
Model de Establishments (Estabelecimentos/Unidades).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: establishments
"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, JSON
from .base import BaseModel


class Establishment(BaseModel):
    """
    Modelo de estabelecimentos/unidades de uma empresa.

    Armazena as filiais, unidades ou postos de atendimento.
    """

    __tablename__ = "establishments"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # Relacionamentos
    person_id = Column(
        BigInteger,
        nullable=False,
        comment="FK para person (dados cadastrais do estabelecimento)"
    )

    company_id = Column(
        BigInteger,
        nullable=False,
        comment="FK para company (empresa proprietária)"
    )

    # Código único
    code = Column(
        String(100),
        nullable=False,
        comment="Código interno único do estabelecimento"
    )

    # Classificação
    type = Column(
        String(40),
        nullable=True,
        comment="Tipo: matriz, filial, unidade, posto"
    )

    category = Column(
        String(60),
        nullable=True,
        comment="Categoria: clinica, hospital, laboratorio, farmacia, etc"
    )

    # Status e flags
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Flag de ativo"
    )

    is_principal = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Flag de unidade matriz/principal"
    )

    # Ordenação
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordem de exibição"
    )

    # Configurações e metadados (String para compatibilidade SQL Server)
    settings = Column(
        String(1000),
        nullable=True,
        comment="Configurações específicas do estabelecimento (JSON string)"
    )

    metadata_ = Column(
        "metadata",  # Nome da coluna no banco
        String(1000),
        nullable=True,
        comment="Metadados adicionais (JSON string)"
    )

    operating_hours = Column(
        String(1000),
        nullable=True,
        comment='Horários de funcionamento: {"monday": "08:00-18:00"} (JSON string)'
    )

    service_areas = Column(
        String(1000),
        nullable=True,
        comment="Áreas de atendimento/serviço (JSON string)"
    )

    # Soft delete
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Data de exclusão lógica (soft delete)"
    )

    def __repr__(self):
        return f"<Establishment {self.code}>"
