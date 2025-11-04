"""
Schemas Pydantic para ActivityEntities.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActivityEntityBase(BaseModel):
    """Campos base de activity entity"""
    EntityType: str = Field(..., max_length=50, description="Tipo entidade")
    EntityValue: str = Field(..., max_length=512, description="Valor da entidade")


class ActivityEntityCreate(ActivityEntityBase):
    """Schema para criação de activity entity"""
    ActivityID: int


class ActivityEntityUpdate(BaseModel):
    """Schema para atualização de activity entity"""
    EntityType: Optional[str] = Field(None, max_length=50)
    EntityValue: Optional[str] = Field(None, max_length=512)


class ActivityEntityResponse(ActivityEntityBase):
    """Schema de resposta de activity entity"""
    EntityID: int
    ActivityID: int
    CreatedAt: datetime

    model_config = ConfigDict(from_attributes=True)
