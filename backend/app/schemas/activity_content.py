"""
Schemas Pydantic para ActivityContents.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActivityContentBase(BaseModel):
    """Campos base de activity content"""
    RawText: Optional[str] = Field(None, description="Texto colado")
    RawImagePath: Optional[str] = Field(None, max_length=512, description="Caminho")
    AIExtractionJSON: Optional[str] = Field(None, description="JSON da IA")
    UserCorrectedJSON: Optional[str] = Field(None, description="JSON validado")


class ActivityContentCreate(ActivityContentBase):
    """Schema para criação de activity content"""
    ActivityID: int


class ActivityContentUpdate(BaseModel):
    """Schema para atualização de activity content"""
    RawText: Optional[str] = None
    RawImagePath: Optional[str] = None
    AIExtractionJSON: Optional[str] = None
    UserCorrectedJSON: Optional[str] = None


class ActivityContentResponse(ActivityContentBase):
    """Schema de resposta de activity content"""
    ContentID: int
    ActivityID: int
    CreatedAt: datetime

    model_config = ConfigDict(from_attributes=True)
