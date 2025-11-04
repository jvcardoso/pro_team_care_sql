"""
Model de ActivityContents (Conteúdo das Atividades).

⚠️ DATABASE FIRST: Tabela criada manualmente no SQL Server.
   Schema: [core]
   Tabela: ActivityContents
   Script: 042_Create_Activity_Tracker_Tables.sql
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ActivityContent(Base):
    """
    Modelo de conteúdo detalhado das atividades.

    Armazena o conteúdo bruto (texto/imagem), a análise da IA
    e os dados validados pelo usuário.
    """

    __tablename__ = "ActivityContents"
    __table_args__ = {"schema": "core", "extend_existing": True}

    ContentID = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID único do conteúdo"
    )

    ActivityID = Column(
        Integer,
        ForeignKey("core.Activities.ActivityID", ondelete="CASCADE"),
        nullable=False,
        comment="FK para Activities"
    )

    # Conteúdo bruto
    RawText = Column(
        Text,
        nullable=True,
        comment="Texto colado pelo usuário"
    )

    RawImagePath = Column(
        String(512),
        nullable=True,
        comment="Caminho da imagem enviada"
    )

    # Análise da IA
    AIExtractionJSON = Column(
        Text,
        nullable=True,
        comment="JSON bruto retornado pela IA"
    )

    UserCorrectedJSON = Column(
        Text,
        nullable=True,
        comment="JSON validado/corrigido pelo usuário"
    )

    # Relacionamento
    activity = relationship(
        "Activity",
        back_populates="contents"
    )

    def __repr__(self):
        return f"<ActivityContent {self.ContentID} for Activity {self.ActivityID}>"
