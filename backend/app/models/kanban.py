"""
Models SQLAlchemy para o sistema Kanban Board.

⚠️ DATABASE FIRST: Tabelas criadas manualmente no SQL Server.
   Schema: [core]
   Script: 046_Create_Kanban_Board_Tables.sql
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CardColumn(Base):
    __tablename__ = "CardColumns"
    __table_args__ = {"schema": "core", "extend_existing": True}

    ColumnID = Column(Integer, primary_key=True, autoincrement=True)
    CompanyID = Column(BigInteger, ForeignKey("core.companies.id"), nullable=False)
    ColumnName = Column(String(100), nullable=False)
    DisplayOrder = Column(Integer, default=0, nullable=False)
    Color = Column(String(20), nullable=True)
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedAt = Column(DateTime, nullable=False)

    # Relacionamento
    cards = relationship("Card", back_populates="column")

class Card(Base):
    __tablename__ = "Cards"
    __table_args__ = {"schema": "core", "extend_existing": True}

    CardID = Column(Integer, primary_key=True, autoincrement=True)
    CompanyID = Column(BigInteger, ForeignKey("core.companies.id"), nullable=False)
    UserID = Column(BigInteger, ForeignKey("core.users.id"), nullable=False)
    ColumnID = Column(Integer, ForeignKey("core.CardColumns.ColumnID"), nullable=False)

    # NOVO CAMPO ADICIONADO
    DisplayOrder = Column(Integer, nullable=True)

    Title = Column(String(255), nullable=False)
    Description = Column(Text, nullable=True)
    OriginalText = Column(Text, nullable=True)
    SubStatus = Column(String(50), nullable=True)
    Priority = Column(String(20), default='Média', nullable=True)
    StartDate = Column(DateTime, nullable=True)
    DueDate = Column(DateTime, nullable=True)
    CompletedDate = Column(DateTime, nullable=True)
    CreatedAt = Column(DateTime, nullable=False)
    IsDeleted = Column(Boolean, default=False, nullable=False)
    DeletedAt = Column(DateTime, nullable=True)
    ExternalCardID = Column(String(50), nullable=True)

    # Relacionamentos
    column = relationship("CardColumn", back_populates="cards")
    movements = relationship("CardMovement", back_populates="card", cascade="all, delete-orphan")
    assignees = relationship("CardAssignee", back_populates="card", cascade="all, delete-orphan")
    tags = relationship("CardTag", back_populates="card", cascade="all, delete-orphan")
    images = relationship("CardImage", back_populates="card", cascade="all, delete-orphan")

class CardMovement(Base):
    __tablename__ = "CardMovements"
    __table_args__ = {"schema": "core", "extend_existing": True}

    MovementID = Column(Integer, primary_key=True, autoincrement=True)
    CardID = Column(Integer, ForeignKey("core.Cards.CardID", ondelete="CASCADE"), nullable=False)
    UserID = Column(BigInteger, ForeignKey("core.users.id"), nullable=False)
    LogDate = Column(DateTime, nullable=False)
    Subject = Column(String(255), nullable=False)
    Description = Column(Text, nullable=True)
    TimeSpent = Column(Integer, nullable=True)
    MovementType = Column(String(50), nullable=True)
    OldColumnID = Column(Integer, nullable=True)
    NewColumnID = Column(Integer, nullable=True)
    OldSubStatus = Column(String(50), nullable=True)
    NewSubStatus = Column(String(50), nullable=True)

    # Relacionamentos
    card = relationship("Card", back_populates="movements")
    images = relationship("MovementImage", back_populates="movement", cascade="all, delete-orphan")

class CardAssignee(Base):
    __tablename__ = "CardAssignees"
    __table_args__ = {"schema": "core", "extend_existing": True}

    AssigneeID = Column(Integer, primary_key=True, autoincrement=True)
    CardID = Column(Integer, ForeignKey("core.Cards.CardID", ondelete="CASCADE"), nullable=False)
    PersonName = Column(String(255), nullable=False)
    PersonID = Column(BigInteger, ForeignKey("core.people.id"), nullable=True)
    AssignedAt = Column(DateTime, nullable=False)

    # Relacionamentos
    card = relationship("Card", back_populates="assignees")

class CardTag(Base):
    __tablename__ = "CardTags"
    __table_args__ = {"schema": "core", "extend_existing": True}

    CardTagID = Column(Integer, primary_key=True, autoincrement=True)
    CardID = Column(Integer, ForeignKey("core.Cards.CardID", ondelete="CASCADE"), nullable=False)
    TagName = Column(String(100), nullable=False)
    TagColor = Column(String(20), nullable=True)
    CreatedAt = Column(DateTime, nullable=False)

    # Relacionamentos
    card = relationship("Card", back_populates="tags")

class CardImage(Base):
    __tablename__ = "CardImages"
    __table_args__ = {"schema": "core", "extend_existing": True}

    CardImageID = Column(Integer, primary_key=True, autoincrement=True)
    CardID = Column(Integer, ForeignKey("core.Cards.CardID", ondelete="CASCADE"), nullable=False)
    ImagePath = Column(String(512), nullable=False)
    ImageType = Column(String(50), nullable=True)
    Description = Column(String(500), nullable=True)
    UploadedBy = Column(BigInteger, ForeignKey("core.users.id"), nullable=False)
    UploadedAt = Column(DateTime, nullable=False)

    # Relacionamentos
    card = relationship("Card", back_populates="images")

class MovementImage(Base):
    __tablename__ = "MovementImages"
    __table_args__ = {"schema": "core", "extend_existing": True}

    MovementImageID = Column(Integer, primary_key=True, autoincrement=True)
    MovementID = Column(Integer, ForeignKey("core.CardMovements.MovementID", ondelete="CASCADE"), nullable=False)
    ImagePath = Column(String(512), nullable=False)
    ImageType = Column(String(50), nullable=True)
    Description = Column(String(500), nullable=True)
    AIAnalysis = Column(String(2000), nullable=True)
    UploadedAt = Column(DateTime, nullable=False)

    # Relacionamentos
    movement = relationship("CardMovement", back_populates="images")