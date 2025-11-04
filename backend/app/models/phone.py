"""
Model de Phones (telefones polimórficos).

Schema: [core]

⚠️ DATABASE FIRST: Este model apenas mapeia a tabela existente.
   A tabela foi criada manualmente no SQL Server.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, ForeignKey, Text, Index, Time
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Phone(BaseModel):
    """
    Model de telefones polimórficos.

    Permite associar telefones a diferentes entidades (Person, Establishment, etc)
    através do padrão polimórfico phoneable_type/phoneable_id.
    """
    __tablename__ = "phones"
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
    phoneable_type = Column(
        String(50),
        nullable=False,
        comment="Tipo da entidade (Person, Establishment, etc)"
    )

    phoneable_id = Column(
        BigInteger,
        nullable=False,
        comment="ID da entidade proprietária do telefone"
    )

    # Dados do telefone
    number = Column(
        String(20),
        nullable=False,
        comment="Número do telefone (sem formatação)"
    )

    country_code = Column(
        String(3),
        nullable=False,
        default="55",
        comment="Código do país (55 para Brasil)"
    )

    extension = Column(
        String(10),
        nullable=True,
        comment="Ramal (para telefones comerciais)"
    )

    type = Column(
        String(20),
        nullable=False,
        default="mobile",
        comment="Tipo: landline, mobile, whatsapp, commercial, emergency, fax"
    )

    # Flags
    is_principal = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Telefone principal (apenas 1 por entidade)"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Telefone ativo"
    )

    phone_name = Column(
        String(100),
        nullable=True,
        comment="Nome do telefone/contato"
    )

    is_whatsapp = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Possui WhatsApp neste número"
    )

    whatsapp_formatted = Column(
        String(15),
        nullable=True,
        comment="Número formatado para WhatsApp"
    )

    whatsapp_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="WhatsApp verificado"
    )

    whatsapp_verified_at = Column(
        DateTime,
        nullable=True,
        comment="Data de verificação do WhatsApp"
    )

    whatsapp_business = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="É WhatsApp Business"
    )

    whatsapp_name = Column(
        String(100),
        nullable=True,
        comment="Nome no WhatsApp"
    )

    accepts_whatsapp_marketing = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Aceita marketing via WhatsApp"
    )

    accepts_whatsapp_notifications = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Aceita notificações via WhatsApp"
    )

    whatsapp_preferred_time_start = Column(
        Time,
        nullable=True,
        comment="Horário preferido início para WhatsApp"
    )

    whatsapp_preferred_time_end = Column(
        Time,
        nullable=True,
        comment="Horário preferido fim para WhatsApp"
    )

    carrier = Column(
        String(30),
        nullable=True,
        comment="Nome da operadora"
    )

    line_type = Column(
        String(20),
        nullable=True,
        comment="Tipo da linha: movel, fixo, voip"
    )

    contact_priority = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Prioridade de contato (1 = mais alta)"
    )

    last_contact_attempt = Column(
        DateTime,
        nullable=True,
        comment="Última tentativa de contato"
    )

    last_contact_success = Column(
        DateTime,
        nullable=True,
        comment="Último contato bem-sucedido"
    )

    contact_attempts_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Contador de tentativas de contato"
    )

    can_receive_calls = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Pode receber chamadas"
    )

    can_receive_sms = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Pode receber SMS"
    )

    verified_at = Column(
        DateTime,
        nullable=True,
        comment="Data de verificação"
    )

    verification_method = Column(
        String(50),
        nullable=True,
        comment="Método de verificação"
    )

    # Dados extras (JSON)
    api_data = Column(
        Text,
        nullable=True,
        comment="Dados retornados de APIs externas (JSON)"
    )

    # Audit fields
    created_by_user_id = Column(
        BigInteger,
        nullable=True,
        comment="ID do usuário que criou"
    )

    updated_by_user_id = Column(
        BigInteger,
        nullable=True,
        comment="ID do usuário que atualizou"
    )

    # Soft delete
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Data/hora da exclusão lógica (soft delete)"
    )

    # Relacionamentos
    company = relationship("Company", foreign_keys=[company_id])
