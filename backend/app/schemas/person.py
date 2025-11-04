"""
Schemas Pydantic para People.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class PersonBase(BaseModel):
    """Campos base de person"""
    company_id: int
    person_type: str = Field(..., pattern="^(PF|PJ)$", description="PF ou PJ")
    name: str = Field(..., min_length=3, max_length=400)
    trade_name: Optional[str] = Field(None, max_length=400)
    tax_id: str = Field(..., min_length=11, max_length=28)
    status: str = Field(default='active', pattern="^(active|inactive|pending|suspended|blocked)$")


class PersonCreate(PersonBase):
    """Schema para criação de person"""
    secondary_tax_id: Optional[str] = None
    birth_date: Optional[date] = None
    incorporation_date: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    tax_regime: Optional[str] = None
    legal_nature: Optional[str] = None
    municipal_registration: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")


class PersonUpdate(BaseModel):
    """Schema para atualização de person"""
    name: Optional[str] = Field(None, min_length=3, max_length=400)
    trade_name: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")


class PersonResponse(PersonBase):
    """Schema de resposta"""
    id: int
    secondary_tax_id: Optional[str] = None
    birth_date: Optional[date] = None
    incorporation_date: Optional[date] = None
    is_active: Optional[bool] = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonListResponse(BaseModel):
    """Schema para lista de people"""
    total: int
    people: list[PersonResponse]
