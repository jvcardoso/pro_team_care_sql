"""
Model de Pendencies (Pendências/Tarefas).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: Pendencies
   Script: 042_Create_Activity_Tracker_Tables.sql
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Pendency(Base):
    """
    Modelo de pendências/tarefas extraídas das atividades.

    Armazena as pendências identificadas pela IA ou pelo usuário,
    com responsável, status e impedimentos.
    """

    __tablename__ = "Pendencies"
    __table_args__ = {"schema": "core", "extend_existing": True}

    PendencyID = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID único da pendência"
    )

    ActivityID = Column(
        Integer,
        ForeignKey("core.Activities.ActivityID", ondelete="CASCADE"),
        nullable=False,
        comment="FK para Activities"
    )

    Description = Column(
        String(1024),
        nullable=False,
        comment="Descrição da pendência"
    )

    Owner = Column(
        String(255),
        nullable=True,
        comment="Responsável pela pendência"
    )

    Status = Column(
        String(50),
        nullable=False,
        default="Pendente",
        comment="Status: Pendente, Cobrado, Resolvido"
    )

    Impediment = Column(
        String(1024),
        nullable=True,
        comment="Descrição do impedimento/bloqueio"
    )

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

    # Relacionamento
    activity = relationship(
        "Activity",
        back_populates="pendencies"
    )

    def __repr__(self):
        return f"<Pendency {self.PendencyID}: {self.Description[:50]}>"
