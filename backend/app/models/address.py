"""
Model de Addresses (endereços polimórficos).

Schema: [core]

⚠️ DATABASE FIRST: Este model apenas mapeia a tabela existente.
   A tabela foi criada manualmente no SQL Server.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Address(BaseModel):
    """
    Model de endereços polimórficos.

    Permite associar múltiplos endereços a diferentes entidades (Person, Establishment, etc)
    através do padrão polimórfico addressable_type/addressable_id.
    """
    __tablename__ = "addresses"
    __table_args__ = (
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
    addressable_type = Column(
        String(50),
        nullable=False,
        comment="Tipo da entidade (Person, Establishment, etc)"
    )

    addressable_id = Column(
        BigInteger,
        nullable=False,
        comment="ID da entidade proprietária do endereço"
    )

    # Dados do endereço
    street = Column(
        String(255),
        nullable=False,
        comment="Logradouro (rua, avenida, etc)"
    )

    number = Column(
        String(20),
        nullable=True,
        comment="Número do imóvel"
    )

    details = Column(
        String(100),
        nullable=True,
        comment="Detalhes/complemento"
    )

    neighborhood = Column(
        String(100),
        nullable=False,
        comment="Bairro / distrito"
    )

    city = Column(
        String(100),
        nullable=False,
        comment="Cidade / município"
    )

    state = Column(
        String(2),
        nullable=False,
        comment="UF (estado) - 2 letras"
    )

    zip_code = Column(
        String(10),
        nullable=False,
        comment="CEP (código postal)"
    )

    country = Column(
        String(2),
        nullable=False,
        default="BR",
        comment="Código do país (ISO 3166-1 alpha-2)"
    )

    type = Column(
        String(20),
        nullable=False,
        default="commercial",
        comment="Tipo: residencial, comercial, cobranca, entrega, correspondencia, outro"
    )

    # Flags
    is_principal = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Endereço principal (apenas 1 por entidade)"
    )

    # Geolocalização
    latitude = Column(
        Numeric(10, 8),
        nullable=True,
        comment="Latitude (coordenada geográfica)"
    )

    longitude = Column(
        Numeric(11, 8),
        nullable=True,
        comment="Longitude (coordenada geográfica)"
    )

    google_place_id = Column(
        String(255),
        nullable=True,
        comment="ID do lugar no Google"
    )

    formatted_address = Column(
        Text,
        nullable=True,
        comment="Endereço formatado"
    )

    ibge_city_code = Column(
        Integer,
        nullable=True,
        comment="Código IBGE da cidade"
    )

    access_notes = Column(
        Text,
        nullable=True,
        comment="Notas de acesso"
    )

    is_validated = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Endereço validado"
    )

    last_validated_at = Column(
        DateTime,
        nullable=True,
        comment="Última validação"
    )

    validation_source = Column(
        String(100),
        nullable=True,
        comment="Fonte da validação"
    )

    # Dados extras (JSON)
    api_data = Column(
        Text,
        nullable=True,
        comment="Dados retornados de APIs externas (JSON, ex: ViaCEP)"
    )

    # Soft delete
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Data/hora da exclusão lógica (soft delete)"
    )

    # Relacionamentos
    company = relationship("Company", foreign_keys=[company_id])
