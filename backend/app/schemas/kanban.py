"""
Schemas Pydantic para o sistema Kanban Board.

Validação de entrada/saída para:
- CardColumns
- Cards
- CardMovements
- CardAssignees
- CardTags
- CardImages
- MovementImages
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# CardColumn Schemas
# ============================================================================

class CardColumnBase(BaseModel):
    """Campos base de CardColumn"""
    ColumnName: str = Field(..., max_length=100)
    DisplayOrder: int = Field(default=0)
    Color: Optional[str] = Field(None, max_length=20)
    IsActive: bool = Field(default=True)


class CardColumnCreate(CardColumnBase):
    """Schema para criação de coluna"""
    CompanyID: int


class CardColumnUpdate(BaseModel):
    """Schema para atualização de coluna"""
    ColumnName: Optional[str] = Field(None, max_length=100)
    DisplayOrder: Optional[int] = None
    Color: Optional[str] = Field(None, max_length=20)
    IsActive: Optional[bool] = None


class CardColumnResponse(CardColumnBase):
    """Schema de resposta de coluna"""
    ColumnID: int
    CompanyID: int
    CreatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Card Schemas
# ============================================================================

class CardBase(BaseModel):
    """Campos base de Card"""
    Title: str = Field(..., max_length=255)
    Description: Optional[str] = None
    SubStatus: Optional[str] = Field(None, max_length=50)
    Priority: str = Field(default='Média', max_length=20)
    StartDate: Optional[datetime] = None
    DueDate: Optional[datetime] = None


class CardCreate(CardBase):
    """Schema para criação de card"""
    ColumnID: int
    OriginalText: Optional[str] = None  # Texto original para IA processar


class CardUpdate(BaseModel):
    """Schema para atualização de card"""
    Title: Optional[str] = Field(None, max_length=255)
    Description: Optional[str] = None
    ColumnID: Optional[int] = None  # Para drag & drop
    SubStatus: Optional[str] = Field(None, max_length=50)
    Priority: Optional[str] = Field(None, max_length=20)
    StartDate: Optional[datetime] = None
    DueDate: Optional[datetime] = None
    CompletedDate: Optional[datetime] = None


class CardResponse(CardBase):
    """Schema de resposta de card"""
    CardID: int
    CompanyID: int
    UserID: int
    ColumnID: int
    ColumnName: Optional[str] = None  # Nome da coluna para exibição
    CreatedAt: datetime
    CompletedDate: Optional[datetime] = None
    IsDeleted: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# CardMovement Schemas
# ============================================================================

class CardMovementBase(BaseModel):
    """Campos base de CardMovement"""
    Subject: str = Field(..., max_length=255)
    Description: Optional[str] = None
    TimeSpent: Optional[int] = Field(None, description="Tempo gasto em minutos")
    MovementType: Optional[str] = Field(None, max_length=50)


class CardMovementCreate(CardMovementBase):
    """Schema para criação de movimento"""
    pass  # CardID vem da URL, não do body


class CardMovementUpdate(BaseModel):
    """Schema para atualização de movimento"""
    Subject: str = Field(..., max_length=255, description="Assunto do movimento (obrigatório)")
    Description: Optional[str] = Field(None, description="Descrição do movimento")
    TimeSpent: Optional[int] = Field(None, description="Tempo gasto em minutos")


class CardMovementResponse(CardMovementBase):
    """Schema de resposta de movimento"""
    MovementID: int
    CardID: int
    UserID: int
    LogDate: datetime
    OldColumnID: Optional[int] = None
    NewColumnID: Optional[int] = None
    OldSubStatus: Optional[str] = None
    NewSubStatus: Optional[str] = None
    images: List["MovementImageResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# CardAssignee Schemas
# ============================================================================

class CardAssigneeBase(BaseModel):
    """Campos base de CardAssignee"""
    PersonName: str = Field(..., max_length=255)
    PersonID: Optional[int] = None


class CardAssigneeCreate(CardAssigneeBase):
    """Schema para criação de assignee"""
    CardID: int


class CardAssigneeResponse(CardAssigneeBase):
    """Schema de resposta de assignee"""
    AssigneeID: int
    CardID: int
    AssignedAt: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# CardTag Schemas
# ============================================================================

class CardTagBase(BaseModel):
    """Campos base de CardTag"""
    TagName: str = Field(..., max_length=100)
    TagColor: Optional[str] = Field(None, max_length=20)


class CardTagCreate(CardTagBase):
    """Schema para criação de tag"""
    CardID: int


class CardTagResponse(CardTagBase):
    """Schema de resposta de tag"""
    CardTagID: int
    CardID: int
    CreatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# CardImage Schemas
# ============================================================================

class CardImageBase(BaseModel):
    """Campos base de CardImage"""
    ImagePath: str = Field(..., max_length=512)
    ImageType: Optional[str] = Field(None, max_length=50)
    Description: Optional[str] = Field(None, max_length=500)


class CardImageCreate(CardImageBase):
    """Schema para criação de imagem do card"""
    CardID: int


class CardImageResponse(CardImageBase):
    """Schema de resposta de imagem do card"""
    CardImageID: int
    CardID: int
    UploadedBy: int
    UploadedAt: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# MovementImage Schemas
# ============================================================================

class MovementImageBase(BaseModel):
    """Campos base de MovementImage"""
    ImagePath: str = Field(..., max_length=512)
    ImageType: Optional[str] = Field(None, max_length=50)
    Description: Optional[str] = Field(None, max_length=500)
    AIAnalysis: Optional[str] = None  # Sem limite - banco usa NVARCHAR(MAX)


class MovementImageCreate(MovementImageBase):
    """Schema para criação de imagem do movimento"""
    MovementID: int


class MovementImageResponse(MovementImageBase):
    """Schema de resposta de imagem do movimento"""
    MovementImageID: int
    MovementID: int
    UploadedAt: datetime
    AIAnalysis: Optional[str] = None  # Sem limite - banco usa NVARCHAR(MAX)

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Schemas Compostos (com relacionamentos)
# ============================================================================

class CardWithDetails(CardResponse):
    """Card com todos os detalhes (assignees, tags, movements, etc.)"""
    assignees: List[CardAssigneeResponse] = Field(default_factory=list)
    tags: List[CardTagResponse] = Field(default_factory=list)
    movements: List[CardMovementResponse] = Field(default_factory=list)
    images: List[CardImageResponse] = Field(default_factory=list)
    total_time_spent: Optional[int] = Field(None, description="Tempo total em minutos")

    model_config = ConfigDict(from_attributes=True)


class CardWithAISuggestions(CardResponse):
    """Card com sugestões da IA"""
    ai_suggestions: Optional[dict] = Field(
        None,
        description="Sugestões da IA (description, assignees, systems, tags, priority, movements)"
    )

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Schemas para Criação com IA
# ============================================================================

class CardCreateWithAI(BaseModel):
    """Schema para criação de card com análise da IA"""
    Title: str = Field(..., max_length=255)
    OriginalText: str = Field(..., description="Texto para IA analisar")
    ColumnID: int = Field(default=1, description="Coluna inicial (default: Backlog)")
    Priority: str = Field(default='Média')
    DueDate: Optional[datetime] = None


class ValidatedCardData(BaseModel):
    """Schema para dados validados pelo usuário após análise da IA"""
    description: Optional[str] = None
    assignees: List[str] = Field(default_factory=list)
    systems: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    priority: str = Field(default='Média')
    sub_status: Optional[str] = None
    due_date: Optional[str] = None  # YYYY-MM-DD
    movements: List[dict] = Field(default_factory=list)  # Lista de movimentos sugeridos


# ============================================================================
# Schemas para Drag & Drop
# ============================================================================

class CardMoveRequest(BaseModel):
    """Schema para mover card entre colunas (drag & drop)"""
    CardID: int
    NewColumnID: int
    NewDisplayOrder: Optional[int] = None  # Para ordenação futura


class BulkCardMoveRequest(BaseModel):
    """Schema para mover múltiplos cards"""
    moves: List[CardMoveRequest]


# ============================================================================
# Analytics / BI Schemas
# ============================================================================

class TimePerStage(BaseModel):
    """Tempo médio por estágio"""
    columnName: str
    avgSeconds: float

    model_config = ConfigDict(from_attributes=True)


class ThroughputHistory(BaseModel):
    """Histórico de throughput por data"""
    date: str  # YYYY-MM-DD
    count: int

    model_config = ConfigDict(from_attributes=True)


class KanbanAnalyticsSummary(BaseModel):
    """Resumo das métricas principais do Kanban"""
    leadTimeAvgSeconds: Optional[float] = None
    cycleTimeAvgSeconds: Optional[float] = None
    throughput: int
    wip: int
    slaCompliance: float

    model_config = ConfigDict(from_attributes=True)


class KanbanAnalyticsResponse(BaseModel):
    """Resposta completa do analytics do Kanban"""
    summary: KanbanAnalyticsSummary
    timePerStage: List[TimePerStage]
    throughputHistory: List[ThroughputHistory]

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ITIL Analytics Schemas (Paginação)
# ============================================================================

class ITILCardResponse(BaseModel):
    """Schema de resposta para card ITIL com classificação"""
    cardId: int
    externalCardId: str
    title: str
    itilCategory: str
    columnName: str
    riskLevel: str
    hasWindow: bool
    hasCAB: bool
    hasBackout: bool
    metSLA: Optional[bool] = None
    daysLate: Optional[int] = None
    completedDate: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ITILCardsPaginatedResponse(BaseModel):
    """Resposta paginada de cards ITIL"""
    items: List[ITILCardResponse]
    total: int
    page: int
    pages: int
    skip: int
    limit: int
    
    model_config = ConfigDict(from_attributes=True)


