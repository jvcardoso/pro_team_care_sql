"""
Model de ActivityEntities (Entidades das Atividades).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: ActivityEntities
   Script: 042_Create_Activity_Tracker_Tables.sql
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ActivityEntity(Base):
    """
    Modelo de entidades extraídas das atividades.

    Armazena pessoas, sistemas, links e outras entidades
    identificadas no conteúdo da atividade.
    """

    __tablename__ = "ActivityEntities"
    __table_args__ = {"schema": "core", "extend_existing": True}

    EntityID = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID único da entidade"
    )

    ActivityID = Column(
        Integer,
        ForeignKey("core.Activities.ActivityID", ondelete="CASCADE"),
        nullable=False,
        comment="FK para Activities"
    )

    EntityType = Column(
        String(50),
        nullable=False,
        comment="Tipo: Pessoa, Sistema, Link, etc."
    )

    EntityValue = Column(
        String(512),
        nullable=False,
        comment="Valor da entidade"
    )

    # Relacionamento
    activity = relationship(
        "Activity",
        back_populates="entities"
    )

    def __repr__(self):
        return f"<ActivityEntity {self.EntityID}: {self.EntityType}-{self.EntityValue}>"
