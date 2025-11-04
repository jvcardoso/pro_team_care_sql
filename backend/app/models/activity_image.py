"""
Model para ActivityImages - Armazena múltiplas imagens por atividade.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ActivityImage(Base):
    """Modelo de imagem de atividade"""
    __tablename__ = "ActivityImages"
    __table_args__ = {"schema": "core"}

    ImageID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ActivityID = Column(Integer, ForeignKey("core.Activities.ActivityID"), nullable=False, index=True)
    ImagePath = Column(String(512), nullable=False)
    ImageOrder = Column(Integer, nullable=False, default=0)
    CreationDate = Column(DateTime, nullable=False, default=datetime.utcnow)
    IsDeleted = Column(Boolean, nullable=False, default=False)
    DeletedAt = Column(DateTime, nullable=True)

    # Relacionamento com Activity
    activity = relationship("Activity", back_populates="images")
