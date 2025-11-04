"""
Model de Activities (Atividades).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: Activities
   Script: 042_Create_Activity_Tracker_Tables.sql
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


class Activity(Base):
    """
    Modelo de atividades registradas pelo usuário.

    Armazena registros de atividades do dia a dia que podem ser
    analisadas por IA para extração de dados e geração de pendências.
    """

    __tablename__ = "Activities"
    __table_args__ = {"schema": "core", "extend_existing": True}

    # Renomear id para ActivityID (conforme banco)
    ActivityID = Column(
        "ActivityID",
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID único da atividade"
    )

    # Multi-tenant
    UserID = Column(
        Integer,
        nullable=False,
        comment="ID do usuário que criou a atividade"
    )

    CompanyID = Column(
        Integer,
        nullable=False,
        comment="ID da empresa (tenant)"
    )

    # Dados principais
    Title = Column(
        String(255),
        nullable=False,
        comment="Título/Assunto da atividade"
    )

    Status = Column(
        String(50),
        nullable=False,
        comment="Status: Pendente, Em Andamento, Concluído, Cancelado"
    )

    # Timestamps
    CreationDate = Column(
        DateTime,
        nullable=False,
        comment="Data/hora de criação"
    )

    DueDate = Column(
        DateTime,
        nullable=True,
        comment="Data/hora de prazo"
    )

    # Soft delete
    IsDeleted = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Flag de exclusão lógica"
    )

    DeletedAt = Column(
        DateTime,
        nullable=True,
        comment="Data/hora da exclusão lógica"
    )

    # Relacionamentos
    contents = relationship(
        "ActivityContent",
        back_populates="activity",
        cascade="all, delete-orphan",
        lazy="select"
    )

    entities = relationship(
        "ActivityEntity",
        back_populates="activity",
        cascade="all, delete-orphan",
        lazy="select"
    )

    pendencies = relationship(
        "Pendency",
        back_populates="activity",
        cascade="all, delete-orphan",
        lazy="select"
    )

    images = relationship(
        "ActivityImage",
        back_populates="activity",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Activity {self.ActivityID}: {self.Title}>"
